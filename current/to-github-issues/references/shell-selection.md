# Shell selection for GitHub issue writes

Use this reference only when you are about to execute `gh` for create or edit. The goal is to choose one shell path and stay on it.

## Decision rule

1. Prefer the active runner or terminal configuration already provided in context.
2. If the execution tool explicitly states the shell, trust that signal over OS defaults.
3. If the environment shows multiple terminals, use the one you will actually execute in.
4. If the shell is still ambiguous, stop the write path and return the approved draft plus the manual command shape instead of guessing.

## Classification

Choose exactly one:

- **PowerShell path** when the active shell is PowerShell or `pwsh`.
- **bash/zsh path** when the active shell is `bash` or `zsh`.

## Guardrails

- Do not infer the shell from the operating system alone.
- Do not mix syntax from both paths in one command sequence.
- Do not continue to creation or edit until the shell path is explicit.

## Next step

After classification, follow exactly one reference:

- PowerShell: [github-cli-powershell.md](github-cli-powershell.md)
- bash/zsh: [github-cli-bash.md](github-cli-bash.md)