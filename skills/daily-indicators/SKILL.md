---
name: daily-indicators
description: Fetch daily market indicators (USD/JPY, WTI, Nikkei, Dow, NASDAQ, S&P500) and Komagane weather. Always source weather from tenki.jp for this skill.
user-invocable: true
---

# Daily Indicators

Run the daily indicators script and relay the results to the user.

## Instructions

1. Run the following command:
   ```bash
   python3 ~/.openclaw/workspace/skills/daily-indicators/fetch_indicators.py
   ```

2. Present the output to the user in a clear, friendly format.

3. Weather in this skill is sourced from tenki.jp (Komagane page). Keep that source unless user asks to change it.

4. If any indicator shows ERROR, mention it briefly but don't dwell on it.
