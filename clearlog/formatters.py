# clearlog/formatters.py
def human(events):
    lines = []
    for e in events:
        # None değerleri boş stringe dönüştür
        domain = e.get("domain") or ""
        user   = e.get("user") or "unknown"
        # Domain varsa 'DOMAIN\kullanıcı' şeklinde, yoksa sadece kullanıcı
        who = f"{domain}\\{user}" if domain else user
        src = e.get("src_ip") or e.get("src_host") or "-"
        logon_type = e.get("logon_type") or "-"
        status = e.get("status") or "-"
        lines.append(f"[{e['ts_utc']}] {who:<20} src={src:<15} type={logon_type} status={status}")
    return "\n".join(lines)


def top_by(key, events, topn=5):
    from collections import Counter
    vals=[(e.get(key) or "unknown") for e in events]
    return Counter(vals).most_common(topn)
