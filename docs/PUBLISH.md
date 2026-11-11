# Publish without leaking device information

Do not publish `.cleanmywatch/`, backups, screenshots, DNS logs, pairing codes, local environment files or transcripts. `.gitignore` prevents routine additions of these directories; it does not remove already tracked files or erase history. Keep exports under the ignored directory and inspect the complete diff and history. There is no universal automatic privacy guarantee.

Run tests and `python tools/check_public_files.py` before release. The scanner checks tracked working files and staged content. Use `python tools/check_public_files.py --history` to scan every locally reachable commit's tree and author metadata too. It is an extra guard, not a complete secret detector. Review `git status --short`, `git ls-files`, `git diff --cached`, and `git log --format=fuller --stat`. Check contents, commit author emails, remotes and earlier commits. Use GitHub's noreply email or a public project identity for your own commits. GitHub account ownership remains public if the repository is public.

You may create a private `.cleanmywatch/public-policy.local.json` file containing `{"deny_terms": []}` and put personal words/identifiers into that list locally. Never commit this policy. The scanner reports affected filenames and revisions without printing matching private text. CI cannot know private terms that are absent from its environment.

Removing a line in a new commit does **not** remove it from older commits, forks, caches or clones. Removing old published history requires a separately authorized coordinated rewrite; do not silently force-push or promise that history cleanup erases copies elsewhere. Prepare and inspect a sanitized root before requesting approval for a remote rewrite. Ordinary privacy fixes can be pushed without rewriting history.

A prepared sanitized branch can be checked independently with `python tools/check_public_files.py --history --revision SANITIZED_BRANCH`. This does not delete or hide local old branches; it verifies only the history selected for publishing. Old local refs must never be pushed with `--all` or `--mirror`.

## GitHub Desktop (recommended for first upload)

1. File → Add local repository → choose this folder. The prepared local history uses a generic project author, without personal identity.
2. Inspect the History and Changes tabs. Do not drag private backups into the repository.
3. Click Publish repository, name it CleanMyWatch, keep it private initially. No existing repository is overwritten.
4. Check GitHub's file list and commit metadata. Then, when satisfied, change visibility to public in the repository settings.

## Git Bash alternative

Create an **empty** CleanMyWatch repository on GitHub; do not add a second README/license. Replace the placeholder remote with your account's repository URL, privately:

```bash
git status --short
git log --format=fuller --stat
git remote -v
git remote add origin https://github.com/YOUR_ACCOUNT/CleanMyWatch.git
git push -u origin main
```

If `origin` exists, inspect it first instead of overwriting it. Never force-push. Authenticate using Git Credential Manager/GitHub Desktop; do not put tokens into URLs. Do not paste credential prompts into chats. The project does not install GitHub CLI or create a remote account/repository automatically.

The bundled CI checks Python behavior and privacy guards on synthetic data; it cannot validate a watch. Pin Actions and Python dependencies to reviewed immutable revisions in your release process if required. Do not upload CI artifacts containing real device state.
