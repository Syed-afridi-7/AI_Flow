#!/usr/bin/env bash
# AI_Flow - Multi-Agent Skills Installer for macOS / Linux
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
SOURCE_SKILLS="$REPO_ROOT/skills"

if [ ! -d "$SOURCE_SKILLS" ]; then
    echo "Error: Source skills directory not found at $SOURCE_SKILLS" >&2
    exit 1
fi

HOME_DIR="$HOME"
DESTINATIONS=(
    "$HOME_DIR/.agents/skills"
    "$HOME_DIR/.gemini/antigravity/skills"
    "$HOME_DIR/.claude/skills"
)

echo "Installing AI_Flow skills from: $SOURCE_SKILLS"

for dest in "${DESTINATIONS[@]}"; do
    mkdir -p "$dest"
    echo "Target directory: $dest"

    for skill_path in "$SOURCE_SKILLS"/*; do
        if [ -d "$skill_path" ]; then
            skill_name="$(basename "$skill_path")"
            target_path="$dest/$skill_name"

            rm -rf "$target_path"
            cp -R "$skill_path" "$target_path"
            echo "  [Installed] $skill_name -> $dest"
        fi
    done
done

echo ""
TOTAL_SKILLS=$(find "$SOURCE_SKILLS" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
echo "Installation complete! All ${TOTAL_SKILLS} skills are now available to your AI agents."

