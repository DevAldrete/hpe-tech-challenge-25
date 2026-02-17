#!/usr/bin/env bash
# Setup script for git hooks
# Run this script to install pre-commit and pre-push hooks

set -e

echo "🔧 Setting up Project AEGIS git hooks..."
echo ""

# Check if we're in a git repository
if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "❌ Error: Not in a git repository"
  exit 1
fi

# Install pre-commit if not installed
echo "📦 Checking for pre-commit..."
if ! command -v pre-commit &>/dev/null; then
  echo "  → Installing pre-commit..."
  if command -v uv &>/dev/null; then
    uv pip install pre-commit
  elif command -v pip &>/dev/null; then
    pip install pre-commit
  else
    echo "❌ Error: Neither uv nor pip found. Please install pre-commit manually."
    exit 1
  fi
else
  echo "  ✅ pre-commit already installed"
fi

# Install pre-commit hooks
echo ""
echo "🪝 Installing pre-commit hooks..."
pre-commit install --install-hooks

echo ""
echo "🪝 Installing commit-msg hook..."
pre-commit install --hook-type commit-msg

# Setup pre-push hook
echo ""
echo "🪝 Installing pre-push hook..."
HOOKS_DIR=".git/hooks"
CUSTOM_HOOKS_DIR=".githooks"

# Make pre-push hook executable
chmod +x "$CUSTOM_HOOKS_DIR/pre-push"

# Link or copy pre-push hook
if [ -f "$HOOKS_DIR/pre-push" ]; then
  echo "  ⚠️  pre-push hook already exists, backing up..."
  mv "$HOOKS_DIR/pre-push" "$HOOKS_DIR/pre-push.backup"
fi

# Create symlink or copy file
if ln -s "../../$CUSTOM_HOOKS_DIR/pre-push" "$HOOKS_DIR/pre-push" 2>/dev/null; then
  echo "  ✅ Linked pre-push hook"
else
  cp "$CUSTOM_HOOKS_DIR/pre-push" "$HOOKS_DIR/pre-push"
  chmod +x "$HOOKS_DIR/pre-push"
  echo "  ✅ Copied pre-push hook"
fi

# Run pre-commit on all files to verify setup
echo ""
echo "🔍 Running pre-commit on all files (this may take a moment)..."
if pre-commit run --all-files; then
  echo ""
  echo "✅ All files passed pre-commit checks!"
else
  echo ""
  echo "⚠️  Some files need formatting. Run 'pre-commit run --all-files' to fix."
fi

echo ""
echo "✅ Git hooks setup complete!"
echo ""
echo "📝 Summary:"
echo "  • Pre-commit hooks: Installed (runs on 'git commit')"
echo "  • Commit-msg hooks: Installed (validates commit messages)"
echo "  • Pre-push hooks: Installed (runs tests before 'git push')"
echo ""
echo "💡 Tips:"
echo "  • Skip pre-commit: git commit --no-verify"
echo "  • Skip pre-push: git push --no-verify"
echo "  • Run manually: pre-commit run --all-files"
echo "  • Update hooks: pre-commit autoupdate"
echo ""
