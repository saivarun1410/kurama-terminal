#!/usr/bin/env python3
"""Install Kurama as a user launch agent so it survives shell exits."""
from pathlib import Path
import os
import plistlib
import shutil
import subprocess
import time

root = Path(__file__).resolve().parent
source_binary = root / "kurama-app"
if not source_binary.is_file():
    raise SystemExit("Run ./build.sh first")
runtime = Path.home() / "Library" / "Application Support" / "KuramaTerminal" / "runtime"
runtime.mkdir(parents=True, exist_ok=True)
shutil.copy2(source_binary, runtime / "kurama-app")
shutil.copy2(root / "kurama", runtime / "kurama")
shutil.copytree(root / "assets", runtime / "assets", dirs_exist_ok=True)
binary = runtime / "kurama-app"

label = "dev.varun.kurama-terminal"
destination = Path.home() / "Library" / "LaunchAgents" / f"{label}.plist"
destination.parent.mkdir(parents=True, exist_ok=True)
data = {
    "Label": label,
    "ProgramArguments": [str(binary)],
    "RunAtLoad": True,
    "KeepAlive": False,
    "ProcessType": "Interactive",
}
with destination.open("wb") as stream:
    plistlib.dump(data, stream)

service = f"gui/{os.getuid()}/{label}"
subprocess.run(["launchctl", "bootout", service], capture_output=True)
for attempt in range(10):
    result = subprocess.run(
        ["launchctl", "bootstrap", f"gui/{os.getuid()}", str(destination)],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        break
    if attempt == 9:
        raise SystemExit(result.stderr.strip() or "Could not start Kurama launch agent")
    time.sleep(0.5)
print(f"Installed and started {destination}")
