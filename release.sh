#!/bin/sh
# Release script — bumps version, commits, tags, and pushes.
# Usage: ./release.sh 1.3.0
set -e

if [ -z "$1" ]; then
    CURRENT=$(grep '__version__' tdeploy/__init__.py | sed 's/.*"\(.*\)"/\1/')
    echo "Usage: ./release.sh <version>"
    echo "Current version: ${CURRENT}"
    exit 1
fi

VERSION="$1"
TAG="v${VERSION}"

# Check for uncommitted changes
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "Error: you have uncommitted changes. Commit or stash them first."
    exit 1
fi

# Check tag doesn't already exist
if git rev-parse "${TAG}" >/dev/null 2>&1; then
    echo "Error: tag ${TAG} already exists"
    exit 1
fi

# Update version in pyproject.toml
sed -i "s/^version = \".*\"/version = \"${VERSION}\"/" pyproject.toml

# Update version in tdeploy/__init__.py
sed -i "s/__version__ = \".*\"/__version__ = \"${VERSION}\"/" tdeploy/__init__.py

echo "Bumped to ${VERSION}"
echo ""

# Commit + tag + push
git add pyproject.toml tdeploy/__init__.py
git commit -m "Release ${TAG}"
git tag "${TAG}"
git push
git push --tags

echo ""
echo "Released ${TAG}"
