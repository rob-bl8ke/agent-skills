# PowerShell GitHub CLI write path

Follow this reference only when the active execution shell is PowerShell or `pwsh`.

## Preconditions

1. Confirm `gh` exists with `Get-Command gh -ErrorAction Stop`.
2. Run `gh auth status` and stop on any nonzero exit.
3. Show the complete drafted title and body in the conversation and obtain explicit user confirmation before any write.

## Rules

- Keep the approved body in memory first.
- Write the body to a unique UTF-8 temporary file with no BOM.
- Use `--body-file`; do not inline the body into the command.
- Check `$LASTEXITCODE` immediately after each native `gh` command.
- Always verify create or edit with a fresh `gh issue view` call.
- Always remove only the temporary file you created, even on failure.

## Create pattern

Assume `$issueTitle` contains the approved title, `$issueBody` the approved body, `$issueLabel` the approved type label such as `type:story`, and `$repoArgs` is either empty or the explicit repository override.

```powershell
$issueBodyFile = [System.IO.Path]::GetTempFileName()
try {
    [System.IO.File]::WriteAllText($issueBodyFile, $issueBody, [System.Text.UTF8Encoding]::new($false))

    $issueUrl = gh issue create @repoArgs --title $issueTitle --body-file $issueBodyFile --label $issueLabel
    if ($LASTEXITCODE -ne 0) { throw 'Issue creation failed; stop.' }
    if ([string]::IsNullOrWhiteSpace($issueUrl)) { throw 'No issue URL returned; stop and reconcile.' }

    $verifiedIssue = gh issue view $issueUrl.Trim() @repoArgs --json number,url,title,body
    if ($LASTEXITCODE -ne 0) { throw 'Issue verification failed; do not retry creation.' }
}
finally {
    Remove-Item -LiteralPath $issueBodyFile -ErrorAction SilentlyContinue
}
```

## Edit pattern

```powershell
$issueBodyFile = [System.IO.Path]::GetTempFileName()
try {
    [System.IO.File]::WriteAllText($issueBodyFile, $issueBody, [System.Text.UTF8Encoding]::new($false))

    gh issue edit $issueTarget @repoArgs --body-file $issueBodyFile
    if ($LASTEXITCODE -ne 0) { throw 'Issue edit failed; stop.' }

    $verifiedIssue = gh issue view $issueTarget @repoArgs --json number,url,title,body
    if ($LASTEXITCODE -ne 0) { throw 'Issue verification failed after edit; stop.' }
}
finally {
    Remove-Item -LiteralPath $issueBodyFile -ErrorAction SilentlyContinue
}
```

## Comment and close pattern

Use this when another skill needs to post a completion summary before closing an issue.

```powershell
$commentBodyFile = [System.IO.Path]::GetTempFileName()
try {
    [System.IO.File]::WriteAllText($commentBodyFile, $commentBody, [System.Text.UTF8Encoding]::new($false))

    gh issue comment $issueTarget @repoArgs --body-file $commentBodyFile
    if ($LASTEXITCODE -ne 0) { throw 'Issue comment failed; stop.' }

    gh issue close $issueTarget @repoArgs
    if ($LASTEXITCODE -ne 0) { throw 'Issue close failed; stop.' }

    $verifiedIssue = gh issue view $issueTarget @repoArgs --json number,url,title,state
    if ($LASTEXITCODE -ne 0) { throw 'Issue verification failed after close; stop.' }
}
finally {
    Remove-Item -LiteralPath $commentBodyFile -ErrorAction SilentlyContinue
}
```

## Worked example

For a draft with title in `$issueTitle`, body in `$issueBody`, and a completion summary in `$commentBody`, the lifecycle is:

1. Create or edit with the temp-file patterns above.
2. After implementation and verification, write `$commentBody` to its own temp file.
3. Post it with `gh issue comment ... --body-file`.
4. Close with `gh issue close`.
5. Verify the final state with `gh issue view --json number,url,title,state`.

## Failure handling

- If `gh auth status` fails, stop and return the draft plus the intended `gh` command shape for manual use.
- If create returns a URL but verification fails, reconcile with read-only `gh issue view` or `gh issue list` before any retry.
- If comment succeeds but close verification fails, reconcile with read-only `gh issue view` before any retry or second close attempt.
- Never claim success until the verified output confirms the issue number, URL, title, and body.

## Manual fallback shape

When writes are blocked, return the approved draft and a PowerShell-shaped command outline that makes clear the body must be written to a UTF-8 temp file and passed with `--body-file`.