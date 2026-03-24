#!/usr/bin/env python3
"""
OpenClaw API Quota Checker
Sends minimal test requests to each provider and reads rate limit headers.
"""

import json
import os
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from pathlib import Path

OPENCLAW_DIR = Path.home() / '.openclaw'
CONFIG_FILE = OPENCLAW_DIR / 'openclaw.json'
AUTH_FILE = OPENCLAW_DIR / 'agents' / 'main' / 'agent' / 'auth-profiles.json'
UA = 'openclaw-quota-check/1.0'


def load_api_keys():
    """Load API keys from env vars, openclaw.json, and auth-profiles.json"""
    keys = {}

    # Read openclaw.json
    cfg = {}
    try:
        with open(CONFIG_FILE) as f:
            cfg = json.load(f)
    except Exception:
        pass

    cfg_env = cfg.get('env', {})
    providers = cfg.get('models', {}).get('providers', {})

    # Read auth-profiles.json
    auth_profiles = {}
    try:
        with open(AUTH_FILE) as f:
            auth = json.load(f)
        auth_profiles = auth.get('profiles', {})
    except Exception:
        pass

    # Groq: env -> openclaw.json providers -> openclaw.json env
    keys['groq'] = (
        os.environ.get('GROQ_API_KEY')
        or providers.get('groq', {}).get('apiKey')
        or cfg_env.get('GROQ_API_KEY')
    )

    # Gemini: env -> openclaw.json env -> auth-profiles
    keys['gemini'] = (
        os.environ.get('GEMINI_API_KEY')
        or cfg_env.get('GEMINI_API_KEY')
        or auth_profiles.get('google:default', {}).get('key')
    )

    # Mistral: env -> openclaw.json env
    keys['mistral'] = (
        os.environ.get('MISTRAL_API_KEY')
        or cfg_env.get('MISTRAL_API_KEY')
    )

    # OpenRouter: env -> auth-profiles
    keys['openrouter'] = (
        os.environ.get('OPENROUTER_API_KEY')
        or auth_profiles.get('openrouter:default', {}).get('key')
        or auth_profiles.get('openrouter:manual', {}).get('key')
    )

    return keys


def send_request(url, headers, data=None, timeout=15):
    """Send HTTP request and return (status_code, response_headers, body_preview)"""
    req = Request(url, headers=headers)
    if data is not None:
        req.data = json.dumps(data).encode('utf-8')
        req.add_header('Content-Type', 'application/json')

    try:
        resp = urlopen(req, timeout=timeout)
        resp_headers = dict(resp.headers)
        body = resp.read().decode('utf-8', errors='replace')[:500]
        return resp.status, resp_headers, body
    except HTTPError as e:
        resp_headers = dict(e.headers)
        try:
            body = e.read().decode('utf-8', errors='replace')[:500]
        except Exception:
            body = ''
        return e.code, resp_headers, body
    except URLError as e:
        return None, {}, f'Connection error: {e.reason}'
    except Exception as e:
        return None, {}, str(e)


def parse_ratelimit_headers(headers):
    """Extract rate limit info from response headers"""
    info = {}
    h = {k.lower(): v for k, v in headers.items()}

    for prefix in ['x-ratelimit-', 'ratelimit-']:
        if f'{prefix}remaining-requests' in h:
            info['remaining_req'] = h[f'{prefix}remaining-requests']
        if f'{prefix}limit-requests' in h:
            info['limit_req'] = h[f'{prefix}limit-requests']
        if f'{prefix}remaining-tokens' in h:
            info['remaining_tok'] = h[f'{prefix}remaining-tokens']
        if f'{prefix}limit-tokens' in h:
            info['limit_tok'] = h[f'{prefix}limit-tokens']
        if f'{prefix}reset-requests' in h:
            info['reset'] = h[f'{prefix}reset-requests']
        elif f'{prefix}reset' in h:
            info['reset'] = h[f'{prefix}reset']

    if 'retry-after' in h:
        info['retry_after'] = h['retry-after']

    return info


def format_status(status_code, headers, body, provider_name):
    """Format the check result for display"""
    lines = []

    if status_code is None:
        lines.append('  Status: CONNECTION ERROR')
        lines.append(f'  Detail: {body[:150]}')
        return '\n'.join(lines)

    rl = parse_ratelimit_headers(headers)

    if status_code == 200:
        lines.append('  Status: OK')
    elif status_code == 429:
        lines.append('  Status: RATE LIMITED')
    elif status_code in (401, 403):
        lines.append(f'  Status: AUTH ERROR ({status_code})')
    elif status_code == 413:
        lines.append('  Status: REQUEST TOO LARGE')
    else:
        lines.append(f'  Status: ERROR ({status_code})')

    if rl.get('remaining_req') is not None:
        lines.append(f'  Requests: {rl["remaining_req"]}/{rl.get("limit_req", "?")} remaining')
    if rl.get('remaining_tok') is not None:
        lines.append(f'  Tokens: {rl["remaining_tok"]}/{rl.get("limit_tok", "?")} remaining')
    if rl.get('reset'):
        lines.append(f'  Reset: {rl["reset"]}')
    if rl.get('retry_after'):
        lines.append(f'  Retry after: {rl["retry_after"]}s')

    if status_code >= 400:
        try:
            err = json.loads(body)
            msg = (
                err.get('error', {}).get('message', '')
                or err.get('message', '')
                or err.get('error', '')
            )
            if isinstance(msg, str) and msg:
                lines.append(f'  Detail: {msg[:150]}')
        except Exception:
            if body:
                lines.append(f'  Detail: {body[:150]}')

    if not rl and status_code == 200:
        lines.append('  (No rate limit headers returned)')

    return '\n'.join(lines)


def check_groq(api_key):
    status, headers, body = send_request(
        'https://api.groq.com/openai/v1/chat/completions',
        {'Authorization': f'Bearer {api_key}', 'User-Agent': UA},
        {
            'model': 'llama-3.3-70b-versatile',
            'messages': [{'role': 'user', 'content': 'hi'}],
            'max_tokens': 1
        }
    )
    return format_status(status, headers, body, 'Groq')


def check_mistral(api_key):
    status, headers, body = send_request(
        'https://api.mistral.ai/v1/chat/completions',
        {'Authorization': f'Bearer {api_key}', 'User-Agent': UA},
        {
            'model': 'mistral-small-latest',
            'messages': [{'role': 'user', 'content': 'hi'}],
            'max_tokens': 1
        }
    )
    return format_status(status, headers, body, 'Mistral')


def check_gemini(api_key):
    url = (
        'https://generativelanguage.googleapis.com/v1beta/'
        f'models/gemini-2.5-flash-lite:generateContent?key={api_key}'
    )
    status, headers, body = send_request(
        url,
        {'User-Agent': UA},
        {
            'contents': [{'parts': [{'text': 'hi'}]}],
            'generationConfig': {'maxOutputTokens': 1}
        }
    )
    return format_status(status, headers, body, 'Gemini')


def check_openrouter(api_key):
    status, headers, body = send_request(
        'https://openrouter.ai/api/v1/chat/completions',
        {'Authorization': f'Bearer {api_key}', 'User-Agent': UA},
        {
            'model': 'meta-llama/llama-3.3-70b-instruct:free',
            'messages': [{'role': 'user', 'content': 'hi'}],
            'max_tokens': 1
        }
    )
    return format_status(status, headers, body, 'OpenRouter')


def main():
    keys = load_api_keys()

    print('=== OpenClaw API Quota Status ===')
    print()

    print('[Groq] llama-3.3-70b-versatile')
    if keys.get('groq'):
        print(check_groq(keys['groq']))
    else:
        print('  Status: API key not found')
    print()

    print('[Mistral] mistral-small-latest')
    if keys.get('mistral'):
        print(check_mistral(keys['mistral']))
    else:
        print('  Status: API key not found')
    print()

    print('[Google Gemini] gemini-2.5-flash-lite')
    if keys.get('gemini'):
        print(check_gemini(keys['gemini']))
    else:
        print('  Status: API key not found')
    print()

    print('[OpenRouter] llama-3.3-70b-instruct:free')
    if keys.get('openrouter'):
        print(check_openrouter(keys['openrouter']))
    else:
        print('  Status: API key not found')
    print()

    print('[OpenAI Codex] gpt-5.3-codex')
    print('  Status: OAuth - cannot check via API')
    print('  Check: https://platform.openai.com/usage')
    print()

    print('[Qwen Portal] coder-model')
    print('  Status: OAuth - cannot check via API')
    print('  Check: https://portal.qwen.ai')


if __name__ == '__main__':
    main()
