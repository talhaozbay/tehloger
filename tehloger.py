# clearlog/windows_parser.py
import socket
from datetime import datetime, timezone
from xml.etree import ElementTree as ET



from typing import List
from .schemas import AuthFailEvent
from collections import defaultdict
from typing import List, Tuple
from .schemas import AuthFailEvent
import yaml, os
from datetime import datetime, timedelta, timezone
# clearlog/main.py
import json, platform, shutil
from .linux_parser import collect_linux
from .windows_parser import collect_windows
from .formatters import to_human
from .aggregator import top_sources
from .config import load_config
from .schemas import asdict













try:
    import win32evtlog                        # pywin32
    import win32evtlogutil
    import win32con
except Exception:
    win32evtlog = None

from .schemas import AuthFailEvent

def _to_iso_utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def collect_windows(max_events=500):
    if not win32evtlog:
        return []
    server = 'localhost'
    logtype = 'Security'
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    hand = win32evtlog.OpenEventLog(server, logtype)
    host = socket.gethostname()

    events = []
    read = 0
    while True:
        records = win32evtlog.ReadEventLog(hand, flags, 0)
        if not records:
            break
        for ev in records:
            if ev.EventID & 0xFFFF != 4625:
                continue
            read += 1
            # Zaman
            dt = ev.TimeGenerated.replace(tzinfo=timezone.utc)
            # XML'e dönüştür
            try:
                xml = win32evtlogutil.SafeFormatMessage(ev, logtype)
            except Exception:
                xml = ""
            user = ip = workstation = reason = None
            try:
                root = ET.fromstring(xml)
                # Event/EventData/Data[@Name="..."]
                for data in root.iter():
                    if data.tag.endswith('Data') and 'Name' in data.attrib:
                        name = data.attrib['Name']
                        val = (data.text or "").strip()
                        if name == 'TargetUserName':
                            user = val
                        elif name == 'IpAddress':
                            ip = val if val and val != '-' else None
                        elif name == 'WorkstationName':
                            workstation = val
                        elif name == 'SubStatus':
                            reason = f"SubStatus:{val}"
            except Exception:
                pass

            events.append(AuthFailEvent(
                ts_utc=_to_iso_utc(dt),
                platform="windows",
                host=host,
                user=user,
                src_ip=ip,
                src_host=workstation,
                method="interactive/remote",
                reason=reason or "Logon failure (4625)",
                raw=(xml[:500] if xml else None)
            ))
            if read >= max_events:
                break
        if read >= max_events:
            break
    win32evtlog.CloseEventLog(hand)
    return list(reversed(events))  # zamansal sırala






def to_human(events: List[AuthFailEvent]) -> str:
    lines = []
    for e in events:
        who = e.user or "unknown"
        src = e.src_ip or e.src_host or "-"
        lines.append(f"[{e.ts_utc}] {e.platform.upper()} @{e.host}: user={who} src={src} reason={e.reason}")
    return "\n".join(lines)

def top_sources(events: List[AuthFailEvent], topn=5) -> List[Tuple[str,int]]:
    counter = defaultdict(int)
    for e in events:
        key = e.src_ip or e.src_host or "unknown"
        counter[key] += 1
    return sorted(counter.items(), key=lambda x: x[1], reverse=True)[:topn]

def load_config(path="configs/default.yaml"):
    if os.path.exists(path):
        with open(path, "r") as f:
            return yaml.safe_load(f)
    return {"threshold": {"window_sec": 300, "max_fails": 3}}
def within_window(events, window_sec=300):
    if not events: return events
    end = max(e.ts_utc for e in events)
    end_dt = datetime.fromisoformat(end.replace("Z","+00:00"))
    start_dt = end_dt - timedelta(seconds=window_sec)
    return [e for e in events if datetime.fromisoformat(e.ts_utc.replace("Z","+00:00")) >= start_dt]

def run():
    cfg = load_config()
    events = []
    system = platform.system().lower()
    if system == "windows":
        events.extend(collect_windows(max_events=500))
    else:
        events.extend(collect_linux(limit=1000))

    # çıktı
    print("=== HUMAN READABLE ===")
    print(to_human(events))
    print("\n=== TOP SOURCES ===")
    for src, n in top_sources(events, topn=5):
        print(f"{src}: {n}")

    # JSON dump (normalize)
    print("\n=== JSON (normalized) ===")
    print(json.dumps([e.__dict__ for e in events], indent=2))

    # Basit eşik uyarısı
    window = cfg["threshold"]["window_sec"]
    maxf = cfg["threshold"]["max_fails"]
    recent = events[-maxf:]
    if len(recent) >= maxf:
        print(f"\n[INFO] Son {window}s içinde {len(recent)} hatalı deneme yakalandı.")
        if len(recent) >= maxf:
            print(f"[ALERT] Eşik aşıldı: >= {maxf} failed password!")
            # gelecekte: e-posta/Slack entegrasyonu

if __name__ == "__main__":
    run()