#!/bin/bash
# Push Zorathena Implementation to GitHub

set -e

REPO_DIR="/Users/christophermichaelbaird/Downloads/mqgt_scf_reissue_2026-01-20_010939UTC"
cd "$REPO_DIR"

echo "=========================================="
echo "Pushing Zorathena Implementation to GitHub"
echo "=========================================="
echo ""

# Check if remote exists
if git remote get-url origin 2>/dev/null; then
    echo "✓ Remote 'origin' already configured"
    REMOTE_URL=$(git remote get-url origin)
    echo "  URL: $REMOTE_URL"
else
    echo "⚠ No remote configured"
    echo ""
    echo "To add a remote, run:"
    echo "  git remote add origin git@github.com:cbaird26/mqgt-scf-reissue.git"
    echo ""
    echo "Or create a new repo at: https://github.com/new"
    echo "Then add the remote and run this script again."
    exit 1
fi

echo ""
echo "Current branch:"
git branch --show-current

echo ""
echo "Commits to push:"
git log --oneline origin/main..HEAD 2>/dev/null || git log --oneline -5

echo ""
echo "Files to push:"
git ls-files | wc -l
echo "files tracked"

echo ""
read -p "Push to GitHub? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Pushing to GitHub..."
git push -u origin main

echo ""
echo "=========================================="
echo "✓ Push complete!"
echo "=========================================="
echo ""
echo "View your repo at:"
echo "  https://github.com/$(git remote get-url origin | sed 's/.*github.com[:/]\(.*\)\.git/\1/')"
echo ""
