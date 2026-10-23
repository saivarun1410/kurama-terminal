#!/usr/bin/env python3
"""Create a Spotlight-searchable native Kurama launcher in ~/Applications."""
from pathlib import Path
from tempfile import TemporaryDirectory
import plistlib
import shutil
import subprocess

from PIL import Image

root = Path(__file__).resolve().parent
command = Path.home() / "Library" / "Application Support" / "KuramaTerminal" / "runtime" / "kurama"
destination = Path.home() / "Applications" / "Kurama.app"
if not command.is_file():
    raise SystemExit("Run python3 install-launch-agent.py first")

destination.parent.mkdir(parents=True, exist_ok=True)
with TemporaryDirectory(prefix="kurama-launcher-") as temp:
    temp = Path(temp)
    app = temp / "Kurama.app"
    macos = app / "Contents" / "MacOS"
    resources = app / "Contents" / "Resources"
    macos.mkdir(parents=True)
    resources.mkdir()
    subprocess.run(["swiftc", str(root / "Launcher.swift"), "-o", str(macos / "KuramaLauncher")], check=True)
    info = {
        "CFBundleDevelopmentRegion": "en",
        "CFBundleDisplayName": "Kurama",
        "CFBundleExecutable": "KuramaLauncher",
        "CFBundleIconFile": "Kurama",
        "CFBundleIdentifier": "dev.varun.kurama.launcher",
        "CFBundleInfoDictionaryVersion": "6.0",
        "CFBundleName": "Kurama",
        "CFBundlePackageType": "APPL",
        "CFBundleShortVersionString": "1.0",
        "CFBundleVersion": "1",
        "LSUIElement": True,
    }
    with (app / "Contents" / "Info.plist").open("wb") as stream:
        plistlib.dump(info, stream)

    iconset = temp / "Kurama.iconset"
    iconset.mkdir()
    source = Image.open(root / "assets" / "idle.png").convert("RGBA")
    for logical in (16, 32, 128, 256, 512):
        for scale in (1, 2):
            size = logical * scale
            canvas = Image.new("RGBA", (size, size))
            sprite = source.copy()
            sprite.thumbnail((int(size * 0.88), int(size * 0.88)), Image.Resampling.LANCZOS)
            canvas.alpha_composite(sprite, ((size - sprite.width) // 2, (size - sprite.height) // 2))
            suffix = "@2x" if scale == 2 else ""
            canvas.save(iconset / f"icon_{logical}x{logical}{suffix}.png")
    icon = temp / "Kurama.icns"
    subprocess.run(["iconutil", "-c", "icns", "-o", str(icon), str(iconset)], check=True)
    shutil.copy2(icon, resources / "Kurama.icns")
    (resources / "kurama-path.txt").write_text(str(command))
    (resources / "kurama-launcher.txt").write_text(str(command))

    if destination.exists():
        marker = destination / "Contents" / "Resources" / "kurama-launcher.txt"
        if not marker.exists():
            raise SystemExit(f"Refusing to replace existing app: {destination}")
        shutil.rmtree(destination)
    shutil.copytree(app, destination)

print(f"Installed {destination}")
