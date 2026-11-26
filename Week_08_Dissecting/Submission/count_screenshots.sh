#!/bin/sh
# Created by Claude Code (Opus 5.5)
# Prints the number of screenshots in screenshots/ (relative to this script).
dir="$(dirname "$0")/screenshots"
find "$dir" -maxdepth 1 -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \) | wc -l | tr -d ' '
