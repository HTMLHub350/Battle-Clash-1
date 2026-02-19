# Battle Clash 1

A real-time multiplayer fighting game where players battle each other in an arena using bullets and power-ups. Play solo against AI bots or compete with other players online!

## Features

- **Multiplayer Combat** - Up to 10+ players in one arena
- **AI Bots** - Spawn intelligent bots with 5 difficulty levels
- **Real-time Bullets** - Shoot in 4 directions (up, down, left, right)
- **Live Chat** - Communicate with other players in-game
- **Persistent Scoring** - High scores saved automatically
- **Fullscreen Mode** - Play in immersive fullscreen
- **Color-coded Players** - Each player has a unique color cube

## Getting Started

### Prerequisites
- Python 3.7+
- Flask and Flask-SocketIO

### Installation

```bash
pip install flask flask-socketio python-socketio python-engineio
```

### Running the Server

```bash
python server.py
```

The game will be available at `http://0.0.0.0:3003`

## How to Play

### Basic Controls

| Key | Action |
|-----|--------|
| **Arrow Keys** or **WASD** | Move around the arena |
| **SPACE** | Shoot bullets in 4 directions |
| **Y** | Open chat (normal talk) |
| **T** | Open chat (team talk) |
| **Z** | Toggle viewing all/recent comments |
| **0** | Close chat input |
| **Fullscreen** | Button to toggle fullscreen mode |

### Game Mechanics

- **Health**: Start with 100 HP
- **Bullets**: Each shot fires 4 bullets (up, down, left, right)
- **Damage**: Each bullet deals 5% damage (20 bullets to defeat)
- **Attack Cooldown**: 0.5 seconds between shots
- **Defeat**: Reach 0 HP → Disconnect → Click "Join" to rejoin
- **Scoring**: Defeat an enemy → +1 point to your score

### Joining the Game

1. Enter your username (8 characters max)
2. Click **Join**
3. Start playing!

### Spawning Bots

Type `bot:<name>` in the username field:

```
bot:Terminator        // Creates bot at level 1
bot:Terminator/lvl=5  // Creates bot at level 5
```

**Bot Levels** (1-5):
- **Level 1**: Speed 2, 100 HP, 150px range
- **Level 2**: Speed 2.5, 120 HP, 175px range
- **Level 3**: Speed 3, 140 HP, 200px range
- **Level 4**: Speed 3.5, 160 HP, 225px range
- **Level 5**: Speed 4, 180 HP, 250px range

Bots automatically wander the arena and attack nearby players.

## Chat System

- **Press Y** → Open chat for normal talk (visible to all)
- **Press T** → Open chat for team talk (marked as [T])
- **Type message** → Can type any character including Y, T, Z, SPACE
- **Press ENTER** → Send message
- **Press 0 or ESC** → Close chat
- **Press Z** → Toggle between 5 recent or all messages

Chat messages are saved in `chats.json` and persist across game restarts.

## Game Files

- `server.py` - Flask-SocketIO server with game logic
- `templates/index.html` - Game client and UI
- `highscores.json` - Saved player scores
- `chats.json` - Saved chat messages

## Scoring System

- **Highscores**: Tracked and saved per player
- **Kills**: Each defeated enemy = +1 point
- **Persistence**: Scores saved even after disconnect
- **Leaderboard**: View top players in the sidebar

## Tips & Tricks

1. **Fullscreen Mode** - Click "Fullscreen" button for better visibility
2. **Chat While Playing** - Press Y/T to chat without losing focus
3. **Strong Bots** - Try spawning `bot:Enemy/lvl=5` for a challenge
4. **Dodge & Attack** - Keep moving to avoid incoming bullets
5. **Team Communication** - Use chat to coordinate with other players

## Server Features

- Real-time bullet physics and collision detection
- Persistent data storage (scores & chats)
- Automatic player/bot cleanup on disconnect
- Anti-duplicate usernames (can't use taken names)
- 60 FPS game updates

## Known Features

- Bots wander randomly and attack only players
- Chat messages limited to 60 characters display
- Maximum players/bots limited by server performance
- Comments auto-save and load on reconnect

## Future Enhancements

- Power-ups and special abilities
- Team-based gameplay
- Different arena maps
- Sound effects and music
- Mobile support

## License

Created for multiplayer gaming entertainment.

---

**Made with Flask, Socket.IO, and SVG Canvas** 🎮🔴

Good luck battling! 💥
