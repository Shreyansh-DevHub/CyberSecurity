#!/usr/bin/env python3
"""Quick system info GUI (Tkinter, stdlib only).

Shows CPU model, RAM, storage drives, and CPU usage (best-effort).
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tkinter as tk
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from tkinter import messagebox, scrolledtext



def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(cmd: list[str]) -> tuple[int, str, str]:
    p = subprocess.run(cmd, capture_output=True, text=True, shell=False)
    return p.returncode, p.stdout or "", p.stderr or ""


def parse_wmic_cpu_name(out: str) -> str | None:
    # WMIC output often has lines like:
    # Name
    # Intel(R) Core(TM) i5-8250U CPU @ 1.60GHz
    for line in out.splitlines():
        s = line.strip()
        if not s or s.lower() == "name":
            continue
        return s
    return None


def get_cpu_model() -> str:
    # WMIC is deprecated in newer Windows but often still present.
    code, out, _ = run_cmd(["wmic", "cpu", "get", "Name"])
    if code == 0:
        name = parse_wmic_cpu_name(out)
        if name:
            return name
    # fallback
    return "Unknown"


def get_memory_stats() -> dict[str, str]:
    # Using wmic to stay stdlib-only.
    # TotalPhysicalMemory + FreePhysicalMemory (KB)
    total_kb = None
    free_kb = None

    # WMIC output may have headings; we grab first digits.
    code, out, err = run_cmd(["wmic", "OS", "get", "TotalVisibleMemorySize"])
    if code == 0 and out.strip():
        for line in out.splitlines():
            s = line.strip()
            if s.isdigit():
                total_kb = int(s)
                break

    code, out, err = run_cmd(["wmic", "OS", "get", "FreePhysicalMemory"])
    if code == 0 and out.strip():
        for line in out.splitlines():
            s = line.strip()
            if s.isdigit():
                free_kb = int(s)
                break

    def kb_to_gb(kb: int | None) -> str:
        if kb is None:
            return "Unknown (WMIC unavailable or blocked)"
        gb = kb / 1024 / 1024
        return f"{gb:.2f} GB"

    return {
        "total_ram": kb_to_gb(total_kb),
        "available_ram": kb_to_gb(free_kb),
    }


def get_drives_stats() -> list[dict[str, str]]:
    # Query logical drives via PowerShell for best formatting.
    ps = (
        "powershell -NoProfile -Command "
        "\"Get-PSDrive -PSProvider FileSystem | "
        "Select-Object Name,Free,Used, @{Name='Total';Expression={($_.Free+$_.Used)}} | "
        "ForEach-Object { '{0}|{1}|{2}|{3}' -f $_.Name,$_.Free,$_.Used,($_.Free+$_.Used) }\""
    )
    code, out, err = run_cmd(["cmd", "/c", ps])
    drives: list[dict[str, str]] = []
    if code != 0 or not out.strip():
        # fallback: enumerate drives by filesystem
        # This fallback won't compute used/free nicely.
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            root = Path(f"{letter}:/")
            if root.exists():
                try:
                    total, used, free = _drive_total_used_free(root)
                    drives.append({"drive": f"{letter}:", "free": _bytes_to_gb(free), "total": _bytes_to_gb(total)})
                except Exception:
                    continue
        return drives

    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("|")
        if len(parts) != 4:
            continue
        name, free_s, used_s, total_s = parts

        drives.append({
            "drive": f"{name}:",
            "free": f"{free_s}",
            "total": f"{total_s}",
        })
    return drives


def _bytes_to_gb(num: int) -> str:
    return f"{num / (1024**3):.2f} GB"


def _drive_total_used_free(root: Path) -> tuple[int, int, int]:
    usage = __import__("shutil").disk_usage(str(root))
    return usage.total, usage.used, usage.free


def get_cpu_usage_percent(sample_seconds: float = 0.5) -> str:
    # Minimal, stdlib-only sampling using Windows perf counters via typeperf.
    # typeperf may not exist; fallback to Unknown.
    # We sample Processor(_Total)\% Processor Time
    try:
        ps_cmd = (
            "powershell -NoProfile -Command "
            "\"(Get-Counter '\\Processor(_Total)\\% Processor Time' -SampleInterval "
            f"{sample_seconds} -MaxSamples 1).CounterSamples[0].CookedValue\""
        )
        code, out, err = run_cmd(["cmd", "/c", ps_cmd])
        if code == 0 and out.strip():
            val = float(out.strip())
            return f"{val:.1f}%"
    except Exception:
        pass
    return "Unknown"


def collect_system_info() -> dict:
    info = {
        "generated_utc": utc_now(),
        "cpu": {
            "model": get_cpu_model(),
            "usage": get_cpu_usage_percent(),
        },
        "memory": get_memory_stats(),
        "drives": get_drives_stats(),
    }
    return info


def format_system_info(info: dict) -> str:
    lines: list[str] = []
    lines.append("SYSTEM INFO")
    lines.append(f"Generated (UTC): {info.get('generated_utc','')}")
    lines.append("")

    cpu = info.get("cpu", {})
    lines.append("CPU")
    lines.append(f"- Model: {cpu.get('model','Unknown')}")
    lines.append(f"- Usage: {cpu.get('usage','Unknown')}")
    lines.append("")

    mem = info.get("memory", {})
    lines.append("RAM")
    lines.append(f"- Total: {mem.get('total_ram','Unknown')}")
    lines.append(f"- Available: {mem.get('available_ram','Unknown')}")
    lines.append("")

    lines.append("STORAGE (drives)")
    drives = info.get("drives", [])
    if not drives:
        lines.append("- (No drive info found)")
    else:
        for d in drives:
            drive = d.get("drive", "")
            free = d.get("free", "")
            total = d.get("total", "")
            lines.append(f"- {drive}  Total: {total}  Free: {free}")

    return "\n".join(lines)


# -------------------- GUI --------------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("System Info (Simple GUI)")
        self.geometry("900x600")

        self.text = scrolledtext.ScrolledText(self, wrap=tk.WORD)
        self.text.pack(fill="both", expand=True, padx=10, pady=10)

        frm = tk.Frame(self)
        frm.pack(fill="x", padx=10, pady=(0,10))

        tk.Button(frm, text="Fetch system info", command=self.fetch_and_show).pack(side="left")
        tk.Button(frm, text="Save JSON", command=self.save_json).pack(side="left", padx=(10,0))

        self.last_info: dict | None = None
        self.fetch_and_show()

    def fetch_and_show(self):
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, "Fetching...\n")
        self.update_idletasks()

        try:
            info = collect_system_info()
            self.last_info = info
            self.text.delete("1.0", tk.END)
            self.text.insert(tk.END, format_system_info(info))
        except Exception as e:
            self.text.delete("1.0", tk.END)
            self.text.insert(tk.END, f"ERROR: {e}\n")
            messagebox.showerror("Error", str(e))

    def save_json(self):
        if not self.last_info:
            messagebox.showerror("No data", "Fetch info first.")
            return
        out_path = Path(__file__).resolve().parent / "system_info.json"
        out_path.write_text(json.dumps(self.last_info, indent=2), encoding="utf-8")
        messagebox.showinfo("Saved", f"Saved to:\n{out_path}")


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()

