# Ping-Pong Game 🏓

A modern, high-performance ping-pong game built with Python and Pygame using Entity-Component-System (ECS) architecture.

## ✨ Features

- **Clean ECS Architecture**: Maintainable, modular code structure
- **60 FPS Gameplay**: Smooth physics and responsive controls
- **Configurable Settings**: Customize game behavior via JSON config
- **Debug Mode**: Performance monitoring and collision visualization
- **Advanced Physics**: Realistic ball bouncing and paddle interaction
- **Object Pooling**: Optimized memory management for performance
- **Component Serialization**: Save/load game state support

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
  "PADDLE_SPEED": 300,
  "BALL_SPEED": 250,
  "WINNING_SCORE": 5,
  "DEBUG_MODE": false
}
```

### Key Settings

- **Display**: Resolution, fullscreen, VSync
- **Gameplay**: Paddle/ball speeds, winning score
- **Physics**: Bounce factors, speed increases
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

- **Object Pooling**: Reuses component instances for memory efficiency
- **System Profiling**: Tracks system execution times
- **Configurable Quality**: Adjust settings for different hardware

## 📁 Project Structure

```
ping-pong/
├── src/ping_pong/           # Main game package
│   ├── core/                # Core ECS and game systems
│   │   ├── ecs/            # ECS framework
│   │   ├── config.py       # Configuration management
│   │   └── game.py         # Main game class
│   ├── components/         # Game components
│   ├── systems/           # Game systems
│   ├── entities/          # Entity factory
│   └── __main__.py        # Entry point
├── docs/                  # Documentation
├── requirements.txt       # Dependencies
├── config.json           # Game configuration
└── run_game.py          # Simple run script
```

## 🛠️ Development

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
- **60 FPS** at 1080p resolution
- **< 50MB** memory usage
- **< 5ms** frame time
- **Object pooling** for zero-allocation gameplay

## 🎯 Game Rules

1. First player to reach the winning score (default: 5) wins
2. Ball speed increases slightly after each paddle hit
3. Ball angle changes based on where it hits the paddle
4. Ball resets to center after each score

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
