import socket
from datetime import datetime, timezone
import win32evtlog                                   # Evt* API
from xml.etree import ElementTree as ET

QUERY = "*[System[(EventID=4625)]]"

from datetime import datetime, timezone, timedelta

UTC_PLUS_3 = timezone(timedelta(hours=3))

def _to_iso_local(dt: datetime) -> str:
    return dt.astimezone(UTC_PLUS_3).strftime("%d-%m-%YT%H:%M:%S%z")


# def _to_iso_utc(dt: datetime) -> str:
#     return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def _as_str(val):
    return val if val and val != "-" else None

def collect(max_events=500, time_from=None):
    """
    EvtQuery ile Security logundan 4625 çek.
    time_from: ISO8601 (UTC) string verilirse sadece sonrasını alır.
    """
    h = win32evtlog.EvtQuery("Security", win32evtlog.EvtQueryReverseDirection, QUERY)
    events = []
    count = 0
    host = socket.gethostname()

    while True:
        handles = win32evtlog.EvtNext(h, 32)
        if not handles:
            break
        for eh in handles:
            xml = win32evtlog.EvtRender(eh, win32evtlog.EvtRenderEventXml)
            root = ET.fromstring(xml)
            # Zaman & Alanlar
            ts = root.findtext(".//System/TimeCreated")
            if ts and "SystemTime" in root.find(".//System/TimeCreated").attrib:
                s = root.find(".//System/TimeCreated").attrib["SystemTime"]
                dt = datetime.fromisoformat(s.replace("Z","+00:00"))
            else:
                dt = datetime.now(timezone.utc)

            if time_from:
                tf = datetime.fromisoformat(time_from.replace("Z","+00:00"))
                if dt < tf:
                    continue

            ev = {
                "ts_utc": _to_iso_utc(dt),
                "host": host,
                "user": root.findtext(".//EventData/Data[@Name='TargetUserName']"),
                "domain": root.findtext(".//EventData/Data[@Name='TargetDomainName']"),
                "src_ip": _as_str(root.findtext(".//EventData/Data[@Name='IpAddress']")),
                "src_host": _as_str(root.findtext(".//EventData/Data[@Name='WorkstationName']")),
                "logon_type": _as_str(root.findtext(".//EventData/Data[@Name='LogonType']")),
                "status": _as_str(root.findtext(".//EventData/Data[@Name='Status']")),
                "substatus": _as_str(root.findtext(".//EventData/Data[@Name='SubStatus']")),
                "process": _as_str(root.findtext(".//EventData/Data[@Name='ProcessName']")),
                "reason": "Logon failure (4625)",
                "raw": (xml[:800] if xml else None)
            }
            events.append(ev)
            count += 1
            if count >= max_events:
                break
        if count >= max_events:
            break
    return list(reversed(events))  # kronolojik
