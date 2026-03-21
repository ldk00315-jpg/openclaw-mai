# HEARTBEAT.md

# Task: USD/JPY change alert (about hourly)

On heartbeat:
1) Fetch current USD/JPY mid rate (e.g., from stooq):
   `curl -s 'https://stooq.com/q/l/?s=usdjpy&i=60'`
   Parse latest close as current rate.
2) Read `memory/heartbeat-state.json`.
   - If `fx.usdjpy.lastRate` is missing, set it and stop (no alert).
3) If `abs(current - lastRate) >= 1.0`, send alert message in this DM:
   - Include previous rate, current rate, delta, and that this is a heartbeat FX alert.
4) Update `fx.usdjpy.lastRate` and `fx.usdjpy.lastCheckedAt` in `memory/heartbeat-state.json`.

If fetch fails, do not alert; just keep previous state.
