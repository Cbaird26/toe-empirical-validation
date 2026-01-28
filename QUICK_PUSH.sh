#!/bin/bash
# Quick push script for existing GitHub repository

echo "🚀 Pushing to existing GitHub repository..."
echo ""

# Get GitHub username
read -p "Enter your GitHub username: " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    echo "❌ Error: GitHub username required"
    exit 1
fi

REPO_NAME="mqgt-scf"
REPO_URL="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

echo "Repository URL: ${REPO_URL}"
echo ""

# Check if remote exists
if git remote get-url origin &>/dev/null; then
    echo "⚠️  Remote 'origin' already exists"
    read -p "Update it? (y/n): " UPDATE_REMOTE
    if [ "$UPDATE_REMOTE" = "y" ]; then
        git remote set-url origin "$REPO_URL"
        echo "✓ Remote updated"
    fi
else
    echo "Adding remote..."
    git remote add origin "$REPO_URL"
    echo "✓ Remote added"
fi

echo ""
echo "Choose push method:"
echo "1. Force push (overwrites existing repo) - Use if repo is empty"
echo "2. Merge push (combines with existing content) - Use if repo has content"
read -p "Enter choice (1 or 2): " PUSH_CHOICE

if [ "$PUSH_CHOICE" = "1" ]; then
    echo ""
    echo "⚠️  WARNING: This will overwrite the existing repository!"
    read -p "Continue? (y/n): " CONFIRM
    if [ "$CONFIRM" = "y" ]; then
        echo "Force pushing..."
        git push -u origin main --force
        echo ""
        echo "✅ Force push complete!"
    else
        echo "Cancelled"
        exit 0
    fi
elif [ "$PUSH_CHOICE" = "2" ]; then
    echo ""
    echo "Pulling existing content first..."
    git pull origin main --allow-unrelated-histories || echo "No existing content to pull"
    echo ""
    echo "Pushing..."
    git push -u origin main
    echo ""
    echo "✅ Push complete!"
else
    echo "Invalid choice"
    exit 1
fi

echo ""
echo "🎉 Repository pushed successfully!"
echo "View at: ${REPO_URL}"
