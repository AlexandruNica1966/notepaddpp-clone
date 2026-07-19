#!/bin/bash
# Notepad++ Clone - Tkinter Edition Launcher

cd "$(dirname "$0")/src" || exit 1
python3 main.py "$@"
