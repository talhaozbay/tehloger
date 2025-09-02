from datetime import datetime, timedelta, timezone
def to_dt(s): return datetime.fromisoformat(s.replace("Z","+00:00"))
def window_filter(events, seconds=300):
    if not events: return events
    end = to_dt(events[-1]["ts_utc"])
    start = end - timedelta(seconds=seconds)
    return [e for e in events if to_dt(e["ts_utc"])>=start]
