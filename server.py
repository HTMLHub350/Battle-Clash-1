from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import random
import json
import os
import math

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

HIGHSCORES_FILE = "highscores.json"
CHATS_FILE = "chats.json"

if os.path.exists(HIGHSCORES_FILE):
    with open(HIGHSCORES_FILE, "r") as f:
        saved_highscores = json.load(f)
else:
    saved_highscores = []

if os.path.exists(CHATS_FILE):
    with open(CHATS_FILE, "r") as f:
        saved_chats = json.load(f)
else:
    saved_chats = []

players = {}  # connected players
bullets = []  # all bullets in flight
bots = {}  # AI bots
player_colors = ["blue", "red", "orange", "green", "yellow", "purple", "cyan", "magenta", "lime", "pink"]

def save_highscores():
    with open(HIGHSCORES_FILE, "w") as f:
        json.dump(saved_highscores, f, indent=4)

def save_chats():
    with open(CHATS_FILE, "w") as f:
        json.dump(saved_chats, f, indent=4)

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("spawn_bot")
def handle_spawn_bot(data):
    bot_input = data["name"]
    bot_id = "bot_" + str(random.randint(10000, 99999))

    # Parse bot name and level
    level = 1
    if "&level=" in bot_input:
        bot_name, level_str = bot_input.split("&level=")
        try:
            level = int(level_str)
            if level < 1 or level > 6:
                level = 1
        except:
            level = 1
    else:
        bot_name = bot_input

    # Check if name is already taken
    if any(p["name"] == bot_name for p in players.values()) or any(b["name"] == bot_name for b in bots.values()):
        socketio.server.emit("notification", f"Bot name '{bot_name}' is already taken!", namespace="/")
        return

    player_number = len(players) + len(bots)
    color = player_colors[player_number % len(player_colors)]

    # Bot stats scale with level
    if level == 6:
        speed = 180
        health = 1000
        attack_range = 800
    else:
        speed = 2 + (level - 1) * 0.5
        health = 100 + (level - 1) * 20
        attack_range = 150 + (level - 1) * 25

    bots[bot_id] = {
        "name": bot_name,
        "health": health,
        "max_health": health,
        "x": random.randint(50, 750),
        "y": random.randint(50, 550),
        "color": color,
        "player_number": player_number + 1,
        "vx": random.uniform(-speed, speed),
        "vy": random.uniform(-speed, speed),
        "attack_cooldown": 0,
        "direction_change_timer": random.randint(30, 90),
        "level": level,
        "speed": speed,
        "attack_range": attack_range
    }

    socketio.server.emit("notification", f"Bot '{bot_name}' (Level {level}) spawned!", namespace="/")
    emit_game_state()

@socketio.on("send_chat")
def handle_send_chat(data):
    username = data.get("username", "Anonymous")
    message = data.get("message", "")
    chat_type = data.get("type", "normal")  # "normal" or "team"

    if not message:
        return

    chat_entry = {
        "username": username,
        "message": message,
        "type": chat_type
    }

    saved_chats.append(chat_entry)
    save_chats()

    socketio.server.emit("new_chat", chat_entry, namespace="/")

@socketio.on("request_chats")
def handle_request_chats():
    emit("load_chats", saved_chats)

@socketio.on("connect")
def handle_connect():
    emit("update_highscores", saved_highscores)
    emit("load_chats", saved_chats)

@socketio.on("join")
def handle_join(data):
    username = data["username"]

    # Check if username is already taken by another player
    if any(p["name"] == username for p in players.values()):
        emit("join_error", "You cannot use someone else's name")
        return

    temp_id = random.randint(1000, 9999)
    player_number = len(players)
    color = player_colors[player_number % len(player_colors)]

    previous_score = next((p["score"] for p in saved_highscores if p["name"] == username), 0)

    players[request.sid] = {
        "name": username,
        "score": previous_score,
        "tempId": temp_id,
        "health": 100,
        "x": random.randint(50, 750),
        "y": random.randint(50, 550),
        "color": color,
        "player_number": player_number + 1
    }

    emit("notification", f"{username} joined the game!", broadcast=True)
    emit("join_response", {"player_number": player_number + 1, "color": color})
    emit_game_state()

@socketio.on("move_player")
def handle_move_player(data):
    player = players.get(request.sid)
    if not player:
        return

    x = max(0, min(800, data.get("x", player["x"])))
    y = max(0, min(600, data.get("y", player["y"])))

    player["x"] = x
    player["y"] = y
    emit_game_state()

@socketio.on("attack")
def handle_attack():
    attacker = players.get(request.sid)
    if not attacker:
        return

    directions = [
        {"vx": 0, "vy": -7}, 
        {"vx": 0, "vy": 7}, 
        {"vx": -7, "vy": 0}, 
        {"vx": 7, "vy": 0} 
    ]

    for direction in directions:
        bullets.append({
            "x": attacker["x"],
            "y": attacker["y"],
            "vx": direction["vx"],
            "vy": direction["vy"],
            "owner_sid": request.sid
        })

    emit_game_state()

@socketio.on("update_bullets")
def handle_update_bullets():
    global bullets

    # Update bot AI
    for bot_id, bot in list(bots.items()):
        if bot["level"] == 6 and len(players) > 0:
            closest_player = None
            closest_distance = float('inf')
            for sid, target in players.items():
                distance = math.sqrt((bot["x"] - target["x"])**2 + (bot["y"] - target["y"])**2)
                if distance < closest_distance:
                    closest_distance = distance
                    closest_player = target

            if closest_player:
                dx = closest_player["x"] - bot["x"]
                dy = closest_player["y"] - bot["y"]
                distance = math.sqrt(dx**2 + dy**2)
                if distance > 0:
                    bot["vx"] = (dx / distance) * bot["speed"]
                    bot["vy"] = (dy / distance) * bot["speed"]
        else:
            bot["direction_change_timer"] -= 1
            if bot["direction_change_timer"] <= 0:
                speed = bot["speed"]
                bot["vx"] = random.uniform(-speed, speed)
                bot["vy"] = random.uniform(-speed, speed)
                bot["direction_change_timer"] = random.randint(30, 90)

        bot["x"] += bot["vx"]
        bot["y"] += bot["vy"]

        if bot["x"] < 0: bot["x"] = 800
        elif bot["x"] > 800: bot["x"] = 0
        if bot["y"] < 0: bot["y"] = 600
        elif bot["y"] > 600: bot["y"] = 0

        bot["attack_cooldown"] -= 1

        if bot["attack_cooldown"] <= 0 and len(players) > 0:
            closest_player = None
            closest_distance = float('inf')
            for sid, target in players.items():
                distance = math.sqrt((bot["x"] - target["x"])**2 + (bot["y"] - target["y"])**2)
                if distance < closest_distance:
                    closest_distance = distance
                    closest_player = (sid, target)

            if closest_player and closest_distance < bot["attack_range"]:
                if bot["level"] == 6:
                    for angle in range(0, 360, 1):
                        rad = math.radians(angle)
                        vx = math.cos(rad) * 7
                        vy = math.sin(rad) * 7
                        bullets.append({
                            "x": bot["x"],
                            "y": bot["y"],
                            "vx": vx,
                            "vy": vy,
                            "owner_sid": bot_id
                        })
                    bot["attack_cooldown"] = 12
                else:
                    directions = [
                        {"vx": 0, "vy": -7},
                        {"vx": 0, "vy": 7},
                        {"vx": -7, "vy": 0},
                        {"vx": 7, "vy": 0}
                    ]
                    for direction in directions:
                        bullets.append({
                            "x": bot["x"],
                            "y": bot["y"],
                            "vx": direction["vx"],
                            "vy": direction["vy"],
                            "owner_sid": bot_id
                        })
                    bot["attack_cooldown"] = 10 - (bot["level"] - 1) * 2

    for bullet in bullets:
        bullet["x"] += bullet["vx"]
        bullet["y"] += bullet["vy"]

    bullets = [b for b in bullets if 0 <= b["x"] <= 800 and 0 <= b["y"] <= 600]

    bullets_to_remove = []
    for i, bullet in enumerate(bullets):
        owner = players.get(bullet["owner_sid"]) or bots.get(bullet["owner_sid"])
        if not owner:
            bullets_to_remove.append(i)
            continue

        for sid, target in list(players.items()):
            if sid == bullet["owner_sid"]:
                continue

            distance = math.sqrt((bullet["x"] - target["x"])**2 + (bullet["y"] - target["y"])**2)
            if distance < 25:
                damage = 5
                target["health"] -= damage
                bullets_to_remove.append(i)

                socketio.server.emit("notification", f"{owner['name']}'s bullet hits {target['name']}! ({damage}% damage)", namespace="/")

                if target["health"] <= 0:
                    target["health"] = 0
                    owner["score"] = owner.get("score", 0) + 1

                    if "tempId" in owner:
                        existing = next((p for p in saved_highscores if p["name"] == owner["name"]), None)
                        if existing:
                            existing["score"] = max(existing["score"], owner["score"])
                        else:
                            saved_highscores.append({
                                "name": owner["name"],
                                "score": owner["score"],
                                "tempId": owner["tempId"]
                            })
                        save_highscores()

                    socketio.server.emit("notification", f"{target['name']} was defeated! {owner['name']} wins!", namespace="/")
                    socketio.server.disconnect(sid)
                break

        for bot_id, target in list(bots.items()):
            if bot_id == bullet["owner_sid"]:
                continue

            distance = math.sqrt((bullet["x"] - target["x"])**2 + (bullet["y"] - target["y"])**2)
            if distance < 25:
                damage = 5
                target["health"] -= damage
                bullets_to_remove.append(i)

                socketio.server.emit("notification", f"{owner['name']}'s bullet hits {target['name']}! ({damage}% damage)", namespace="/")

                if target["health"] <= 0:
                    owner["score"] = owner.get("score", 0) + 1

                    if "tempId" in owner:
                        existing = next((p for p in saved_highscores if p["name"] == owner["name"]), None)
                        if existing:
                            existing["score"] = max(existing["score"], owner["score"])
                        else:
                            saved_highscores.append({
                                "name": owner["name"],
                                "score": owner["score"],
                                "tempId": owner["tempId"]
                            })
                        save_highscores()

                    socketio.server.emit("notification", f"{target['name']} was defeated! {owner['name']} wins!", namespace="/")
                    del bots[bot_id]
                break

    for i in sorted(bullets_to_remove, reverse=True):
        if i < len(bullets):
            bullets.pop(i)

    emit_game_state()

@socketio.on("disconnect")
def handle_disconnect():
    if request.sid in players:
        del players[request.sid]
        emit_game_state()
        emit_highscores()

def emit_game_state():
    game_state = []
    for sid, player in players.items():
        game_state.append({
            "sid": sid,
            "name": player["name"],
            "health": player["health"],
            "x": player["x"],
            "y": player["y"],
            "color": player["color"],
            "player_number": player["player_number"]
        })

    for bot_id, bot in bots.items():
        game_state.append({
            "sid": bot_id,
            "name": bot["name"],
            "health": bot["health"],
            "x": bot["x"],
            "y": bot["y"],
            "color": bot["color"],
            "player_number": bot["player_number"]
        })

    bullets_state = [{"x": b["x"], "y": b["y"]} for b in bullets]
    emit("game_state", {"players": game_state, "bullets": bullets_state}, broadcast=True)

def emit_highscores():
    merged = {p["name"]: p for p in saved_highscores}
    for p in players.values():
        merged[p["name"]] = {"name": p["name"], "score": p["score"], "tempId": p["tempId"]}

    sorted_scores = sorted(merged.values(), key=lambda x: x["score"], reverse=True)
    emit("update_highscores", sorted_scores, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=3003, debug=True)
