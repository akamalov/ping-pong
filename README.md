# Ping-Pong Game 🏓

A modern, high-performance ping-pong game built with Python and Pygame using Entity-Component-System (ECS) architecture.

## ✨ Features

- **Clean ECS Architecture**: Maintainable, modular code structure
- **60 FPS Gameplay**: Smooth physics and responsive controls
- **Configurable Settings**: Customize game behavior via JSON config
- **Debug Mode**: Performance monitoring and collision visualization
- **Advanced Physics**: Realistic ball bouncing and paddle interaction
- **Component-Based Design**: Extensible game architecture

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd ping-pong

# Install dependencies
pip install -r requirements.txt

# Run the game
python run_game.py
```

### Alternative Methods

```bash
# Run as module
python -m ping_pong

# With command line options  
python run_game.py --debug --windowed --fps 120
```

## 🎮 Controls

| Player 1 | Player 2 | Action |
|----------|----------|--------|
| W / S | ↑ / ↓ | Move paddle up/down |
| - | - | - |
| **Global Controls** | | |
| ESC | | Quit game |
| P | | Pause/Unpause |
| R | | Restart game |
| F1 | | Toggle debug mode |

## ⚙️ Configuration

Game settings are stored in `config.json`:

```json
{
  "SCREEN_WIDTH": 800,
  "SCREEN_HEIGHT": 600,
  "TARGET_FPS": 60,
  "FULLSCREEN": false,
  "VSYNC": true,
  "BALL_SPEED": 250,
  "PADDLE_SPEED": 300,
  "WINNING_SCORE": 5,
  "BALL_SPEED_INCREASE": 1.05,
  "MAX_BALL_SPEED": 500,
  "BALL_BOUNCE_FACTOR": 1.0,
  "PADDLE_BOUNCE_FACTOR": 1.1,
  "WALL_BOUNCE_FACTOR": 1.0,
  "PADDLE_WIDTH": 15,
  "PADDLE_HEIGHT": 80,
  "PADDLE_OFFSET": 50.0,
  "BALL_SIZE": 12,
  "BALL_TRAIL_LENGTH": 5,
  "MASTER_VOLUME": 0.8,
  "SFX_VOLUME": 1.0,
  "MUSIC_VOLUME": 0.6,
  "AUDIO_ENABLED": true,
  "ENABLE_VSYNC": true,
  "ENABLE_PERFORMANCE_MONITORING": false,
  "MAX_FRAME_TIME_MS": 16.67,
  "DEBUG_MODE": true,
  "SHOW_FPS": true,
  "SHOW_COLLISION_BOXES": true,
  "SHOW_PERFORMANCE_STATS": false,
  "INPUT_BUFFER_SIZE": 8
}
```

### Key Settings

- **Display**: Resolution, fullscreen, VSync
- **Gameplay**: Paddle/ball speeds, winning score, speed increases
- **Physics**: Bounce factors, collision settings
- **Audio**: Volume controls and audio settings
- **Debug**: Collision boxes, FPS display, performance monitoring

## 🏗️ Architecture

### Entity-Component-System (ECS)

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Entities   │    │ Components  │    │   Systems   │
├─────────────┤    ├─────────────┤    ├─────────────┤
│ • Paddles   │    │ • Position  │    │ • Movement  │
│ • Ball      │    │ • Velocity  │    │ • Collision │
│ • Walls     │    │ • Render    │    │ • Input     │
│ • Goals     │    │ • Collision │    │ • Render    │
│             │    │ • Input     │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Core Systems

- **InputSystem**: Processes player input and updates velocities
- **MovementSystem**: Updates entity positions based on velocity
- **CollisionSystem**: Handles collision detection and response
- **RenderSystem**: Draws entities to screen with layer sorting

### Performance Features

- **Component-Based Architecture**: Clean separation of concerns
- **System Profiling**: Tracks system execution times
- **Configurable Quality**: Adjust settings for different hardware
- **Efficient Collision Detection**: Optimized for real-time gameplay

## 📁 Project Structure

```
ping-pong/
├── src/ping_pong/           # Main game package
│   ├── core/                # Core ECS and game systems
│   │   ├── ecs/            # ECS framework
│   │   │   ├── entity_manager.py
│   │   │   ├── component_manager.py
│   │   │   ├── system_manager.py
│   │   │   ├── component.py
│   │   │   └── system.py
│   │   ├── config.py       # Configuration management
│   │   └── game.py         # Main game class
│   ├── components/         # Game components
│   │   ├── position.py     # Position component
│   │   ├── velocity.py     # Velocity component
│   │   ├── render.py       # Render component
│   │   ├── collision.py    # Collision component
│   │   └── input.py        # Input component
│   ├── systems/           # Game systems
│   │   ├── movement.py    # Movement system
│   │   ├── collision.py   # Collision system
│   │   ├── render.py      # Render system
│   │   └── input.py       # Input system
│   ├── entities/          # Entity factory
│   │   └── entity_factory.py
│   └── __main__.py        # Entry point
├── docs/                  # Documentation
│   ├── architecture.md    # System architecture details
│   ├── product_requirement_docs.md # Product requirements
│   └── technical.md       # Technical documentation
├── prompts/              # APM framework prompts
├── requirements.txt      # Dependencies
├── requirements-dev.txt  # Development dependencies
├── config.json          # Game configuration
├── run_game.py         # Simple run script
└── final_review_gate.py # Interactive review script
```

## 🛠️ Development

### Dependencies

**Runtime Dependencies:**
```
pygame-ce==2.4.1
numpy==1.24.3
dataclasses-json==0.5.9
typing-extensions==4.7.1
```

**Development Dependencies:**
```
pytest==7.4.0
pytest-cov==4.1.0
pytest-mock==3.11.1
black==23.7.0
pylint==2.17.4
mypy==1.4.1
pre-commit==3.3.3
sphinx==7.1.1
```

### Running Tests

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run with coverage
pytest --cov=ping_pong tests/
```

### Code Quality

```bash
# Format code
black src/

# Lint code
pylint src/ping_pong

# Type checking
mypy src/ping_pong
```

### Debug Mode

Enable debug mode to see:
- FPS counter
- Collision boxes
- Performance metrics
- System execution times

```bash
python run_game.py --debug
```

## 📊 Performance

Target specifications:
- **60 FPS** at 800x600 resolution
- **Responsive controls** with minimal input latency  
- **Efficient rendering** with layer-based drawing
- **Clean architecture** for maintainability

## 🎯 Game Rules

1. First player to reach the winning score (configurable, default: 5) wins
2. Ball speed can increase after paddle hits (configurable)
3. Ball angle changes based on collision dynamics
4. Ball resets to center after each score with random direction

## 🎮 Command Line Options

```bash
python run_game.py [OPTIONS]

Options:
  --config PATH     Path to configuration file (default: config.json)
  --debug          Enable debug mode with collision boxes and FPS display
  --windowed       Force windowed mode (disable fullscreen)
  --fps INTEGER    Target FPS (default: 60)
  -h, --help       Show help message
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔧 Troubleshooting

### Common Issues

**Game won't start:**
- Check Python version (3.8+ required)
- Install dependencies: `pip install -r requirements.txt`
- Try windowed mode: `python run_game.py --windowed`

**Low FPS:**
- Reduce screen resolution in config.json
- Disable VSync: set `"VSYNC": false`
- Try different FPS targets: `python run_game.py --fps 30`

**Input lag:**
- Check if other applications are using high CPU
- Try disabling debug mode
- Reduce ball/paddle speeds in config

### System Requirements

- **Minimum**: Python 3.8, 512MB RAM, integrated graphics
- **Recommended**: Python 3.9+, 1GB RAM, dedicated graphics
- **Optimal**: Python 3.11+, 2GB RAM, modern GPU

## 📚 Documentation

For detailed documentation, see the `docs/` directory:
- `architecture.md` - System architecture details  
- `product_requirement_docs.md` - Complete feature specifications
- `technical.md` - Technical implementation details

## 🎯 Current Implementation Status

### ✅ Completed Features
- Complete ECS architecture with Entity, Component, and System managers
- Core game entities: Paddles, Ball, Walls, Goals
- Physics systems: Movement, Collision detection and response
- Input handling with configurable key bindings
- Rendering system with layered drawing
- Game state management (Playing, Paused)
- Configuration system with JSON settings
- Debug mode with performance monitoring
- Command-line argument support

### 🚧 In Development
- Advanced AI opponent
- Audio system integration
- Particle effects
- Menu system
- Game state persistence

### 🔮 Future Enhancements
- Network multiplayer capability
- Tournament mode
- Power-ups and special effects
- Customizable themes
- Replay system
