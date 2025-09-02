# Tehloger

`tehloger` is a simple Python tool that collects **4625 – Logon Failure** events from the Windows Security log and reports them in a user‑friendly format. This event type is generated for both local login attempts and remote access attempts (RDP, SMB shares, WinRM, etc.). The tool normalizes timestamps and user information, lists the most frequent IP addresses and usernames, and can optionally output JSON.

## Features

- Reads failed logon events (ID 4625) from the Windows Security log.
- Collects both local and remote login attempts; displays IP address and workstation name for remote attempts.
- Uses two different `pywin32` APIs: new (`EvtQuery`) and legacy (`ReadEventLog`). Falls back automatically if needed.
- Output consists of three sections:
  - **Human Readable List** – shows timestamp, username, source IP/host, logon type, and status code.
  - **Top Sources** – summarizes which IP addresses and usernames attempted the most logons.
  - **JSON** – normalized event objects, can be saved with `--json` parameter.
- Flexible usage via `--since`, `--max`, and `--json` parameters.

## Requirements

- Windows 10/11 or server editions (not supported on Linux/macOS)
- Python 3.7+ (Python 3.9 recommended)
- **Administrator privileges** required to access the Security log.
- Python packages:
  - `pywin32` – for accessing Windows event logs
  - `PyYAML` – for reading configuration files

## Installation

Clone or download the repository:

```bash
git clone https://github.com/talhaozbay/tehloger.git
cd tehloger
```

Create and activate a virtual environment (recommended):

```bash
python -m venv venv
venv\Scripts\activate  # Windows PowerShell / Cmd
```

Install dependencies:

```bash
pip install pywin32 pyyaml
```

Fix the configuration file (`configs/default.yaml`):

```yaml
threshold:
  window_sec: 300   # 5-minute window
  max_fails: 3      # alert threshold
max_events: 500
```

If running Python files directly, make sure imports in `tehloger/main.py` are absolute, or use the module call described below.

## Usage

Run as a package:

```bash
python -m tehloger.main
```

### Parameters

- `--max <number>` – limits the number of events retrieved.
- `--since <datetime>` – ISO 8601 format (e.g., `2025-09-01T00:00:00Z`).
- `--json <file>` – saves JSON output to the given file.

### Examples

```bash
# Read the last 200 failed logon attempts and print them
python -m tehloger.main --max 200

# Save all 4625 events from the last 24 hours to JSON
python -m tehloger.main --since 2025-09-01T00:00:00Z --json C:\temp\failures.json
```

**Note:** Run the command with administrator rights.

## Timestamps and Time Zone

Events are logged in **UTC** by default (`ts_utc` field in ISO‑8601). Since Turkey time is UTC+3, you can adjust formatting in `formatters.py` if you want to display local time.

## Configuration

`configs/default.yaml` contains:

- `threshold.window_sec` – time window in seconds (default: 300)
- `threshold.max_fails` – threshold for failed attempts (default: 3)
- `max_events` – default number of events to fetch (default: 500)

If the file is missing or invalid, defaults in `tehloger/config.py` are used.

## Why are some fields empty?

Local logon attempts may not include IP address, domain name, or workstation name. In such cases, these fields appear as `null` in JSON output.

## Tests

Run basic unit tests with:

```bash
pip install pytest
pytest -q
```

## License and Contributions

This project is a personal work and is not yet licensed under an open-source license. Feel free to open issues or pull requests for bug reports and contributions. **It is your responsibility to comply with company policies and legal regulations when using this tool.**
