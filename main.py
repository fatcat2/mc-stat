from datetime import datetime
import os
from typing import Dict, List


from flask import Flask, jsonify


app = Flask(__name__)

safe_words = [
        "impaled",
        "pricked",
        "was shot by",
        "fell",
        "pummeled",
        "pricked",
        "drowned",
        "walked into a cactus",
        "kinetic energy",
        "blew up",
        "blown up"
]

LOGFILE = os.getenv("LOGFILE", "/etc/latest.log")

@app.route("/active")
def active_route():
    player_list = active_players()
    return "\n".join(player_list)

@app.route("/death")
def death_route():
    death_list = recently_dead_players()
    return jsonify(death_list)

def active_players() -> List[str]:
    """Helper function that parses logfile to find active players.

    Returns:
        List[str] of active users.
    """
    active_players = set([])
    with open(LOGFILE) as f:
        for line in f.readlines():
            if "<" not in line and ">" not in line and "joined the game" in line:
                user = line.split("]:")[1].strip().split(" ")[0].strip()
                active_players.add(user)
            if "<" not in line and ">" not in line and "left the game" in line:
                user = line.split("]:")[1].strip().split(" ")[0].strip()

                if user in active_players:
                    active_players.remove(user)
    return list(active_players)


def recently_dead_players() -> Dict[int, str]:
    """Helper function to return a dictionary of dead players and the death message.

    Returns:
        Dict[int, str], key is when user died and value is death message.
    """

    dead_players =  {}
    with open(LOGFILE) as f:
        for line in f.readlines():
            if is_death_message(line):
                msg = line.split("]:")[1].strip()
                times = line.split(" ")[0][1:-1].split(":")

                t = datetime.utcnow()

                t.replace(hour=int(times[0]), minute=int(times[1]), second=int(times[2]))

                ts = int(t.timestamp())
                dead_players[ts] = msg
                

    return dead_players


def is_death_message(line: str) -> bool:
    """Helper function to determine whether a player has died.

    Params:
        line (str): log message

    Returns:
        True if death message False if not LOL figure it out
    """

    # chat message
    if "<" in line and ">" in line:
        return False
    
    # if any of these words are in the message
    if any(safe_word in line for safe_word in safe_words):
        return True

    return False





if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5555)
