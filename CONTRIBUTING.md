# Contributing to Kurama Terminal

Thanks for improving the pet. Bug reports, accessibility fixes, macOS compatibility work, and new expressions are welcome.

## Before opening a pull request

1. Open an issue for larger changes so the behavior and scope can be discussed.
2. Fork the repository and create a focused branch from `main`.
3. Keep the app lightweight and avoid reading keystrokes, passwords, or terminal output.
4. Include art provenance and permission details for any new sprite or preview. See [ASSET_POLICY.md](ASSET_POLICY.md).
5. Run the relevant checks:

   ```zsh
   ./build.sh
   node --check bin/kurama.mjs
   npm pack --dry-run
   ```

6. Explain what changed, why, and how you checked it. Add before and after images for visual changes.

Do not commit compiled binaries, credentials, personal terminal captures, or files from `~/Library/Application Support/KuramaTerminal`.

## Pull requests and merges

Anyone may open a pull request. The repository owner, [@saivarun1410](https://github.com/saivarun1410), reviews and merges accepted pull requests. Contributors should leave their PRs open for the owner and should not request write access to merge them. The `main` branch requires a pull request for changes.

Be respectful and specific in issues and reviews. Critique the work, avoid personal attacks, and keep discussions relevant to the project.
