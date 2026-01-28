#!/bin/bash
# Quick push script for toe-empirical-validation repository

echo "🚀 Pushing to toe-empirical-validation repository..."
echo ""

# Get GitHub username
read -p "Enter your GitHub username: " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    echo "❌ Error: GitHub username required"
    exit 1
fi

REPO_NAME="toe-empirical-validation"
REPO_URL="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

echo ""
echo "Repository: ${REPO_URL}"
echo ""
echo "⚠️  IMPORTANT: Create the repository on GitHub first!"
echo "   1. Go to: https://github.com/new"
echo "   2. Repository name: ${REPO_NAME}"
echo "   3. Description: 'Empirical Validation of MQGT-SCF Theory of Everything'"
echo "   4. Choose: Public"
echo "   5. DO NOT initialize with README"
echo "   6. Click 'Create repository'"
echo ""
read -p "Press Enter after you've created the repository on GitHub..."

# Check if remote exists
if git remote get-url origin &>/dev/null; then
    echo ""
    echo "⚠️  Remote 'origin' already exists"
    read -p "Update it? (y/n): " UPDATE_REMOTE
    if [ "$UPDATE_REMOTE" = "y" ]; then
        git remote set-url origin "$REPO_URL"
        echo "✓ Remote updated"
    else
        echo "Keeping existing remote"
        REPO_URL=$(git remote get-url origin)
    fi
else
    echo ""
    echo "Adding remote..."
    git remote add origin "$REPO_URL"
    echo "✓ Remote added"
fi

echo ""
echo "Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "🎉 Your repository is live at:"
    echo "   ${REPO_URL}"
    echo ""
    echo "Next steps:"
    echo "  - Add repository topics: theory-of-everything, physics, empirical-validation"
    echo "  - Create a release (v1.0.0)"
    echo "  - Share on social media!"
else
    echo ""
    echo "❌ Push failed. Common issues:"
    echo "   - Repository not created on GitHub yet"
    echo "   - Authentication failed (use personal access token)"
    echo "   - Wrong repository name or username"
    echo ""
    echo "Try again or check: ${REPO_URL}"
fi
