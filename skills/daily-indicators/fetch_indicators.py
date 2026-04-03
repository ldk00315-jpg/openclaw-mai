#!/usr/bin/env python3
"""
Daily Indicators Fetcher
Uses curl for HTTP requests (more reliable with Yahoo Finance).
"""

import json
import subprocess
import time

SYMBOLS = [
    ('USDJPY=X', 'USD/JPY', 'fx'),
    ('CL=F', 'WTI', 'commodity'),
    ('^N225', 'Nikkei 225', 'index'),
    ('^DJI', 'Dow Jones', 'index'),
    ('^IXIC', 'NASDAQ', 'index'),
    ('^GSPC', 'S&P 500', 'index'),
]


def curl_get(url, timeout=15):
    try:
        result = subprocess.run(
            ['curl', '-s', '-m', str(timeout), '-H', 'User-Agent: Mozilla/5.0', url],
            capture_output=True, text=True, timeout=timeout+5)
        if result.returncode == 0 and result.stdout:
            return result.stdout
    except Exception:
        pass
    return None


def fetch_quote(symbol):
    url = f'https://query2.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=2d'
    body = curl_get(url)
    if not body:
        return None
    try:
        data = json.loads(body)
        err = data.get('chart', {}).get('error')
        if err:
            return None
        meta = data['chart']['result'][0]['meta']
        price = meta.get('regularMarketPrice', 0)
        prev = meta.get('chartPreviousClose', 0)
        if not prev:
            prev = meta.get('previousClose', 0)
        return price, prev
    except Exception:
        return None


def format_quote(name, qtype, price, prev):
    if prev and prev != 0:
        change = price - prev
        change_pct = (change / prev) * 100
        sign = '+' if change >= 0 else ''
    else:
        change = 0
        change_pct = 0
        sign = ''

    if qtype == 'fx':
        return f'{price:.3f} ({sign}{change:.3f}, {sign}{change_pct:.2f}%)'
    elif qtype == 'commodity':
        return f'${price:.2f} ({sign}{change:.2f}, {sign}{change_pct:.2f}%)'
    else:
        return f'{price:,.2f} ({sign}{change:,.2f}, {sign}{change_pct:.2f}%)'


def fetch_weather():
    """Fetch Komagane weather from tenki.jp (today's telop + high/low)."""
    body = curl_get('https://tenki.jp/forecast/3/23/4830/20210/')
    if not body:
        return 'ERROR: tenki.jp connection failed'

    try:
        import re

        # Weather telop (e.g., 晴時々曇)
        telop_match = re.search(r'<p class="weather-telop">\s*([^<]+?)\s*</p>', body)
        telop = telop_match.group(1).strip() if telop_match else '天気不明'

        # Today high / low
        high_match = re.search(
            r'<dt class="high-temp sumarry">最高</dt>\s*<dd class="high-temp temp">\s*<span class="value">\s*([\-0-9]+)\s*</span>',
            body,
            re.S,
        )
        low_match = re.search(
            r'<dt class="low-temp sumarry">最低</dt>\s*<dd class="low-temp temp">\s*<span class="value">\s*([\-0-9]+)\s*</span>',
            body,
            re.S,
        )

        if not high_match or not low_match:
            return 'ERROR: tenki.jp parse failed'

        high_temp = high_match.group(1)
        low_temp = low_match.group(1)
        return f'{telop} (high {high_temp}C / low {low_temp}C) [tenki.jp]'
    except Exception as e:
        return f'ERROR: {str(e)[:80]}'


def main():
    print('=== Daily Indicators ===')
    print()

    print('[Market Data]')
    for symbol, name, qtype in SYMBOLS:
        result = fetch_quote(symbol)
        if result:
            price, prev = result
            print(f'  {name}: {format_quote(name, qtype, price, prev)}')
        else:
            print(f'  {name}: ERROR: data not available')
        time.sleep(0.5)
    print()

    print('[Komagane Weather]')
    weather = fetch_weather()
    print(f'  {weather}')


if __name__ == '__main__':
    main()
