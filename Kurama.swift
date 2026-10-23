import AppKit
import Foundation

private let root = URL(fileURLWithPath: NSHomeDirectory())
    .appendingPathComponent("Library/Application Support/KuramaTerminal", isDirectory: true)
private let commandFile = root.appendingPathComponent("command")
private let pidFile = root.appendingPathComponent("pid")
private let positionFile = root.appendingPathComponent("position")

final class PetView: NSView {
    var images: [String: NSImage] = [:]
    var pose = "idle"
    var tick = 0.0
    var dragStart: NSPoint?

    override var isOpaque: Bool { false }

    override func draw(_ dirtyRect: NSRect) {
        guard let image = images[pose == "goodbye" ? "wave" : pose] ?? images["idle"], let context = NSGraphicsContext.current?.cgContext else { return }
        let bob = pose == "idle" ? sin(tick * 2.2) * 2.0 : 0.0
        let tilt = pose == "wave" || pose == "goodbye" ? sin(tick * 13.0) * 0.045 : 0.0
        context.saveGState()
        context.translateBy(x: 90, y: 100 + bob)
        context.rotate(by: tilt)
        image.draw(in: NSRect(x: -84, y: -90, width: 168, height: 180),
                   from: .zero, operation: .sourceOver, fraction: 1)
        context.restoreGState()
        if pose == "goodbye" {
            let bubble = NSRect(x: 166, y: 135, width: 69, height: 34)
            NSColor(calibratedRed: 1, green: 0.96, blue: 0.88, alpha: 0.96).setFill()
            NSBezierPath(roundedRect: bubble, xRadius: 12, yRadius: 12).fill()
            let style: [NSAttributedString.Key: Any] = [
                .font: NSFont.boldSystemFont(ofSize: 15),
                .foregroundColor: NSColor(calibratedRed: 0.48, green: 0.12, blue: 0.05, alpha: 1)
            ]
            ("Bye!" as NSString).draw(at: NSPoint(x: 182, y: 143), withAttributes: style)
        }
    }

    override func mouseDown(with event: NSEvent) {
        dragStart = event.locationInWindow
    }

    override func mouseDragged(with event: NSEvent) {
        guard let start = dragStart, let window = window else { return }
        let point = window.convertPoint(toScreen: event.locationInWindow)
        window.setFrameOrigin(NSPoint(x: point.x - start.x, y: point.y - start.y))
    }

    override func mouseUp(with event: NSEvent) {
        guard let origin = window?.frame.origin else { return }
        try? "\(origin.x),\(origin.y)".write(to: positionFile, atomically: true, encoding: .utf8)
    }
}

final class PetApp: NSObject, NSApplicationDelegate {
    private var window: NSWindow!
    private var pet: PetView!
    private var lastCommand = ""
    private var nextBlink = Date().addingTimeInterval(Double.random(in: 1.0...2.0))
    private var nextHeadTilt = Date().addingTimeInterval(5)
    private var tiltToFirstSide = true
    private var poseUntil: Date?
    private var privateMode = false
    private var quitting = false
    private var lastTick = Date()

    func applicationDidFinishLaunching(_ notification: Notification) {
        try? FileManager.default.createDirectory(at: root, withIntermediateDirectories: true)
        try? String(ProcessInfo.processInfo.processIdentifier).write(to: pidFile, atomically: true, encoding: .utf8)

        let frame = NSRect(x: 0, y: 0, width: 245, height: 205)
        window = NSWindow(contentRect: frame, styleMask: [.borderless], backing: .buffered, defer: false)
        window.isOpaque = false
        window.backgroundColor = .clear
        window.hasShadow = false
        window.level = .floating
        window.collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary]
        window.isMovableByWindowBackground = false
        pet = PetView(frame: frame)
        let assetRoot = URL(fileURLWithPath: CommandLine.arguments[0]).deletingLastPathComponent().appendingPathComponent("assets")
        for name in ["idle", "blink", "tilt", "tilt_opposite", "privacy", "wave"] {
            pet.images[name] = NSImage(contentsOf: assetRoot.appendingPathComponent("\(name).png"))
        }
        window.contentView = pet
        if let screen = NSScreen.main?.visibleFrame {
            var point = NSPoint(x: screen.maxX - 270, y: screen.minY + 25)
            if let saved = try? String(contentsOf: positionFile, encoding: .utf8) {
                let values = saved.split(separator: ",").compactMap { Double($0) }
                if values.count == 2 {
                    let candidate = NSPoint(x: values[0], y: values[1])
                    if screen.intersects(NSRect(origin: candidate, size: frame.size)) { point = candidate }
                }
            }
            window.setFrameOrigin(point)
        }
        let menu = NSMenu()
        let privacy = NSMenuItem(title: "Cover eyes", action: #selector(togglePrivacy), keyEquivalent: "")
        privacy.target = self
        menu.addItem(privacy)
        let wave = NSMenuItem(title: "Wave", action: #selector(wave), keyEquivalent: "")
        wave.target = self
        menu.addItem(wave)
        menu.addItem(.separator())
        let quit = NSMenuItem(title: "Say goodbye", action: #selector(quit), keyEquivalent: "")
        quit.target = self
        menu.addItem(quit)
        pet.menu = menu
        window.orderFrontRegardless()
        Timer.scheduledTimer(timeInterval: 0.05, target: self, selector: #selector(update), userInfo: nil, repeats: true)
    }

    func applicationWillTerminate(_ notification: Notification) {
        try? FileManager.default.removeItem(at: pidFile)
    }

    @objc private func togglePrivacy() {
        privateMode.toggle()
        if !privateMode { nextHeadTilt = Date().addingTimeInterval(5) }
        show(privateMode ? "privacy" : "idle")
    }
    @objc private func wave() { show("wave", for: 2) }
    @objc private func quit() {
        guard !quitting else { return }
        quitting = true
        show("goodbye")
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.8) { NSApp.terminate(nil) }
    }

    private func show(_ pose: String, for seconds: TimeInterval? = nil) {
        pet.pose = pose
        poseUntil = seconds.map { Date().addingTimeInterval($0) }
        pet.needsDisplay = true
    }

    @objc private func update() {
        let now = Date()
        pet.tick += now.timeIntervalSince(lastTick)
        lastTick = now
        if let raw = try? String(contentsOf: commandFile, encoding: .utf8), raw != lastCommand {
            lastCommand = raw
            switch raw.split(separator: " ").first.map(String.init) {
            case "privacy-on": privateMode = true; show("privacy")
            case "privacy-off": privateMode = false; nextHeadTilt = now.addingTimeInterval(5); show("idle")
            case "wave": if !privateMode { show("wave", for: 2) }
            case "quit": quit()
            default: break
            }
        }
        if !quitting && !privateMode {
            if let until = poseUntil, now >= until { show("idle") }
            if now >= nextHeadTilt && pet.pose == "idle" {
                show(tiltToFirstSide ? "tilt" : "tilt_opposite", for: 0.8)
                tiltToFirstSide.toggle()
                nextHeadTilt = now.addingTimeInterval(5)
            }
            if now >= nextBlink && pet.pose == "idle" {
                show("blink", for: 0.18)
                nextBlink = now.addingTimeInterval(Double.random(in: 1.0...2.0))
            }
        }
        pet.needsDisplay = true
    }
}

let app = NSApplication.shared
app.setActivationPolicy(.accessory)
let delegate = PetApp()
app.delegate = delegate
app.run()
