


from __future__ import annotations

import json
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, scrolledtext
from datetime import datetime, timezone


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(cmd: list[str]) -> tuple[int, str, str]:
    p = subprocess.run(cmd, capture_output=True, text=True, shell=False)
    return p.returncode, p.stdout or "", p.stderr or ""


def get_gateway_and_ips() -> dict:
    code, out, err = run_cmd(["ipconfig"])
    # best effort: parse gateway and IPv4 by looking for keywords
    # If parsing fails, we still return whatever we can.
    gateway = ""
    ips: list[str] = []

    if code != 0:
        return {"gateway": gateway, "ips": ips, "error": err.strip() or "ipconfig failed"}

    lines = out.splitlines()
    for ln in lines:
        s = ln.strip()
        low = s.lower()
        # "Default Gateway . . . . : 192.168.1.1"
        if "default gateway" in low or "gateway" in low and ":" in s:
            parts = s.split(":", 1)
            if len(parts) == 2 and parts[1].strip():
                gateway = parts[1].strip()

        # collect ipv4 lines
        if ("ipv4 address" in low) and ":" in s:
            parts = s.split(":", 1)
            if len(parts) == 2:
                val = parts[1].strip()
                if val and val.count(".") == 3:
                    ips.append(val)

        # fallback for older localized output: line ends with an ip
        if (low.startswith("ipv4") or "ipv4" in low) and ":" in s:
            parts = s.split(":", 1)
            if len(parts) == 2:
                val = parts[1].strip()
                if val and val.count(".") == 3:
                    ips.append(val)

    # de-dupe ips
    ips2 = []
    seen = set()
    for ip in ips:
        if ip in seen:
            continue
        seen.add(ip)
        ips2.append(ip)

    return {"gateway": gateway or "(not found)", "ips": ips2, "error": ""}


def get_arp() -> list[dict[str, str]]:
    code, out, err = run_cmd(["arp", "-a"])
    if code != 0:
        return [{"ip": "(arp failed)", "mac": "", "type": err.strip() or ""}]

    devices: list[dict[str, str]] = []
    for line in out.splitlines():
        s = line.strip()
        if not s:
            continue
        # Windows format example:
        #  192.168.1.10           aa-bb-cc-dd-ee-ff     dynamic
        if s[0].isdigit() and "-" in s:
            parts = s.split()
            if len(parts) >= 3 and parts[0].count(".") == 3 and ("-" in parts[1] or ":" in parts[1]):
                ip = parts[0]
                mac = parts[1].replace(":", "-")
                typ = parts[2] if len(parts) > 2 else ""
                devices.append({"ip": ip, "mac": mac, "type": typ})

    # de-dupe
    out2 = []
    seen = set()
    for d in devices:
        k = (d["ip"], d["mac"].lower())
        if k in seen:
            continue
        seen.add(k)
        out2.append(d)

    return out2


def collect() -> dict:
    g = get_gateway_and_ips()
    return {
        "generated_utc": utc_now(),
        "gateway": g.get("gateway", "(not found)"),
        "ips": g.get("ips", []),
        "arp": get_arp(),
    }


def format_text(data: dict) -> str:
    lines: list[str] = []
    lines.append("NETWORK SNAPSHOT")
    lines.append(f"UTC: {data.get('generated_utc','')}")
    lines.append("")

    lines.append("DEFAULT GATEWAY")
    lines.append(str(data.get("gateway", "(not found)")))
    lines.append("")

    lines.append("LOCAL IPv4")
    ips = data.get("ips", [])
    if not ips:
        lines.append("(none found)")
    else:
        for ip in ips:
            lines.append(f"- {ip}")

    lines.append("")
    lines.append("ARP (local devices)")
    arp = data.get("arp", [])
    if not arp:
        lines.append("(no entries)")
    else:
        for d in arp:
            lines.append(f"- {d.get('ip','')}  {d.get('mac','')}  {d.get('type','')}")

    return "\n".join(lines)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Network Connections (Simple)")
        self.geometry("900x650")

        self.last = None

        self.text = scrolledtext.ScrolledText(self, wrap=tk.WORD)
        self.text.pack(fill="both", expand=True, padx=10, pady=10)

        frm = tk.Frame(self)
        frm.pack(fill="x", padx=10, pady=(0, 10))

        tk.Button(frm, text="Refresh", command=self.refresh).pack(side="left")
        tk.Button(frm, text="Save JSON", command=self.save_json).pack(side="left", padx=(10, 0))

        self.refresh()

    def refresh(self):
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, "Fetching...\n")
        self.update_idletasks()

        try:
            data = collect()
            self.last = data
            self.text.delete("1.0", tk.END)
            self.text.insert(tk.END, format_text(data))
        except Exception as e:
            self.text.delete("1.0", tk.END)
            self.text.insert(tk.END, f"ERROR: {e}\n")
            messagebox.showerror("Error", str(e))

    def save_json(self):
        if not self.last:
            messagebox.showerror("No data", "Refresh first.")
            return
        out_path = Path(__file__).resolve().parent / "network_info.json"
        out_path.write_text(json.dumps(self.last, indent=2), encoding="utf-8")
        messagebox.showinfo("Saved", f"Saved to:\n{out_path}")


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()

