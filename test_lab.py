"""Offline regression tests for retry, citation correctness and failed-run output handling."""
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import httpx
import tools
from check_citations import check
from research import save_outputs, slugify, summarize
from agents import REPORT_PATH, SOURCES_PATH


class LabTests(unittest.TestCase):
    def test_retry_respects_header_and_stops_without_final_sleep(self):
        fn = Mock(side_effect=[tools.RetryableError('busy', 8), tools.RetryableError('busy', 100), tools.RetryableError('busy')])
        with patch('tools.time.sleep') as sleep:
            with self.assertRaises(tools.RetryableError):
                tools.with_retry(fn, attempts=3, cap=20)
            self.assertEqual([c.args[0] for c in sleep.call_args_list], [8, 20])
        with patch('tools.time.sleep') as sleep:
            with self.assertRaises(ValueError):
                tools.with_retry(Mock(side_effect=ValueError('bad code')))
            sleep.assert_not_called()

    def test_backoff_jitter_and_success(self):
        with patch('tools.random.uniform', return_value=.5), patch('tools.time.sleep') as sleep:
            value = tools.with_retry(Mock(side_effect=[tools.RetryableError('busy'), tools.RetryableError('busy'), 'ok']))
            self.assertEqual(value, 'ok')
            self.assertEqual([c.args[0] for c in sleep.call_args_list], [1.5, 2.5])

    def test_transport_and_http_status_are_retryable(self):
        with patch('tools.httpx.request', side_effect=httpx.ConnectError('offline')):
            with self.assertRaises(tools.RetryableError):
                tools._request('GET', 'https://example.org')
        r = httpx.Response(429, headers={'Retry-After':'7'}, request=httpx.Request('GET','https://example.org'))
        with patch('tools.httpx.request', return_value=r):
            with self.assertRaises(tools.RetryableError) as error:
                tools._request('GET','https://example.org')
            self.assertEqual(error.exception.retry_after, 7)

    def test_exa_http_200_limit_retries_and_redacts(self):
        r = Mock(text=json.dumps({'jsonrpc':'2.0','id':1,'result':{'_meta':{'rateLimited':True},'content':[]}}))
        r.json.return_value = json.loads(r.text)
        with patch('tools._request', return_value=r), patch('tools.time.sleep') as sleep:
            result = tools.web_search.invoke({'query':'research'})
            self.assertTrue(result.startswith('ERROR:'))
            self.assertEqual(sleep.call_count, 6)
        with patch.dict('os.environ', {'EXA_API_KEY':'private-key-for-test'}):
            self.assertNotIn('private-key-for-test', tools.safe_error(ValueError('https://example.org?exaApiKey=private-key-for-test')))

    def test_arxiv_normalizes_and_sanitizes(self):
        xml = '<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>http://arxiv.org/abs/2501.00001v2</id><title> A\n B </title><summary>Some evidence</summary><published>2025-01-01T00:00:00Z</published></entry></feed>'
        with patch('tools._request', return_value=SimpleNamespace(text=xml)) as request, patch('tools.time.sleep'):
            records = json.loads(tools.arxiv_search.invoke({'query':'all:"world" AND model'}))
            self.assertEqual(records[0]['url'], 'https://arxiv.org/abs/2501.00001')
            self.assertEqual(records[0]['title'], 'A B')
            self.assertEqual(request.call_args.kwargs['params']['search_query'], 'all:world AND all:model')
        with patch('tools._request') as request:
            self.assertEqual(tools.arxiv_search.invoke({'query':'" :'}), 'NO RESULTS')
            request.assert_not_called()

    def test_citations_groups_code_links_and_bad_references(self):
        sources = [{'n':1,'url':'https://example.org/a'},{'n':2,'url':'https://example.org/b'}]
        refs = '\n## References\n[1] A. https://example.org/a\n[2] B. https://example.org/b\n'
        self.assertEqual(check('Evidence [1-2]. `fake [9]` [8](https://example.org)\n```\n[7]\n```'+refs,sources), [])
        self.assertTrue(check('Evidence [1].'+refs, sources))
        self.assertTrue(check('Evidence [1,2].'+refs.replace('https://example.org/b','https://example.org/wrong'),sources))
        self.assertTrue(check('Evidence [1,2].'+refs+'[1] duplicate https://example.org/a\n',sources))
        self.assertTrue(check('Evidence [1,2].'+refs.replace('A.','A. https://other.org'),sources))
        self.assertTrue(check('Evidence [1].\n## References\n[1] A https://example.org/a', [{'n':True,'url':'https://example.org/a'}]))

    def test_failed_outputs_write_nothing(self):
        backend = Mock()
        backend.download_files.return_value = [SimpleNamespace(path=REPORT_PATH,content=b'body'), SimpleNamespace(path=SOURCES_PATH,content=b'invalid-json')]
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(RuntimeError):
                save_outputs(backend,'topic',[],1,'test',Path(folder))
            self.assertEqual(list(Path(folder).iterdir()), [])

    def test_successful_outputs_preserve_downloaded_bytes(self):
        from agents import NOTES_DIR
        sources = [{'n':1,'id':'2501.00001','url':'https://arxiv.org/abs/2501.00001','title':'A','date':'2025-01-01','source':'arxiv'},
                   {'n':2,'id':'2501.00002','url':'https://huggingface.co/papers/2501.00002','title':'B','date':'2025-01-02','source':'hf-search'},
                   {'n':3,'id':'c','url':'https://example.org/c','title':'C','date':'','source':'web'}]
        report = b'# Survey\nEvidence [1][2][3].\n\n## References\n[1] A https://arxiv.org/abs/2501.00001\n[2] B https://huggingface.co/papers/2501.00002\n[3] C https://example.org/c\n'
        raw_sources = json.dumps(sources, indent=4).encode()
        backend = Mock()
        backend.download_files.return_value = [SimpleNamespace(path=REPORT_PATH,content=report),
            SimpleNamespace(path=SOURCES_PATH,content=raw_sources),SimpleNamespace(path=NOTES_DIR+'/citation-audit.md',content=b'SUPPORTED')]
        messages = [SimpleNamespace(tool_calls=[{'name':'task'}]*3,usage_metadata={})]
        with tempfile.TemporaryDirectory() as folder:
            path = save_outputs(backend,'topic',messages,1,'test',Path(folder))
            self.assertEqual(path.read_bytes(),report)
            self.assertEqual(path.with_suffix('.sources.json').read_bytes(),raw_sources)
            self.assertEqual(json.loads(path.with_suffix('.meta.json').read_text())['n_sources'],3)

    def test_provenance_rejects_wrong_tool_and_date(self):
        source = {'n':1,'id':'2501.00001','url':'https://huggingface.co/papers/2501.00001',
                  'date':'2025-01-01','source':'hf-search'}
        report = '## TL;DR\nEvidence [1].\n## Background\nEvidence [1].\n## Trends and open problems\nEvidence [1].\n## References\n[1] A https://huggingface.co/papers/2501.00001\n'
        provenance = [{'source':'hf-daily','url':source['url'],'id':source['id'],'published':'2025-01-02'}]
        problems = check(report,[source],provenance)
        self.assertTrue(any('not returned' in p for p in problems))
        source['source'] = 'hf-daily'
        problems = check(report,[source],provenance)
        self.assertTrue(any('date must match' in p for p in problems))

    def test_short_two_theme_draft_fails_submission_gate(self):
        sources = [{'n':1,'source':'arxiv','id':'2204.03458','url':'https://arxiv.org/abs/2204.03458'},
                   {'n':2,'source':'hf-search','id':'2310.19512','url':'https://huggingface.co/papers/2310.19512'},
                   {'n':3,'source':'web','id':'vbench','url':'https://vbench.github.io/'}]
        draft = ('## TL;DR\nFindings [1][2][3].\n## Background\nDefinition.\n'
                 '## Current Approaches\nModels.\n## Evaluation\nMetrics.\n'
                 '## Trends and open problems\nLimitations.\n## References\n'+
                 ''.join(f"[{s['n']}] Source {s['url']}\n" for s in sources))
        self.assertEqual(check(draft,sources), [])  # Citation consistency alone is insufficient.
        problems = check(draft,sources,sources)
        self.assertTrue(any('3-6' in problem for problem in problems))
        self.assertTrue(any('too short' in problem for problem in problems))

    def test_token_window_waits_for_expiry(self):
        from openai_adapter import TokenWindow
        window = TokenWindow()
        with patch('openai_adapter.time.monotonic', side_effect=[0,0,61]), patch('openai_adapter.time.sleep') as sleep:
            window.reserve(100,150)
            window.reserve(100,150)
            self.assertEqual(sleep.call_count,1)
            self.assertLessEqual(sum(n for _,n in window.events),150)

    def test_llm_quota_cooldown_recovers(self):
        import openai
        from openai_adapter import OpenAICompatibleChat
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage
        model = OpenAICompatibleChat(model='test',api_key='test',disable_streaming=True)
        response = httpx.Response(429, request=httpx.Request('POST','https://example.org'))
        error = openai.RateLimitError('Please retry in 7s.',response=response,body={})
        with patch.dict('os.environ',{'LAB_INPUT_TOKENS_PER_MINUTE':'0'}), patch.object(ChatOpenAI,'_generate',side_effect=[error,'ok']), patch('openai_adapter.time.sleep') as sleep:
            self.assertEqual(model._generate([HumanMessage('test')]),'ok')
            sleep.assert_called_once_with(9)

    def test_normalizer_uses_real_discoveries_not_citation_indices(self):
        from normalize_sources import normalize
        sources = [{'n':14,'id':'2501.00001v2','url':'https://arxiv.org/html/2501.00001v2','source':'hf-search','date':'wrong'},
                   {'n':4,'id':'unknown','url':'https://example.org/imagined','source':'web','date':'wrong'}]
        provenance = [{'id':'2501.00001','url':'https://huggingface.co/papers/2501.00001','source':'hf-search','published':'2025-01-02','title':'Actual paper'}]
        fixed, problems = normalize(sources,provenance)
        self.assertEqual(fixed[0]['n'],14)
        self.assertEqual(fixed[0]['url'],provenance[0]['url'])
        self.assertEqual(fixed[0]['date'],'2025-01-02')
        self.assertEqual(fixed[1],sources[1])
        self.assertEqual(len(problems),1)

    def test_placeholder_fetch_title_does_not_erase_known_metadata(self):
        from normalize_sources import normalize
        url = 'https://example.org/paper'
        text = '# N/A\nURL: '+url+'\n\nRetrieved article content.'
        payload = {'id':1,'result':{'content':[{'type':'text','text':text}]}}
        response = SimpleNamespace(text='',json=lambda:payload)
        with patch.object(tools,'_provenance',{}), patch('tools._request',return_value=response):
            tools.web_fetch.invoke({'url':url})
            self.assertNotIn('title',tools.source_provenance()[0])
        fixed, errors = normalize([{'n':1,'source':'web','url':url,'title':'Actual paper'}],
                                  [{'source':'web','url':url,'title':'N/A'}])
        self.assertEqual(fixed[0]['title'],'Actual paper')
        self.assertEqual(errors,[])
        caption = 'Figure caption explaining the plotted reasoning trees. '*25
        fixed, errors = normalize([{'n':1,'source':'web','url':url,'title':'Actual paper'}],
                                  [{'source':'web','url':url,'title':caption}])
        self.assertEqual(fixed[0]['title'],'Actual paper')
        self.assertEqual(errors,[])
        _, errors = normalize([{'n':1,'source':'web','url':url,'title':caption}],
                              [{'source':'web','url':url,'title':caption}])
        self.assertTrue(any('bibliographic title' in error for error in errors))

    def test_role_models_restore_lead_configuration(self):
        import agents
        seen = []
        def factory():
            import os
            seen.append(os.environ['LAB_MODEL'])
            return seen[-1]
        with patch.dict('os.environ',{'LAB_MODEL':'lead','LAB_RESEARCH_MODEL':'research','LAB_CHECKER_MODEL':'checker'}), \
             patch('agents.make_model',side_effect=factory), patch('agents.preserve_tool_extensions',side_effect=lambda value:value):
            configured = agents.build_subagents()
            self.assertEqual([a['model'] for a in configured],['research','checker'])
            self.assertEqual(__import__('os').environ['LAB_MODEL'],'lead')
            with patch('agents.make_model',side_effect=RuntimeError('bad model')):
                with self.assertRaises(RuntimeError): agents._role_model('LAB_RESEARCH_MODEL')
                self.assertEqual(__import__('os').environ['LAB_MODEL'],'lead')

    def test_revision_metadata_is_not_replaced_by_repair_counter(self):
        import hashlib
        import research
        from contextlib import nullcontext
        with tempfile.TemporaryDirectory() as folder:
            draft = Path(folder)/'draft.md'
            original = b'Existing system draft'
            draft.write_bytes(original)
            records = [{'source':'web','url':'https://example.org/retrieved'}]
            draft.with_suffix('.sources.json').write_text(json.dumps(records))
            draft.with_suffix('.provenance.json').write_text(json.dumps(records))
            backend = Mock()
            backend.execute.return_value = SimpleNamespace(exit_code=0,output='OK')
            agent = Mock()
            agent.stream.return_value = iter([{'messages':[]}])
            with patch('research.make_model'), patch('research.open_sandbox',return_value=nullcontext(backend)), \
                 patch('research.upload'), patch('research.restore_provenance'), \
                 patch('research.build_lead_agent',return_value=agent), \
                 patch('research.recover_daily_candidates',return_value=None), \
                 patch('research.source_provenance',return_value=records), patch('research.save_outputs',return_value='test-report') as save:
                self.assertEqual(research.main('topic','Check the draft',draft),0)
                info = save.call_args.kwargs['revision']
                self.assertEqual(info['draft_sha256'],hashlib.sha256(original).hexdigest())
                self.assertEqual(info['archived_discoveries'],1)

    def test_revision_rejects_sources_missing_from_archive(self):
        import research
        from contextlib import nullcontext
        with tempfile.TemporaryDirectory() as folder:
            draft = Path(folder)/'draft.md'
            draft.write_bytes(b'Original draft stays unchanged')
            draft.with_suffix('.sources.json').write_text(json.dumps([{'source':'web','url':'https://example.org/unretrieved'}]))
            draft.with_suffix('.provenance.json').write_text(json.dumps([{'source':'web','url':'https://example.org/retrieved'}]))
            backend = Mock()
            backend.execute.return_value = SimpleNamespace(exit_code=0,output='OK')
            with patch('research.make_model'), patch('research.open_sandbox',return_value=nullcontext(backend)), \
                 patch('research.upload'), patch('research.restore_provenance'), patch('research.save_outputs') as save:
                self.assertEqual(research.main('topic','Check the draft',draft),1)
                save.assert_not_called()
                self.assertEqual(draft.read_bytes(),b'Original draft stays unchanged')

    def test_revision_keeps_original_discovery_when_fetching_again(self):
        from normalize_sources import normalize
        original = {'source':'arxiv','id':'2405.12399','url':'https://arxiv.org/abs/2405.12399',
                    'published':'2024-05-20','title':'Diffusion for World Modeling'}
        source = dict(original, n=1, date=original['published'])
        with patch.object(tools,'_provenance',{}):
            tools.restore_provenance([original])
            tools._remember('web',[{'url':original['url']}])
            archive = tools.source_provenance()
            self.assertEqual({r['source'] for r in archive},{'arxiv','web'})
            fixed, problems = normalize([source],archive)
            self.assertEqual(fixed[0]['source'],'arxiv')
            self.assertEqual(problems,[])
            with self.assertRaises(ValueError):
                tools.restore_provenance([{'source':'imagined','url':'https://example.org'}])

    def test_wrong_paper_title_requires_claim_review(self):
        from normalize_sources import normalize
        source = {'n':3,'url':'https://arxiv.org/abs/2212.03866','source':'web',
                  'title':'Align Your Latents: High-Resolution Video Synthesis With Latent Diffusion Models'}
        actual = {'url':source['url'],'source':'web',
                  'title':'Learning Action-Effect Dynamics for Hypothetical Vision-Language Reasoning Task'}
        fixed, errors = normalize([source],[actual])
        self.assertEqual(fixed[0]['title'], actual['title'])
        self.assertTrue(any('EVERY body claim' in error for error in errors))
        self.assertEqual(normalize(fixed,[actual])[1], [])
        short = dict(source,title='The Building Block Economy')
        extended = dict(actual,title='The Building Block Economy: How Agent-Native Tools Are Reshaping What It Means to Build Software')
        fixed, errors = normalize([short],[extended])
        self.assertEqual(fixed[0]['title'],extended['title'])
        self.assertEqual(errors,[])

    def test_family_recovery_does_not_count_unproven_labels(self):
        from research import recover_daily_candidates
        sources = [{'n':1,'id':'2501.00001','source':'hf-search','url':'https://huggingface.co/papers/2501.00001'},
                   {'n':2,'id':'web','source':'web','url':'https://example.org/real'},
                   {'n':3,'id':'2501.99999','source':'arxiv','url':'https://arxiv.org/abs/2501.99999'}]
        provenance=[dict(s) for s in sources[:2]]
        backend=Mock()
        backend.download_files.return_value=[SimpleNamespace(path=SOURCES_PATH,content=json.dumps(sources).encode())]
        daily=[{'id':'2601.00001','url':'https://huggingface.co/papers/2601.00001','title':'LLM agents and tools','summary':'LLM agents select tools','published':'2026-01-01'}]
        with patch('research.source_provenance',return_value=provenance), patch('research.hf_daily_papers',new=Mock(invoke=Mock(return_value=json.dumps(daily)))) as fetch:
            path=recover_daily_candidates(backend,'survey about LLM agents and tool use')
            self.assertTrue(path.endswith('source-recovery-daily.md'))
            fetch.invoke.assert_called_once()
            self.assertIn(b'hf-daily',backend.upload_files.call_args.args[0][0][1])

    def test_host_gate_restores_tampered_sandbox_helpers(self):
        import research
        from contextlib import nullcontext
        files = {}
        trusted = {research.VALIDATOR_PATH: research.VALIDATOR_SOURCE.read_bytes(),
                   research.FINALIZER_PATH: research.FINALIZER_SOURCE.read_bytes(),
                   research.NORMALIZER_PATH: (research.ROOT/'normalize_sources.py').read_bytes()}
        backend = Mock()
        def execute(command):
            if command.startswith('python3 '):
                path = command.split()[1]
                self.assertEqual(files[path], trusted[path], 'untrusted agent helper reached host gate')
            return SimpleNamespace(exit_code=0,output='OK')
        backend.execute.side_effect = execute
        def stream(*args, **kwargs):
            for path in trusted:
                files[path] = b"print('fake OK')"
            yield {'messages': []}
        agent = Mock()
        agent.stream.side_effect = stream
        with patch('research.make_model'), patch('research.open_sandbox',return_value=nullcontext(backend)), \
             patch('research.build_lead_agent',return_value=agent), \
             patch('research.upload',side_effect=lambda backend,values: files.update(values)), \
             patch('research.recover_daily_candidates',return_value=None), \
             patch('research.source_provenance',return_value=[]), patch('research.save_outputs',return_value='test-report'):
            self.assertEqual(research.main('test topic'),0)

    def test_provider_tool_metadata_round_trip(self):
        from openai_adapter import OpenAICompatibleChat
        from langchain_core.messages import HumanMessage, ToolMessage
        model = OpenAICompatibleChat(model='test', api_key='test', disable_streaming=True)
        raw = {'id':'response', 'model':'test', 'choices':[{'index':0,'finish_reason':'tool_calls','message':{
            'role':'assistant','content':None,'tool_calls':[{'id':'call-1','type':'function',
                'function':{'name':'check','arguments':'{}'},'extra_content':{'google':{'thought_signature':'opaque-test-signature'}}}]}}]}
        result = model._create_chat_result(raw)
        message = result.generations[0].message
        payload = model._get_request_payload([HumanMessage('check'),message,ToolMessage('ok',tool_call_id='call-1')])
        self.assertEqual(payload['messages'][1]['tool_calls'][0]['extra_content'], {'google':{'thought_signature':'opaque-test-signature'}})

    def test_safe_slug_and_real_message_counts(self):
        self.assertEqual(slugify('../../x'), 'x')
        self.assertEqual(slugify(''), 'topic')
        self.assertLessEqual(len(slugify('a'*100)), 60)
        messages = [SimpleNamespace(tool_calls=[{'name':'task'},{'name':'execute'}],usage_metadata={'input_tokens':12,'output_tokens':4})]
        meta = summarize(messages, 1.234, 'test')
        self.assertEqual(meta['subagent_calls'],1)
        self.assertEqual(meta['tokens'],{'input':12,'output':4})


class VertexAuthTests(unittest.TestCase):
    def test_url_citations_bind_to_source_identity_not_array_order(self):
        from normalize_sources import compile_url_citations
        sources=[{'n':1,'url':'https://example.org/other'},{'n':12,'url':'https://example.org/ppo'}]
        result, errors=compile_url_citations('PPO claim [@https://example.org/ppo].',sources)
        self.assertEqual(result,'PPO claim [12].')
        self.assertEqual(errors,[])
        result, errors=compile_url_citations('Unknown [@https://example.org/missing]',sources)
        self.assertTrue(errors)
        self.assertIn('[@https://example.org/missing]',result)
        report='Claim [12] and uncompiled [@https://example.org/missing].\n## References\n[12] PPO. https://example.org/ppo\n'
        self.assertTrue(any('uncompiled URL' in error for error in check(report,[sources[1]])))

    def test_provenance_gate_enforces_requested_survey_length(self):
        sources=[{'n':1,'url':'https://example.org/one','source':'web'}]
        report='# Survey\n## TL;DR\n- Claim [1]\n## Background\n'+'evidence '*1810+'\n## Theme 1\n## Theme 2\n## Theme 3\n## Trends and open problems\n## References\n[1] Source. https://example.org/one\n'
        errors=check(report,sources,[{'source':'web','url':'https://example.org/one'}])
        self.assertTrue(any('exceeds the requested length' in error for error in errors))

    def test_token_estimate_excludes_opaque_signature_without_mutating_request(self):
        from openai_adapter import estimate_input_tokens
        signature = 'opaque' * 10000
        payload = {'messages':[{'content':'retrieved evidence', 'extra_content':
                   {'google':{'thought_signature':signature}}}]}
        self.assertLess(estimate_input_tokens(payload), 100)
        self.assertEqual(payload['messages'][0]['extra_content']['google']['thought_signature'], signature)

    def test_oauth_callback_reuses_token_and_refreshes_when_expired(self):
        import vertex_auth
        credential = Mock(valid=False, token='test-token')
        credential.refresh.side_effect = lambda request: setattr(credential, 'valid', True)
        with patch('google.oauth2.service_account.Credentials.from_service_account_file', return_value=credential), \
             patch('google.auth.transport.requests.Request'):
            vertex_auth._credential_provider.cache_clear()
            token = vertex_auth._credential_provider('test-only.json')
            self.assertEqual(token(), 'test-token')
            self.assertEqual(token(), 'test-token')
            self.assertEqual(credential.refresh.call_count, 1)
            credential.valid = False
            token()
            self.assertEqual(credential.refresh.call_count, 2)
        vertex_auth._credential_provider.cache_clear()

    def test_vertex_configuration_never_stores_bearer_token(self):
        import os
        from vertex_auth import configure_vertex
        with patch.dict('os.environ', {'LAB_VERTEX_CREDENTIALS':'test-only.json',
                        'LAB_VERTEX_PROJECT':'test-project', 'LAB_VERTEX_LOCATION':'global'}, clear=True):
            self.assertTrue(configure_vertex())
            self.assertEqual(os.environ['LAB_API_KEY'], 'vertex-oauth')
            self.assertEqual(os.environ['LAB_BASE_URL'],
                'https://aiplatform.googleapis.com/v1/projects/test-project/locations/global/endpoints/openapi')


if __name__ == '__main__':
    unittest.main()
