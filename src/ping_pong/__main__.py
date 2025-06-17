"""
Main entry point for the ping-pong game.

This module can be run directly to start the game:
    python -m ping_pong
"""

import sys
import argparse
from pathlib import Path

from .core.game import Game


def main():
    """Main entry point for the ping-pong game."""
    parser = argparse.ArgumentParser(description="Ping-Pong Game")
    parser.add_argument(
        "--config", 
        type=str, 
        default="config.json",
        help="Path to configuration file (default: config.json)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    parser.add_argument(
        "--windowed",
        action="store_true", 
        help="Force windowed mode (disable fullscreen)"
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=60,
        help="Target FPS (default: 60)"
    )
    
    args = parser.parse_args()
    
    try:
        # Create game instance
        game = Game(config_path=args.config)
        
        # Apply command line overrides
        if args.debug:
            game.config.DEBUG_MODE = True
            game.config.SHOW_COLLISION_BOXES = True
            game.config.SHOW_FPS = True
            print("Debug mode enabled")
        
        if args.windowed:
            game.config.FULLSCREEN = False
            print("Windowed mode enabled")
        
        if args.fps != 60:
            game.config.TARGET_FPS = args.fps
            print(f"Target FPS set to {args.fps}")
        
        # Start the game
        game.run()
        
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error running game: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 