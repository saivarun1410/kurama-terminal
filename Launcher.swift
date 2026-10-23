import Foundation

let resources = Bundle.main.resourceURL!
let pathFile = resources.appendingPathComponent("kurama-path.txt")
guard let command = try? String(contentsOf: pathFile, encoding: .utf8).trimmingCharacters(in: .whitespacesAndNewlines),
      !command.isEmpty else { exit(1) }

let process = Process()
process.executableURL = URL(fileURLWithPath: "/bin/zsh")
process.arguments = [command, "start"]
do {
    try process.run()
    process.waitUntilExit()
    exit(process.terminationStatus)
} catch {
    exit(1)
}
