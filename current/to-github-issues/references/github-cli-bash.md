# bash/zsh GitHub CLI write path

Follow this reference only when the active execution shell is `bash` or `zsh`.

## Preconditions

1. Confirm `gh` exists with `command -v gh`.
2. Run `gh auth status` and stop on any nonzero exit.
3. Show the complete drafted title and body in the conversation and obtain explicit user confirmation before any write.

## Rules

- Keep the approved body in memory first.
- Write the body to a unique UTF-8 temporary file.
- Use `--body-file`; do not inline the body into the command.
- Use immediate exit checks after each `gh` command.
- Always verify create or edit with a fresh `gh issue view` call.
- Clean up the temporary file with a trap scoped to the subshell performing the write.

## Create pattern

Assume `issue_title` contains the approved title, `issue_body` the approved body, `issue_label` the approved type label such as `type:story`, and `repo_args` expands either to nothing or to the explicit repository override.

```bash
(
    issue_body_file=$(mktemp) || exit 1
    trap 'rm -f -- "$issue_body_file"' EXIT

    printf '%s' "$issue_body" > "$issue_body_file" || exit 1

    issue_url=$(gh issue create "${repo_args[@]}" --title "$issue_title" --body-file "$issue_body_file" --label "$issue_label") || exit 1
    [ -n "$issue_url" ] || exit 1

    verified_issue=$(gh issue view "$issue_url" "${repo_args[@]}" --json number,url,title,body) || exit 1
)
```

## Edit pattern

```bash
(
    issue_body_file=$(mktemp) || exit 1
    trap 'rm -f -- "$issue_body_file"' EXIT

    printf '%s' "$issue_body" > "$issue_body_file" || exit 1

    gh issue edit "$issue_target" "${repo_args[@]}" --body-file "$issue_body_file" || exit 1

    verified_issue=$(gh issue view "$issue_target" "${repo_args[@]}" --json number,url,title,body) || exit 1
)
```

## Comment and close pattern

Use this when another skill needs to post a completion summary before closing an issue.

```bash
(
    comment_body_file=$(mktemp) || exit 1
    trap 'rm -f -- "$comment_body_file"' EXIT

    printf '%s' "$comment_body" > "$comment_body_file" || exit 1

    gh issue comment "$issue_target" "${repo_args[@]}" --body-file "$comment_body_file" || exit 1
    gh issue close "$issue_target" "${repo_args[@]}" || exit 1

    verified_issue=$(gh issue view "$issue_target" "${repo_args[@]}" --json number,url,title,state) || exit 1
)
```

## Worked example

For a draft with title in `issue_title`, body in `issue_body`, and a completion summary in `comment_body`, the lifecycle is:

1. Create or edit with the temp-file patterns above.
2. After implementation and verification, write `comment_body` to its own temp file.
3. Post it with `gh issue comment ... --body-file`.
4. Close with `gh issue close`.
5. Verify the final state with `gh issue view --json number,url,title,state`.

## Failure handling

- If `gh auth status` fails, stop and return the draft plus the intended `gh` command shape for manual use.
- If create returns a URL but verification fails, reconcile with read-only `gh issue view` or `gh issue list` before any retry.
- If comment succeeds but close verification fails, reconcile with read-only `gh issue view` before any retry or second close attempt.
- Never claim success until the verified output confirms the issue number, URL, title, and body.

## Manual fallback shape

When writes are blocked, return the approved draft and a bash/zsh-shaped command outline that makes clear the body must be written to a temp file and passed with `--body-file`.