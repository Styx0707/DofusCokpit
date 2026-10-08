"""Dofus Cockpit — launcher / panneau de contrôle (packagé en .exe).

Orchestre la stack sans taper de commandes :
  1) démarre la base + l'API (docker compose up -d db api) ;
  2) lance la capture réseau (dumpcap, ring-buffer) vers data/live ;
  3) ouvre l'app dans le navigateur.

⚠️ Pré-requis (NON embarqués, trop lourds) : Docker Desktop et Wireshark
(dumpcap) installés. L'exe doit être placé À LA RACINE du projet (à côté de
docker-compose.yml) : il détecte le dossier projet via son propre emplacement.

Build : voir scripts/build_exe.ps1  (pyinstaller --onefile --noconsole).
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import threading
import time
import tkinter as tk
import urllib.request
from tkinter import ttk

APP_URL = "http://localhost:8000/ui/"
HEALTH_URL = "http://localhost:8000/health"
WIRESHARK_PATHS = [
    r"C:\Program Files\Wireshark\dumpcap.exe",
    r"C:\Program Files (x86)\Wireshark\dumpcap.exe",
]
NO_WINDOW = 0x08000000  # CREATE_NO_WINDOW : pas de fenêtre console parasite


def project_dir() -> str:
    base = sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__)
    return os.path.dirname(base)


ROOT = project_dir()
LIVE_DIR = os.path.join(ROOT, "data", "live")
CAP_FILE = os.path.join(LIVE_DIR, "dofus.pcapng")


def _run(cmd: list[str], timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                          timeout=timeout, creationflags=NO_WINDOW)


def find_dumpcap() -> str | None:
    for p in WIRESHARK_PATHS:
        if os.path.exists(p):
            return p
    return None


def list_interfaces(dumpcap: str) -> list[str]:
    try:
        out = _run([dumpcap, "-D"], timeout=20).stdout
    except Exception:
        return []
    names = []
    for line in out.splitlines():
        # format "N. \Device\NPF_{..} (Ethernet)"  -> on garde le libellé lisible
        m = re.match(r"\s*\d+\.\s+(\S+)(?:\s+\((.+)\))?", line)
        if m:
            names.append(m.group(2) or m.group(1))
    return names


class App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.cap_proc: subprocess.Popen | None = None
        self.dumpcap = find_dumpcap()

        root.title("Dofus Cockpit — Launcher")
        root.geometry("640x470")
        root.minsize(560, 420)

        top = ttk.Frame(root, padding=12)
        top.pack(fill="x")
        ttk.Label(top, text="🎛️  Dofus Cockpit", font=("Segoe UI", 15, "bold")).pack(side="left")
        self.api_dot = ttk.Label(top, text="● API ?", foreground="#888")
        self.api_dot.pack(side="right")
        self.cap_dot = ttk.Label(top, text="● Capture ?", foreground="#888")
        self.cap_dot.pack(side="right", padx=(0, 14))

        body = ttk.Frame(root, padding=(12, 0, 12, 12))
        body.pack(fill="both", expand=True)

        row1 = ttk.Frame(body); row1.pack(fill="x", pady=4)
        ttk.Button(row1, text="1 ▶  Démarrer DB + API", command=self.start_stack).pack(side="left")
        ttk.Button(row1, text="🌐  Ouvrir l'app", command=self.open_app).pack(side="left", padx=6)
        ttk.Button(row1, text="⏹  Tout arrêter", command=self.stop_all).pack(side="right")

        row2 = ttk.Frame(body); row2.pack(fill="x", pady=4)
        ttk.Label(row2, text="Interface :").pack(side="left")
        self.iface = ttk.Combobox(row2, state="readonly", width=30)
        self.iface.pack(side="left", padx=6)
        self.cap_btn = ttk.Button(row2, text="2 ⏺  Lancer capture", command=self.toggle_capture)
        self.cap_btn.pack(side="left")

        self.log = tk.Text(body, height=16, wrap="word", font=("Consolas", 9))
        self.log.pack(fill="both", expand=True, pady=(8, 0))
        self.log.configure(state="disabled")

        self._init_ifaces()
        self.logln(f"Projet : {ROOT}")
        if not self.dumpcap:
            self.logln("⚠️ dumpcap introuvable — installe Wireshark (capture indisponible).")
        threading.Thread(target=self._health_loop, daemon=True).start()
        root.protocol("WM_DELETE_WINDOW", self._on_close)

    # --- utils UI ---
    def logln(self, msg: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", msg.rstrip() + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _init_ifaces(self) -> None:
        names = list_interfaces(self.dumpcap) if self.dumpcap else []
        self.iface["values"] = names
        if names:
            pick = next((n for n in names if "ethernet" in n.lower()), None) \
                or next((n for n in names if "wi" in n.lower()), names[0])
            self.iface.set(pick)

    # --- actions ---
    def start_stack(self) -> None:
        def task():
            os.makedirs(LIVE_DIR, exist_ok=True)
            self.logln("→ docker compose up -d db api …")
            try:
                r = _run(["docker", "compose", "up", "-d", "db", "api"], timeout=300)
                self.logln(r.stdout.strip() or "")
                self.logln(r.stderr.strip() or "")
                self.logln("✔ Stack démarrée." if r.returncode == 0 else "✖ Échec (Docker Desktop lancé ?).")
            except FileNotFoundError:
                self.logln("✖ 'docker' introuvable — installe/lance Docker Desktop.")
            except Exception as e:
                self.logln(f"✖ {e}")
        threading.Thread(target=task, daemon=True).start()

    def toggle_capture(self) -> None:
        if self.cap_proc and self.cap_proc.poll() is None:
            self.cap_proc.terminate()
            self.cap_proc = None
            self.cap_btn.config(text="2 ⏺  Lancer capture")
            self.logln("⏹ Capture arrêtée.")
            return
        if not self.dumpcap:
            self.logln("✖ dumpcap introuvable (Wireshark).")
            return
        iface = self.iface.get()
        if not iface:
            self.logln("✖ Choisis une interface réseau.")
            return
        os.makedirs(LIVE_DIR, exist_ok=True)
        cmd = [self.dumpcap, "-i", iface, "-f", "tcp port 443",
               "-b", "duration:5", "-b", "files:50", "-w", CAP_FILE]
        try:
            self.cap_proc = subprocess.Popen(cmd, cwd=ROOT, creationflags=NO_WINDOW)
            self.cap_btn.config(text="2 ⏹  Stop capture")
            self.logln(f"⏺ Capture sur « {iface} » → data/live/ (ring 50×5 s).")
            self.logln("   Ouvre ta banque / l'hôtel de vente en jeu : MAJ auto en ~10 s.")
        except Exception as e:
            self.logln(f"✖ capture: {e}")

    def open_app(self) -> None:
        import webbrowser
        webbrowser.open(APP_URL)

    def stop_all(self) -> None:
        if self.cap_proc and self.cap_proc.poll() is None:
            self.cap_proc.terminate()
            self.cap_proc = None
            self.cap_btn.config(text="2 ⏺  Lancer capture")
        def task():
            self.logln("→ docker compose stop …")
            try:
                _run(["docker", "compose", "stop"], timeout=120)
                self.logln("✔ Stack arrêtée.")
            except Exception as e:
                self.logln(f"✖ {e}")
        threading.Thread(target=task, daemon=True).start()

    # --- statut live ---
    def _health_loop(self) -> None:
        while True:
            up = False
            try:
                with urllib.request.urlopen(HEALTH_URL, timeout=2) as r:
                    up = r.status == 200
            except Exception:
                up = False
            cap = bool(self.cap_proc and self.cap_proc.poll() is None)
            self.root.after(0, lambda u=up, c=cap: self._set_dots(u, c))
            time.sleep(3)

    def _set_dots(self, up: bool, cap: bool) -> None:
        self.api_dot.config(text="● API " + ("OK" if up else "down"),
                            foreground="#0ca30c" if up else "#c0392b")
        self.cap_dot.config(text="● Capture " + ("ON" if cap else "off"),
                            foreground="#0ca30c" if cap else "#888")

    def _on_close(self) -> None:
        try:
            if self.cap_proc and self.cap_proc.poll() is None:
                self.cap_proc.terminate()
        finally:
            self.root.destroy()


def main() -> None:
    root = tk.Tk()
    try:
        ttk.Style().theme_use("vista")
    except Exception:
        pass
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
