import json
import os

FILE = "highscore.json"

def load_highscore():
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            return json.load(f).get("highscore", 0)
    return 0

def save_highscore(highscore):
    with open(FILE, "w") as f:
        json.dump({"highscore": highscore}, f)
