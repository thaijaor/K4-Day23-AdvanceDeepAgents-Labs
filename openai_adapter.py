"""Preserve provider tool-call extensions through LangChain's OpenAI adapter.

Gemini's compatible endpoint returns thought signatures in extra_content. The pinned
langchain-openai normalizes tool calls and drops that field; retain it by call ID.
Uses the OpenAI SDK via ChatOpenAI, without modifying the provided model factory.
"""
from copy import deepcopy
import os
import asyncio
import json
import re
import threading
import time
from collections import deque

import openai
from pydantic import PrivateAttr

from langchain_core.rate_limiters import InMemoryRateLimiter

from langchain_openai import ChatOpenAI
from vertex_auth import vertex_token_provider


def estimate_input_tokens(payload):
    """Exclude opaque provider signatures, which are metadata rather than model text."""
    def text_fields(value):
        if isinstance(value, dict):
            return {key: text_fields(item) for key, item in value.items() if key != 'thought_signature'}
        if isinstance(value, list):
            return [text_fields(item) for item in value]
        return value
    return len(json.dumps(text_fields(payload), ensure_ascii=False, default=str)) // 3 + 1


class TokenWindow:
    """A shared rolling minute window for estimated input tokens."""
    def __init__(self):
        self.lock = threading.Lock()
        self.events = deque()

    def reserve(self, size, limit):
        if limit <= 0:
            return
        size = min(size, limit)
        while True:
            with self.lock:
                now = time.monotonic()
                while self.events and now - self.events[0][0] >= 60:
                    self.events.popleft()
                if sum(n for _, n in self.events) + size <= limit:
                    self.events.append((now,size))
                    return
                delay = max(.1, 60 - (now-self.events[0][0]) + .1)
            time.sleep(delay)


class OpenAICompatibleChat(ChatOpenAI):
    _token_window: TokenWindow = PrivateAttr(default_factory=TokenWindow)

    def _reserve_tokens(self, messages, stop, kwargs):
        limit = int(os.getenv('LAB_INPUT_TOKENS_PER_MINUTE', '0'))
        if limit <= 0:
            return
        payload = self._get_request_payload(messages, stop=stop, **kwargs)
        # Conservative estimate for English evidence plus tool schemas; actual counts are recorded separately.
        estimate = estimate_input_tokens(payload)
        self._token_window.reserve(estimate, limit)

    @staticmethod
    def _quota_delay(exc):
        match = re.search(r'(?:retry in |retryDelay[^0-9]*)([0-9.]+)s', str(exc), re.I)
        return min(60, float(match[1]) + 2) if match else 60

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        for attempt in range(4):
            self._reserve_tokens(messages, stop, kwargs)
            try:
                return super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)
            except openai.RateLimitError as exc:
                if attempt == 3 or re.search(r"RequestsPerDay|requests_per_day", str(exc), re.I):
                    raise
                delay = self._quota_delay(exc)
                print(f'[LLM] quota cooldown {delay:.0f}s', flush=True)
                time.sleep(delay)

    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
        for attempt in range(4):
            await asyncio.to_thread(self._reserve_tokens, messages, stop, kwargs)
            try:
                return await super()._agenerate(messages, stop=stop, run_manager=run_manager, **kwargs)
            except openai.RateLimitError as exc:
                if attempt == 3 or re.search(r"RequestsPerDay|requests_per_day", str(exc), re.I):
                    raise
                delay = self._quota_delay(exc)
                print(f'[LLM] quota cooldown {delay:.0f}s', flush=True)
                await asyncio.sleep(delay)

    def _create_chat_result(self, response, generation_info=None):
        result = super()._create_chat_result(response, generation_info)
        raw = response if isinstance(response, dict) else response.model_dump()
        for generation, choice in zip(result.generations, raw.get('choices', [])):
            extensions = {call['id']: deepcopy(call['extra_content'])
                          for call in choice.get('message', {}).get('tool_calls') or []
                          if call.get('extra_content') and call.get('id')}
            if extensions:
                generation.message.additional_kwargs['provider_tool_extensions'] = extensions
        return result

    def _get_request_payload(self, input_, *, stop=None, **kwargs):
        payload = super()._get_request_payload(input_, stop=stop, **kwargs)
        messages = self._convert_input(input_).to_messages()
        for original, outgoing in zip(messages, payload.get('messages', [])):
            extensions = original.additional_kwargs.get('provider_tool_extensions', {})
            for call in outgoing.get('tool_calls', []):
                if call.get('id') in extensions:
                    call['extra_content'] = deepcopy(extensions[call['id']])
        return payload


def preserve_tool_extensions(model):
    """Wrap compatible chat models; retain all configured model/client options."""
    if not isinstance(model, ChatOpenAI) or isinstance(model, OpenAICompatibleChat):
        return model
    values = {name: getattr(model, name) for name in type(model).model_fields
              if name not in {'client', 'async_client', 'root_client', 'root_async_client'}}
    values.update(disable_streaming=True, streaming=False, use_responses_api=False,
                  max_retries=max(6, model.max_retries or 0))
    token_provider = vertex_token_provider()
    if token_provider is not None:
        values['openai_api_key'] = token_provider
    effort = os.getenv('LAB_REASONING_EFFORT')
    if effort:
        values['reasoning_effort'] = effort
    rpm = float(os.getenv('LAB_REQUESTS_PER_MINUTE', '0'))
    if rpm > 0:
        values['rate_limiter'] = InMemoryRateLimiter(requests_per_second=rpm / 60,
                                                    check_every_n_seconds=0.1, max_bucket_size=1)
    return OpenAICompatibleChat(**values)
