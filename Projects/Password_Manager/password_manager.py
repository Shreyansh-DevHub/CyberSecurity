import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

import cryptography.fernet as fernet

from pathlib import Path

# Store key/data files next to this script
_BASE_DIR = Path(__file__).resolve().parent
KEY_FILE = _BASE_DIR / "key_fixed.txt"
DATA_FILE = _BASE_DIR / "data.txt"


secure_pass = "password123"


def load_or_create_key() -> bytes:
    try:
        with open(KEY_FILE, "rb") as f:
            key = f.read().strip()
            if key:
                return key
    except FileNotFoundError:
        pass

    # This should rarely happen because you already have key_fixed.txt.
    key = fernet.Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    return key


def decrypt_entries(cipher: fernet.Fernet, raw: bytes) -> list[str]:
    tokens = [line.strip() for line in raw.splitlines() if line.strip()]
    results: list[str] = []
    for token in tokens:
        results.append(cipher.decrypt(token).decode("utf-8"))
    return results


def encrypt_entry(cipher: fernet.Fernet, entry: str) -> bytes:
    return cipher.encrypt(entry.encode("utf-8"))


class PasswordManagerGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Password Manager (Fernet)")
        self.root.geometry("720x520")

        self.cipher = fernet.Fernet(load_or_create_key())

        self._build_ui()

    def _build_ui(self) -> None:
        frm = tk.Frame(self.root, padx=12, pady=12)
        frm.pack(fill="both", expand=True)

        # Save section
        save_frame = tk.LabelFrame(frm, text="Save a password", padx=10, pady=10)
        save_frame.pack(fill="x", pady=(0, 12))

        tk.Label(save_frame, text="Website:").grid(row=0, column=0, sticky="w")
        self.website_var = tk.StringVar()
        tk.Entry(save_frame, textvariable=self.website_var, width=40).grid(
            row=0, column=1, padx=(8, 0), pady=6, sticky="ew"
        )

        tk.Label(save_frame, text="Password:").grid(row=1, column=0, sticky="w")
        self.password_var = tk.StringVar()
        tk.Entry(
            save_frame,
            textvariable=self.password_var,
            width=40,
            show="*",
        ).grid(row=1, column=1, padx=(8, 0), pady=6, sticky="ew")

        save_btn = tk.Button(save_frame, text="Save", command=self.on_save)
        save_btn.grid(row=2, column=1, sticky="e", pady=(8, 0))

        save_frame.columnconfigure(1, weight=1)

        # View section
        view_frame = tk.LabelFrame(frm, text="View saved passwords", padx=10, pady=10)
        view_frame.pack(fill="both", expand=True)

        btns = tk.Frame(view_frame)
        btns.pack(fill="x")

        tk.Button(btns, text="View", command=self.on_view).pack(side="left")
        tk.Button(btns, text="Clear", command=self.on_clear).pack(side="left", padx=10)
        tk.Button(btns, text="Reset", command=self.on_reset).pack(side="left", padx=10)


        self.output = ScrolledText(view_frame, height=18, wrap="word")
        self.output.pack(fill="both", expand=True, pady=(10, 0))
        self.output.configure(state="disabled")

    def _set_output(self, text: str) -> None:
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("1.0", text)
        self.output.configure(state="disabled")

    def on_clear(self) -> None:
        self._set_output("")

    def on_reset(self) -> None:
        confirm = messagebox.askyesno(
            "Reset data?",
            "This will permanently clear data.txt (all saved passwords). Continue?",
        )
        if not confirm:
            return

        try:
            DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
            # Truncate file to empty (create if missing)
            with open(DATA_FILE, "wb") as f:
                f.truncate(0)
            self._set_output("")
            messagebox.showinfo("Reset complete", "data.txt has been cleared.")
        except Exception as e:
            messagebox.showerror("Reset failed", f"Could not reset data.txt: {e}")


    def on_save(self) -> None:
        website = self.website_var.get().strip()
        password = self.password_var.get().strip()

        if not website or not password:
            messagebox.showwarning("Missing info", "Please enter both website and password.")
            return

        entry = f"{website}:{password}"

        try:
            encrypted = encrypt_entry(self.cipher, entry)
            with open(DATA_FILE, "ab") as f:
                f.write(encrypted + b"\n")
        except Exception as e:
            messagebox.showerror("Save failed", f"Error saving data: {e}")
            return

        messagebox.showinfo("Saved", "Data saved successfully!")
        self.password_var.set("")
        self.website_var.set("")

    def on_view(self) -> None:
        # prompt for secure password
        dialog = tk.Toplevel(self.root)
        dialog.title("Secure access")
        dialog.geometry("420x150")
        dialog.grab_set()

        tk.Label(dialog, text="Enter secure password to continue:").pack(padx=14, pady=(16, 8))

        secure_var = tk.StringVar()
        entry = tk.Entry(dialog, textvariable=secure_var, show="*")
        entry.pack(padx=14, fill="x")
        entry.focus_set()

        def do_check():
            secure_input = secure_var.get().strip()
            if secure_input != secure_pass:
                messagebox.showerror("Access denied", "Incorrect password. Access denied.")
                dialog.destroy()
                return

            try:
                with open(DATA_FILE, "rb") as f:
                    raw = f.read()
            except FileNotFoundError:
                messagebox.showwarning("No data", "No saved data yet (data.txt not found).")
                dialog.destroy()
                return
            
            try:
                decrypted_entries = decrypt_entries(self.cipher, raw)
            except Exception as e:
                messagebox.showerror(
                    "Decrypt failed",
                    "Could not decrypt existing data.\n"
                    f"Error: {e}\n"
                    "If data.txt was created with the old code, reset data.txt to start fresh.",
                )
                dialog.destroy()
                return

            text = "access granted.\n\n" + "\n".join(decrypted_entries) if decrypted_entries else "No entries found."
            self._set_output(text)
            dialog.destroy()

        tk.Button(dialog, text="Continue", command=do_check).pack(padx=14, pady=(12, 0), anchor="e")
        tk.Button(dialog, text="Cancel", command=dialog.destroy).pack(padx=14, pady=(6, 10), anchor="e")


def main() -> None:
    root = tk.Tk()
    app = PasswordManagerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

