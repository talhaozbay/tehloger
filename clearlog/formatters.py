# clearlog/formatters.py
def human(events):
    lines=[]
    for e in events:
        who = e.get("domain","") + ("\\" if e.get("domain") else "") + (e.get("user") or "unknown")
        src = e.get("src_ip") or e.get("src_host") or "-"
        lines.append(f"[{e['ts_utc']}] {who:<20} src={src:<15} type={e.get('logon_type') or '-'} status={e.get('status') or '-'}")
    return "\n".join(lines)

def top_by(key, events, topn=5):
    from collections import Counter
    vals=[(e.get(key) or "unknown") for e in events]
    return Counter(vals).most_common(topn)
