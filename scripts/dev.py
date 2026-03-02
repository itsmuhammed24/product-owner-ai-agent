#!/usr/bin/env python3
"""Lance API + UI en une seule commande. Ctrl+C arrête tout."""

import os
import signal
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    os.chdir(ROOT)
    venv_python = os.path.join(ROOT, ".venv", "bin", "python")
    python = venv_python if os.path.isfile(venv_python) else sys.executable

    print("PO Agent — démarrage API + UI")
    print("   API : http://localhost:8000")
    print("   UI  : http://localhost:5173")
    print("   Ctrl+C pour arrêter\n")

    api = subprocess.Popen(
        [
            python,
            "-m",
            "uvicorn",
            "apps.api.main:app",
            "--reload",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
        ],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )

    def cleanup():
        api.terminate()
        api.wait(timeout=3)

    signal.signal(signal.SIGINT, lambda *_: (cleanup(), sys.exit(0)))
    signal.signal(signal.SIGTERM, lambda *_: (cleanup(), sys.exit(0)))

    try:
        subprocess.run(["npm", "run", "dev"], cwd=os.path.join(ROOT, "apps", "web"), check=False)
    finally:
        cleanup()


if __name__ == "__main__":
    main()
