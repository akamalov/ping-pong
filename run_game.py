#!/usr/bin/env python3
"""
Simple run script for the ping-pong game.
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run the game
from ping_pong.__main__ import main

if __name__ == "__main__":
    main() 