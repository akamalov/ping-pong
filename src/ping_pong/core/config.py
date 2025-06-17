"""
Game configuration management.

Centralized configuration for all game settings including display,
gameplay, physics, and audio parameters.
"""

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any, Optional


@dataclass
class GameConfig:
    """
    Centralized game configuration.
    
    All game settings are stored here and can be loaded from/saved to
    configuration files.
    """
    
    # Display settings
    SCREEN_WIDTH: int = 800
    SCREEN_HEIGHT: int = 600
    TARGET_FPS: int = 60
    FULLSCREEN: bool = False
    VSYNC: bool = True
    
    # Game settings
    BALL_SPEED: float = 200.0
    PADDLE_SPEED: float = 300.0
    WINNING_SCORE: int = 10
    BALL_SPEED_INCREASE: float = 1.05  # Speed multiplier per paddle hit
    MAX_BALL_SPEED: float = 600.0
    
    # Physics settings
    BALL_BOUNCE_FACTOR: float = 1.0
    PADDLE_BOUNCE_FACTOR: float = 1.1
    WALL_BOUNCE_FACTOR: float = 1.0
    
    # Paddle settings
    PADDLE_WIDTH: float = 15.0
    PADDLE_HEIGHT: float = 80.0
    PADDLE_OFFSET: float = 50.0  # Distance from screen edge
    
    # Ball settings
    BALL_SIZE: float = 10.0
    BALL_TRAIL_LENGTH: int = 5  # Number of trail segments
    
    # Audio settings
    MASTER_VOLUME: float = 0.8
    SFX_VOLUME: float = 1.0
    MUSIC_VOLUME: float = 0.6
    AUDIO_ENABLED: bool = True
    
    # Performance settings
    ENABLE_VSYNC: bool = True
    ENABLE_PERFORMANCE_MONITORING: bool = False
    MAX_FRAME_TIME_MS: float = 16.67  # 60 FPS target
    
    # Debug settings
    DEBUG_MODE: bool = False
    SHOW_FPS: bool = False
    SHOW_COLLISION_BOXES: bool = False
    SHOW_PERFORMANCE_STATS: bool = False
    
    # Input settings
    INPUT_BUFFER_SIZE: int = 8  # Frames to buffer input
    
    @classmethod
    def load_from_file(cls, config_path: str) -> 'GameConfig':
        """
        Load configuration from a JSON file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            GameConfig instance with loaded settings
        """
        config_file = Path(config_path)
        
        if not config_file.exists():
            # Create default config file
            default_config = cls()
            default_config.save_to_file(config_path)
            return default_config
        
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            # Create instance with loaded data
            config = cls()
            for key, value in config_data.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            
            return config
            
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load config from {config_path}: {e}")
            print("Using default configuration.")
            return cls()
    
    def save_to_file(self, config_path: str) -> None:
        """
        Save configuration to a JSON file.
        
        Args:
            config_path: Path where to save the configuration
        """
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(config_file, 'w') as f:
                json.dump(asdict(self), f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save config to {config_path}: {e}")
    
    def get_screen_size(self) -> tuple:
        """Get screen dimensions as a tuple."""
        return (self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
    
    def get_screen_center(self) -> tuple:
        """Get screen center coordinates."""
        return (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2)
    
    def get_paddle_positions(self) -> tuple:
        """Get default paddle positions (left, right)."""
        left_x = self.PADDLE_OFFSET
        right_x = self.SCREEN_WIDTH - self.PADDLE_OFFSET
        center_y = self.SCREEN_HEIGHT // 2
        return (left_x, center_y), (right_x, center_y)
    
    def validate_settings(self) -> list:
        """
        Validate configuration settings and return any issues.
        
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Screen resolution validation
        if self.SCREEN_WIDTH < 400 or self.SCREEN_HEIGHT < 300:
            errors.append("Screen resolution too small (minimum 400x300)")
        
        # FPS validation
        if self.TARGET_FPS < 30 or self.TARGET_FPS > 240:
            errors.append("Target FPS should be between 30 and 240")
        
        # Speed validation
        if self.BALL_SPEED <= 0 or self.PADDLE_SPEED <= 0:
            errors.append("Speeds must be positive values")
        
        if self.MAX_BALL_SPEED < self.BALL_SPEED:
            errors.append("Max ball speed must be >= initial ball speed")
        
        # Paddle validation
        if self.PADDLE_WIDTH <= 0 or self.PADDLE_HEIGHT <= 0:
            errors.append("Paddle dimensions must be positive")
        
        if self.PADDLE_OFFSET < 0 or self.PADDLE_OFFSET > self.SCREEN_WIDTH // 4:
            errors.append("Paddle offset should be between 0 and screen_width/4")
        
        # Volume validation
        volumes = [self.MASTER_VOLUME, self.SFX_VOLUME, self.MUSIC_VOLUME]
        for vol in volumes:
            if vol < 0.0 or vol > 1.0:
                errors.append("Volume values must be between 0.0 and 1.0")
        
        return errors
    
    def apply_performance_preset(self, preset: str) -> None:
        """
        Apply a performance preset.
        
        Args:
            preset: Performance preset name ('low', 'medium', 'high', 'ultra')
        """
        if preset == 'low':
            self.TARGET_FPS = 30
            self.ENABLE_VSYNC = False
            self.BALL_TRAIL_LENGTH = 0
            self.ENABLE_PERFORMANCE_MONITORING = False
        elif preset == 'medium':
            self.TARGET_FPS = 60
            self.ENABLE_VSYNC = True
            self.BALL_TRAIL_LENGTH = 3
            self.ENABLE_PERFORMANCE_MONITORING = False
        elif preset == 'high':
            self.TARGET_FPS = 60
            self.ENABLE_VSYNC = True
            self.BALL_TRAIL_LENGTH = 5
            self.ENABLE_PERFORMANCE_MONITORING = True
        elif preset == 'ultra':
            self.TARGET_FPS = 120
            self.ENABLE_VSYNC = False
            self.BALL_TRAIL_LENGTH = 8
            self.ENABLE_PERFORMANCE_MONITORING = True
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of current configuration."""
        return {
            "display": {
                "resolution": f"{self.SCREEN_WIDTH}x{self.SCREEN_HEIGHT}",
                "fps": self.TARGET_FPS,
                "fullscreen": self.FULLSCREEN
            },
            "gameplay": {
                "ball_speed": self.BALL_SPEED,
                "paddle_speed": self.PADDLE_SPEED,
                "winning_score": self.WINNING_SCORE
            },
            "audio": {
                "enabled": self.AUDIO_ENABLED,
                "master_volume": self.MASTER_VOLUME
            },
            "debug": {
                "debug_mode": self.DEBUG_MODE,
                "show_fps": self.SHOW_FPS
            }
        } 