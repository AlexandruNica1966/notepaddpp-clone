#!/bin/bash
# Alias script for resuming Notepad++ Clone session
# Usage: npp or ./resume_notepaddpp.sh

SESSION_ID="20260719_093158_bbf5ed4d"
PROJECT_DIR="$HOME/hermes_workspace/notepaddpp_clone"

echo "Resuming Notepad++ Clone session: $SESSION_ID"
cd "$PROJECT_DIR" || { echo "Project directory not found!"; exit 1; }

hermes --resume "$SESSION_ID"
