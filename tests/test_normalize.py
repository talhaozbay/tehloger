## Basit Test (örnek)

# tests/test_normalize.py
from xml.etree import ElementTree as ET
from tehloger.collector_evtapi import _as_str

def test_as_str():
    assert _as_str("1.2.3.4") == "1.2.3.4"
    assert _as_str("-") is None
