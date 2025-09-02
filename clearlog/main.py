# clearlog/main.py
import argparse, json
from .config import load
from . import collector_evtapi as evt
from . import collector_legacy as legacy
from .formatters import human, top_by
from .utils import window_filter

def collect(max_events, since=None):
    try:
        return evt.collect(max_events=max_events, time_from=since)
    except Exception:
        return legacy.collect(max_events=max_events)

def run():
    parser = argparse.ArgumentParser(description="Windows 4625 failed logon collector")
    parser.add_argument("--since", help="ISO8601 UTC: 2025-09-02T00:00:00Z", default=None)
    parser.add_argument("--json", help="JSON çıktısını dosyaya yaz", default=None)
    parser.add_argument("--max", type=int, default=None, help="Maks event sayısı")
    args = parser.parse_args()

    cfg = load()
    max_events = args.max or cfg["max_events"]
    events = collect(max_events=max_events, since=args.since)

    print("=== HUMAN READABLE ===")
    print(human(events))

    print("\n=== TOP SOURCE IP ===")
    for k,n in top_by("src_ip", events, 5): print(f"{k}: {n}")

    print("\n=== TOP USERS ===")
    for k,n in top_by("user", events, 5): print(f"{k}: {n}")

    if args.json:
        with open(args.json,"w", encoding="utf-8") as f:
            json.dump(events, f, indent=2)
        print(f"\nJSON yazıldı: {args.json}")
    else:
        print("\n=== JSON (normalized) ===")
        print(json.dumps(events, indent=2))

    # Basit eşik uyarısı
    recent = window_filter(events, seconds=cfg["threshold"]["window_sec"])
    if len(recent) >= cfg["threshold"]["max_fails"]:
        print(f"\n[ALERT] Son {cfg['threshold']['window_sec']}s içinde {len(recent)} adet 4625 tespit edildi!")

if __name__ == "__main__":
    run()
