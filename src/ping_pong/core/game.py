"""
Main game class that orchestrates the entire ping-pong game.
"""

import pygame
import sys
import time
from typing import Optional

from .config import GameConfig
from .ecs.entity_manager import EntityManager
from .ecs.system_manager import SystemManager
from .ecs.component_manager import ComponentManager
from ..systems.movement import MovementSystem
from ..systems.collision import CollisionSystem
from ..systems.input import InputSystem
from ..systems.render import RenderSystem
from ..entities.entity_factory import EntityFactory


class Game:
    """
    Main game class that manages the game loop and coordinates all systems.
    
    This class is responsible for:
    - Initializing pygame and game systems
    - Managing the main game loop
    - Coordinating between systems
    - Handling game state transitions
    """
    
    def __init__(self, config_path: str = "config.json"):
        # Load configuration
        self.config = GameConfig.load_from_file(config_path)
        
        # Validate configuration
        config_errors = self.config.validate_settings()
        if config_errors:
            print("Configuration errors found:")
            for error in config_errors:
                print(f"  - {error}")
            print("Using default values for invalid settings.")
        
        # Initialize pygame
        pygame.init()
        pygame.font.init()
        
        # Create display
        display_flags = 0
        if self.config.FULLSCREEN:
            display_flags |= pygame.FULLSCREEN
        if self.config.VSYNC:
            display_flags |= pygame.HWSURFACE | pygame.DOUBLEBUF
        
        self.screen = pygame.display.set_mode(
            self.config.get_screen_size(),
            display_flags
        )
        pygame.display.set_caption("Ping-Pong Game")
        
        # Initialize game clock
        self.clock = pygame.time.Clock()
        
        # Initialize ECS components
        self.entity_manager = EntityManager()
        self.component_manager = ComponentManager()
        self.system_manager = SystemManager(self.entity_manager)
        
        # Initialize entity factory
        self.entity_factory = EntityFactory(self.entity_manager, self.config)
        
        # Initialize systems
        self._initialize_systems()
        
        # Game state
        self.running = False
        self.paused = False
        
        # Performance tracking
        self.frame_count = 0
        self.last_fps_update = time.time()
        self.fps_display = 60.0
        
        # Game entities
        self.player1_paddle = None
        self.player2_paddle = None
        self.ball = None
        
        # Score tracking
        self.player1_score = 0
        self.player2_score = 0
    
    def _initialize_systems(self) -> None:
        """Initialize and register all game systems."""
        # Create systems in priority order
        input_system = InputSystem(self.entity_manager)
        movement_system = MovementSystem(self.entity_manager)
        collision_system = CollisionSystem(self.entity_manager, self.config)
        render_system = RenderSystem(self.entity_manager, self.config, self.screen)
        
        # Register systems
        self.system_manager.register_system(input_system)
        self.system_manager.register_system(movement_system)
        self.system_manager.register_system(collision_system)
        self.system_manager.register_system(render_system)
        
        # Store references for easy access
        self.input_system = input_system
        self.render_system = render_system
    
    def initialize_game_entities(self) -> None:
        """Create the initial game entities."""
        # Create paddles
        left_pos, right_pos = self.config.get_paddle_positions()
        
        self.player1_paddle = self.entity_factory.create_paddle(
            left_pos[0], left_pos[1], player_number=1
        )
        
        self.player2_paddle = self.entity_factory.create_paddle(
            right_pos[0], right_pos[1], player_number=2
        )
        
        # Create ball at center
        center_x, center_y = self.config.get_screen_center()
        self.ball = self.entity_factory.create_ball(center_x, center_y)
    
    def run(self) -> None:
        """Start the main game loop."""
        self.running = True
        self.initialize_game_entities()
        
        print(f"Starting Ping-Pong Game ({self.config.SCREEN_WIDTH}x{self.config.SCREEN_HEIGHT})")
        print("Controls:")
        print("  Player 1: W/S keys")
        print("  Player 2: UP/DOWN arrow keys")
        print("  ESC: Quit game")
        print("  P: Pause/Unpause")
        
        while self.running:
            dt = self.clock.tick(self.config.TARGET_FPS) / 1000.0  # Convert to seconds
            
            self._handle_events()
            
            if not self.paused:
                self._update_game(dt)
            
            self._render_game()
            
            # Update performance stats
            self._update_performance_stats(dt)
        
        self._cleanup()
    
    def _handle_events(self) -> None:
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                    print("Game Paused" if self.paused else "Game Resumed")
                elif event.key == pygame.K_r:
                    self._reset_game()
                elif event.key == pygame.K_F1:
                    self._toggle_debug_mode()
            
            # Let input system handle other events
            self.input_system.handle_event(event)
    
    def _update_game(self, dt: float) -> None:
        """Update all game systems."""
        # Update all systems
        self.system_manager.update_all_systems(dt)
        
        # Check for scoring
        self._check_scoring()
        
        # Check for game over
        self._check_game_over()
    
    def _render_game(self) -> None:
        """Render the game (handled by render system)."""
        # The render system handles all rendering
        # Just update the display
        pygame.display.flip()
    
    def _check_scoring(self) -> None:
        """Check if a player has scored."""
        if not self.ball:
            return
        
        ball_pos = self.entity_manager.get_component(self.ball, 
            self.entity_factory.position_component_type)
        
        if ball_pos:
            # Check if ball went off left or right side
            if ball_pos.x < 0:
                # Player 2 scores
                self.player2_score += 1
                print(f"Player 2 scores! Score: {self.player1_score} - {self.player2_score}")
                self._reset_ball()
            elif ball_pos.x > self.config.SCREEN_WIDTH:
                # Player 1 scores
                self.player1_score += 1
                print(f"Player 1 scores! Score: {self.player1_score} - {self.player2_score}")
                self._reset_ball()
    
    def _check_game_over(self) -> None:
        """Check if the game is over."""
        if (self.player1_score >= self.config.WINNING_SCORE or 
            self.player2_score >= self.config.WINNING_SCORE):
            
            winner = "Player 1" if self.player1_score >= self.config.WINNING_SCORE else "Player 2"
            print(f"\nGame Over! {winner} wins!")
            print(f"Final Score: {self.player1_score} - {self.player2_score}")
            print("Press R to restart or ESC to quit")
            
            self.paused = True
    
    def _reset_ball(self) -> None:
        """Reset the ball to center with random direction."""
        if self.ball:
            self.entity_manager.destroy_entity(self.ball)
        
        center_x, center_y = self.config.get_screen_center()
        self.ball = self.entity_factory.create_ball(center_x, center_y)
    
    def _reset_game(self) -> None:
        """Reset the entire game."""
        print("Resetting game...")
        
        # Reset scores
        self.player1_score = 0
        self.player2_score = 0
        
        # Reset ball
        self._reset_ball()
        
        # Reset paddle positions
        left_pos, right_pos = self.config.get_paddle_positions()
        
        if self.player1_paddle:
            paddle_pos = self.entity_manager.get_component(self.player1_paddle,
                self.entity_factory.position_component_type)
            if paddle_pos:
                paddle_pos.set_position(left_pos[0], left_pos[1])
        
        if self.player2_paddle:
            paddle_pos = self.entity_manager.get_component(self.player2_paddle,
                self.entity_factory.position_component_type)
            if paddle_pos:
                paddle_pos.set_position(right_pos[0], right_pos[1])
        
        self.paused = False
    
    def _toggle_debug_mode(self) -> None:
        """Toggle debug mode."""
        self.config.DEBUG_MODE = not self.config.DEBUG_MODE
        self.config.SHOW_COLLISION_BOXES = self.config.DEBUG_MODE
        self.config.SHOW_FPS = self.config.DEBUG_MODE
        
        print(f"Debug mode: {'ON' if self.config.DEBUG_MODE else 'OFF'}")
    
    def _update_performance_stats(self, dt: float) -> None:
        """Update performance statistics."""
        self.frame_count += 1
        current_time = time.time()
        
        # Update FPS display every second
        if current_time - self.last_fps_update >= 1.0:
            self.fps_display = self.frame_count / (current_time - self.last_fps_update)
            self.frame_count = 0
            self.last_fps_update = current_time
            
            if self.config.SHOW_FPS:
                print(f"FPS: {self.fps_display:.1f}")
    
    def _cleanup(self) -> None:
        """Clean up resources."""
        print("Shutting down...")
        
        # Save configuration
        self.config.save_to_file("config.json")
        
        # Quit pygame
        pygame.quit()
        sys.exit()
    
    def get_performance_report(self) -> dict:
        """Get a comprehensive performance report."""
        return {
            "fps": self.fps_display,
            "system_performance": self.system_manager.get_performance_report(),
            "entity_count": self.entity_manager.get_entity_count(),
            "config_summary": self.config.get_config_summary()
        } 