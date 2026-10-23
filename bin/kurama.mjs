#!/usr/bin/env node
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const packageRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const packageVersion = JSON.parse(fs.readFileSync(path.join(packageRoot, 'package.json'), 'utf8')).version;
const support = path.join(os.homedir(), 'Library', 'Application Support', 'KuramaTerminal');
const runtime = path.join(support, 'runtime');
const runtimeCommand = path.join(runtime, 'kurama');
const agentLabel = 'dev.varun.kurama-terminal';
const service = `gui/${process.getuid()}/${agentLabel}`;
const agentFile = path.join(os.homedir(), 'Library', 'LaunchAgents', `${agentLabel}.plist`);
const app = path.join(os.homedir(), 'Applications', 'Kurama.app');
const shellHook = path.join(runtime, 'shell-integration.zsh');

function requireMac() {
  if (process.platform !== 'darwin') {
    throw new Error('Kurama currently supports macOS only.');
  }
}

function run(command, args, allowFailure = false) {
  const result = spawnSync(command, args, { encoding: 'utf8', maxBuffer: 1024 * 1024 * 4 });
  if (result.error) throw result.error;
  if (result.status !== 0 && !allowFailure) {
    throw new Error(`${command} ${args.join(' ')} failed:\n${result.stderr || result.stdout}`.trim());
  }
  return result;
}

function pause(ms) {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
}

function xml(value) {
  return value.replaceAll('&', '&amp;').replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;').replaceAll('"', '&quot;');
}

function makeAgent() {
  fs.mkdirSync(path.dirname(agentFile), { recursive: true });
  fs.writeFileSync(agentFile, `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>Label</key><string>${agentLabel}</string>
<key>ProgramArguments</key><array><string>${xml(path.join(runtime, 'kurama-app'))}</string></array>
<key>RunAtLoad</key><true/>
<key>KeepAlive</key><false/>
<key>ProcessType</key><string>Interactive</string>
</dict></plist>
`);
  run('launchctl', ['bootout', service], true);
  for (let attempt = 0; attempt < 10; attempt += 1) {
    const result = run('launchctl', ['bootstrap', `gui/${process.getuid()}`, agentFile], true);
    if (result.status === 0) return;
    if (attempt === 9) throw new Error(`Could not start launch agent: ${result.stderr.trim()}`);
    pause(500);
  }
}

function makeApp() {
  const staging = path.join(os.homedir(), 'Applications', `.Kurama-staging-${process.pid}.app`);
  const contents = path.join(staging, 'Contents');
  const macos = path.join(contents, 'MacOS');
  const resources = path.join(contents, 'Resources');
  fs.mkdirSync(macos, { recursive: true });
  fs.mkdirSync(resources, { recursive: true });
  try {
    run('swiftc', [path.join(packageRoot, 'Launcher.swift'), '-o', path.join(macos, 'KuramaLauncher')]);
    fs.copyFileSync(path.join(packageRoot, 'assets', 'Kurama.icns'), path.join(resources, 'Kurama.icns'));
    fs.writeFileSync(path.join(resources, 'kurama-path.txt'), runtimeCommand);
    fs.writeFileSync(path.join(resources, 'kurama-launcher.txt'), runtimeCommand);
    fs.writeFileSync(path.join(contents, 'Info.plist'), `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleDevelopmentRegion</key><string>en</string>
<key>CFBundleDisplayName</key><string>Kurama</string>
<key>CFBundleExecutable</key><string>KuramaLauncher</string>
<key>CFBundleIconFile</key><string>Kurama</string>
<key>CFBundleIdentifier</key><string>dev.varun.kurama.launcher</string>
<key>CFBundleInfoDictionaryVersion</key><string>6.0</string>
<key>CFBundleName</key><string>Kurama</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleShortVersionString</key><string>${packageVersion}</string>
<key>CFBundleVersion</key><string>1</string>
<key>LSUIElement</key><true/>
</dict></plist>
`);
    if (fs.existsSync(app)) {
      const marker = path.join(app, 'Contents', 'Resources', 'kurama-launcher.txt');
      if (!fs.existsSync(marker)) throw new Error(`Refusing to replace an unrelated app at ${app}`);
      fs.rmSync(app, { recursive: true });
    }
    fs.renameSync(staging, app);
  } finally {
    if (fs.existsSync(staging)) fs.rmSync(staging, { recursive: true });
  }
}

function makeShellHook() {
  const rc = path.join(os.homedir(), '.zshrc');
  const line = `source "${shellHook.replaceAll('"', '\\"')}"`;
  let body = fs.existsSync(rc) ? fs.readFileSync(rc, 'utf8') : '';
  if (body.includes(line)) return;
  body = body.replace(/^# Animated Kurama terminal companion\nsource .*\/kurama-terminal\/shell-integration\.zsh\n?/m, '');
  body = body.replace(/^# Kurama terminal companion\nsource .*\/shell-integration\.zsh\n?/m, '');
  fs.writeFileSync(rc, `${body.trimEnd()}\n\n# Kurama terminal companion\n${line}\n`);
}

function install() {
  requireMac();
  fs.mkdirSync(runtime, { recursive: true });
  run('swiftc', ['-O', '-framework', 'AppKit', path.join(packageRoot, 'Kurama.swift'), '-o', path.join(runtime, 'kurama-app')]);
  fs.copyFileSync(path.join(packageRoot, 'kurama'), runtimeCommand);
  fs.chmodSync(runtimeCommand, 0o755);
  fs.copyFileSync(path.join(packageRoot, 'shell-integration.zsh'), shellHook);
  fs.cpSync(path.join(packageRoot, 'assets'), path.join(runtime, 'assets'), { recursive: true, force: true });
  makeApp();
  makeShellHook();
  makeAgent();
  console.log('Kurama installed and started. Open Kurama from Applications or run `kurama start`.');
}

function installed() {
  return fs.existsSync(path.join(runtime, 'kurama-app')) && fs.existsSync(runtimeCommand);
}

function delegate(args) {
  const result = run(runtimeCommand, args);
  if (result.stdout) process.stdout.write(result.stdout);
  if (result.stderr) process.stderr.write(result.stderr);
}

function help() {
  console.log(`Kurama terminal companion (macOS)

Usage:
  kurama install       Build the pet and set up login, shell, and app launchers
  kurama start         Launch the pet (installs it on first run)
  kurama status        Show whether it is running
  kurama privacy on    Cover its eyes
  kurama privacy off   Return to idle
  kurama wave          Play a wave
  kurama quit          Wave goodbye and close
`);
}

try {
  const [command = 'start', ...args] = process.argv.slice(2);
  if (command === 'help' || command === '--help' || command === '-h') help();
  else if (command === 'version' || command === '--version' || command === '-v') console.log(packageVersion);
  else {
    requireMac();
    if (command === 'install') install();
    else if (command === 'start') {
      if (!installed()) install();
      else delegate(['start']);
    } else if (['status', 'wave', 'quit', 'stop'].includes(command)) {
      if (command === 'status' && !installed()) console.log('Kurama is not installed');
      else if (!installed()) throw new Error('Run `kurama install` first.');
      else delegate([command]);
    } else if (command === 'privacy' && ['on', 'off'].includes(args[0])) {
      if (!installed()) throw new Error('Run `kurama install` first.');
      delegate([command, args[0]]);
    } else {
      help();
      process.exitCode = 2;
    }
  }
} catch (error) {
  console.error(`Kurama: ${error.message}`);
  process.exitCode = 1;
}
