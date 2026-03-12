# personal-repo-only-remote

Updated: 2026-03-12

## Rule
- If the original GitHub repository is not writable by the user, create or reuse a repository under the user's own account.
- Configure that personal repository as the only active remote for daily work.
- Avoid keeping the original upstream remote configured unless the user explicitly needs it.

## Steps
- Create or identify a writable repository under the user's GitHub account.
- Set it as `origin`.
- Remove any original upstream remote that could cause accidental sync.
- Commit and push milestone states to the personal repository.

## Why
- Reduces accidental pushes to a read-only or third-party repository.
- Gives all future agents one unambiguous remote policy.
