#!/usr/bin/env bash
# Sync this fork with upstream by merging, so existing commits (and their
# timestamps) are never rewritten. Never rebases, never force-pushes.
set -euo pipefail

UPSTREAM_URL="https://github.com/Neltharion59/AI4SE_Labs_2026.git"
BRANCH="main"

cd "$(git rev-parse --show-toplevel)"

if [[ "$(git branch --show-current)" != "$BRANCH" ]]; then
  echo "error: switch to '$BRANCH' first (git switch $BRANCH)" >&2
  exit 1
fi

if [[ -n "$(git status --porcelain)" ]]; then
  echo "error: uncommitted changes; commit them before syncing" >&2
  exit 1
fi

if ! git remote get-url upstream >/dev/null 2>&1; then
  git remote add upstream "$UPSTREAM_URL"
fi

git fetch upstream
git fetch origin

# Bring in anything already pushed to the fork (e.g. via GitHub's "Sync fork").
git merge --ff-only "origin/$BRANCH"

if git merge-base --is-ancestor "upstream/$BRANCH" HEAD; then
  echo "Already up to date with upstream."
else
  if ! git merge --no-edit "upstream/$BRANCH"; then
    echo >&2
    echo "Merge conflict. Fix the files, then: git add <files> && git commit && git push" >&2
    echo "Or cancel with: git merge --abort" >&2
    exit 1
  fi
fi

git push origin "$BRANCH"
