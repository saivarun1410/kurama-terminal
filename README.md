# Kurama terminal companion

![Kurama beside a terminal](docs/previews/terminal-hero.png)

A draggable, animated macOS Kurama that floats beside your terminal. It blinks every 1–2 seconds, alternates left and right head tilts about every 5 seconds, covers its eyes in privacy mode, and waves with a goodbye bubble when closed. Right click the pet for controls. Its position is remembered.

## Screenshots and animation

These are staged terminal previews using the same Kurama sprites shipped with the app. No personal desktop or terminal data appears in them.

![Animated preview of Kurama blinking, tilting, covering its eyes, and waving](docs/previews/kurama-in-action.gif)

### Every expression

![Six Kurama expressions: idle, blink, left tilt, right tilt, privacy, and goodbye](docs/previews/expression-gallery.png)

| Privacy mode | Goodbye wave |
| --- | --- |
| ![Kurama covers its eyes beside a password prompt](docs/previews/privacy-mode.png) | ![Kurama waves goodbye after quitting](docs/previews/goodbye-wave.png) |

## Install on macOS

```zsh
git clone https://github.com/saivarun1410/kurama-terminal.git
cd kurama-terminal
python3 -m pip install -r requirements.txt
./build.sh
python3 install-launch-agent.py
python3 install-launcher.py
./kurama start
```

To control Kurama:

```zsh
./kurama privacy on
./kurama privacy off
./kurama wave
./kurama quit
```

## Easy ways to launch

- Press **Command–Space**, type **Kurama**, and press Return. The launcher lives in `~/Applications/Kurama.app`.
- Open **Kurama** from your Applications folder, or drag it to the Dock.
- In a new terminal, type `kurama` or `kurama start`.
- Kurama starts automatically at login through its user launch agent.

The installer copies the runtime to `~/Library/Application Support/KuramaTerminal/runtime`, so the clickable app can launch without requesting access to your Documents folder.

This is an unofficial fan project. The character artwork was adapted from a user supplied reference image; no ownership of the Naruto character is claimed.

For every new zsh session, add this line to `~/.zshrc`:

```zsh
source /absolute/path/to/kurama-terminal/shell-integration.zsh
```

The install script also adds a user launch agent, so the pet starts at login and survives shell exits. It can be removed with `launchctl bootout gui/$(id -u)/dev.varun.kurama-terminal`; remove the matching `.plist` in `~/Library/LaunchAgents` and the source line in `~/.zshrc` to disable startup permanently.

The shell hook covers Kurama's eyes while commands starting with `sudo`, `ssh`, `sftp`, `scp`, `gpg`, `pass`, `op`, `security`, or `read -s` run. It never reads keystrokes or captures terminal text. Other password prompts cannot be detected reliably; use `kurama privacy on` before those and `kurama privacy off` afterward. The pet waves when a shell exits. `kurama quit` waves and closes it.

## More expression ideas

- Sleep after long inactivity, wake on a new command.
- Proud grin after a successful build and a worried face after a failed one.
- Tails wag for long running commands, with no command text shown.
- Tiny chakra glow on successful tests.
- Per-terminal positioning if Accessibility permission is explicitly granted.

The current version keeps animation gentle and does not need Accessibility permission.
