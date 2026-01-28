#!/bin/bash
# Push to a NEW repository with a different name

echo "🚀 Creating new GitHub repository..."
echo ""

# Get GitHub username
read -p "Enter your GitHub username: " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    echo "❌ Error: GitHub username required"
    exit 1
fi

# Suggest some good names
echo ""
echo "Suggested repository names:"
echo "1. mqgt-scf-validation"
echo "2. toe-empirical-validation"
echo "3. mqgt-scf-empirical"
echo "4. theory-of-everything-validation"
echo "5. Custom name"
echo ""
read -p "Choose option (1-5) or enter custom name: " CHOICE

case $CHOICE in
    1) REPO_NAME="mqgt-scf-validation" ;;
    2) REPO_NAME="toe-empirical-validation" ;;
    3) REPO_NAME="mqgt-scf-empirical" ;;
    4) REPO_NAME="theory-of-everything-validation" ;;
    5) read -p "Enter custom repository name: " REPO_NAME ;;
    *) REPO_NAME="$CHOICE" ;;  # If they typed a name directly
esac

if [ -z "$REPO_NAME" ]; then
    echo "❌ Error: Repository name required"
    exit 1
fi

REPO_URL="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

echo ""
echo "Repository will be: ${REPO_URL}"
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
    read -p "Update it to new repo? (y/n): " UPDATE_REMOTE
    if [ "$UPDATE_REMOTE" = "y" ]; then
        git remote set-url origin "$REPO_URL"
        echo "✓ Remote updated"
    else
        echo "Keeping existing remote"
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
    echo "View at: ${REPO_URL}"
else
    echo ""
    echo "❌ Push failed. Common issues:"
    echo "   - Repository not created on GitHub yet"
    echo "   - Authentication failed (use personal access token)"
    echo "   - Wrong repository name"
fi
