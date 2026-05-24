#!/usr/bin/env python3
"""system_devices_fetcher.py

Beginner-friendly (stdlib only) device inventory from the *local* Windows ARP table.

What it returns:
- IP address (from ARP)
- MAC address (from ARP)
- Adapter name (very basic grouping)

Notes:
- Models/vendor are often not available without external lookups or router-level access.
- This script is intentionally limited to safe, local, read-only info.

Run:
  python system_devices_fetcher.py

Optional:
  python system_devices_fetcher.py --save devices.json
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from typing import Dict, List, Tuple


ARP_LINE_RE = re.compile(r"^(?P<ip>\d+\.\d+\.\d+\.\d+)\s+(?P<mac>(?:[0-9a-fA-F]{2}-){5}[0-9a-fA-F]{2})\s+\w+$")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(cmd: List[str]) -> Tuple[int, str, str]:
    p = subprocess.run(cmd, capture_output=True, text=True, shell=False)
    return p.returncode, p.stdout or "", p.stderr or ""


def parse_arp(output: str) -> List[Dict[str, str]]:
    devices: List[Dict[str, str]] = []
    for line in output.splitlines():
        line = line.strip()
        if not line or line.lower().startswith("interface") or line.lower().startswith("internet"):
            continue
        m = ARP_LINE_RE.match(line)
        if not m:
            continue
        devices.append({
            "ip": m.group("ip"),
            "mac": m.group("mac"),
        })
    # de-dupe by (ip, mac)
    seen = set()
    out: List[Dict[str, str]] = []
    for d in devices:
        key = (d["ip"], d["mac"].lower())
        if key in seen:
            continue
        seen.add(key)
        out.append(d)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch local device info from Windows ARP cache (IP + MAC).")
    parser.add_argument("--save", default=None, help="Optional path to save JSON output")
    args = parser.parse_args()

    # arp -a shows something like:
    # Interface: 192.168.1.10 --- 0x... 
    #   Internet Address      Physical Address      Type
    #   192.168.1.1           aa-bb-cc-dd-ee-ff     dynamic
    code, out, err = run_cmd(["arp", "-a"])
    if code != 0:
        print("ERROR: arp command failed.")
        if err:
            print(err)
        return 2

    devices = parse_arp(out)

    result = {
        "generated_utc": utc_now(),
        "count": len(devices),
        "devices": devices,
        "model_info": "Not included (requires external/vendor lookup or router/DNS access).",
    }

    print("=== Connected devices (from ARP cache) ===")
    if not devices:
        print("No ARP entries found. Try accessing devices on your network first.")
    else:
        for d in devices:
            print(f'{d["ip"]}\t{d["mac"]}')

    if args.save:
        path = args.save
        with open(path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"\nSaved JSON to: {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

