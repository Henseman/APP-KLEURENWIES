from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__, template_folder="templates", static_folder="static")

# Bestandspaden
SCORES_FILE = "data/scores.json"

# Puntentabel voor Kleurenwies
punten_tabel = {
    "Samen 8": {"basispunten": 8, "verliezen": -11, "overslag": 3, "minimum_slagen": 8, "team": True},
    "Solo 5": {"basispunten": 3, "verliezen": -4, "overslag": 1, "minimum_slagen": 5, "team": False},
    "Samen 9": {"basispunten": 11, "verliezen": -14, "overslag": 3, "minimum_slagen": 9, "team": True},
    "Solo 6": {"basispunten": 4, "verliezen": -5, "overslag": 1, "minimum_slagen": 6, "team": False},
    "Samen 10": {"basispunten": 14, "verliezen": -17, "overslag": 3, "minimum_slagen": 10, "team": True},
    "Solo 7": {"basispunten": 5, "verliezen": -6, "overslag": 1, "minimum_slagen": 7, "team": False},
    "Samen 11": {"basispunten": 17, "verliezen": -20, "overslag": 3, "minimum_slagen": 11, "team": True},
    "Kleine Miserie": {"basispunten": 6, "verliezen": -6, "overslag": 0, "minimum_slagen": 0, "max_slagen": 0, "team": False},
    "Samen 12": {"basispunten": 20, "verliezen": -23, "overslag": 3, "minimum_slagen": 12, "team": True},
    "Solo 8": {"basispunten": 7, "verliezen": -8, "overslag": 1, "minimum_slagen": 8, "team": False},
    "Piccolo": {"basispunten": 8, "verliezen": -8, "overslag": 0, "minimum_slagen": 1, "max_slagen": 1, "team": False},
    "Samen 13": {"basispunten": 30, "verliezen": -26, "overslag": 0, "minimum_slagen": 13, "team": True},
    "Solo 9": {"basispunten": 10, "verliezen": -10, "overslag": 5, "minimum_slagen": 9, "team": False},
    "Troel 8": {"basispunten": 16, "verliezen": -16, "overslag": 0, "minimum_slagen": 8, "team": True},
    "Miserie": {"basispunten": 12, "verliezen": -12, "overslag": 0, "minimum_slagen": 0, "max_slagen": 0, "team": False},
    "Solo 10": {"basispunten": 15, "verliezen": -15, "overslag": 0, "minimum_slagen": 10, "team": False},
    "Solo 11": {"basispunten": 20, "verliezen": -20, "overslag": 0, "minimum_slagen": 11, "team": False},
    "Open Miserie": {"basispunten": 24, "verliezen": -24, "overslag": 0, "minimum_slagen": 0, "max_slagen": 0, "team": False},
    "Solo 12": {"basispunten": 30, "verliezen": -30, "overslag": 0, "minimum_slagen": 9, "team": False},
    "Solo Slim 13": {"basispunten": 60, "verliezen": -60, "overslag": 0, "minimum_slagen": 0, "team": False},
    }

# Scores laden
def load_scores():
    try:
        with open(SCORES_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {
            "scores": {"Speler 1": 0, "Speler 2": 0, "Speler 3": 0, "Speler 4": 0},
            "namen": {"Speler 1": "Speler 1", "Speler 2": "Speler 2", "Speler 3": "Speler 3", "Speler 4": "Speler 4"},
            "historiek": []
        }

# Scores opslaan
def save_scores(data):
    with open(SCORES_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Laad bestaande scores
scores = load_scores()

@app.route('/')
def index():
    return render_template("index.html", namen=scores["namen"])

@app.route('/bereken', methods=['POST'])
def bereken():
    global scores
    data = request.json
    contract = data.get("contract")
    slagen = int(data.get("slagen", 0))
    zetter = data.get("zetter")
    teamgenoten = data.get("teamgenoten", [])

   if contract in punten_tabel:
    info = punten_tabel[contract]

 # ✅ Als een speler 13 slagen haalt, is de score altijd 30 punten
    if slagen == 13:
        punten = 30   
        
 # ✅ Toegevoegde code voor Kleine Miserie
    if contract == "Kleine Miserie" and slagen > info["max_slagen"]:
        punten = info["verliezen"]  # Speler haalt slagen → verlies
    elif contract == "Kleine Miserie":
        punten = info["basispunten"]  # Speler haalt geen slagen → winst

 # ✅ Toegevoegde code voor Miserie
    if contract == "Miserie" and slagen > info["max_slagen"]:
        punten = info["verliezen"]  # Speler haalt slagen → verlies
    elif contract == "Miserie":
        punten = info["basispunten"]  # Speler haalt geen slagen → winst

 # ✅ Toegevoegde code voor Open Miserie
    if contract == "Open Miserie" and slagen > info["max_slagen"]:
        punten = info["verliezen"]  # Speler haalt slagen → verlies
    elif contract == "Open Miserie":
        punten = info["basispunten"]  # Speler haalt geen slagen → winst

 # ✅ Toegevoegde code voor Piccolo
    if contract == "Piccolo" and slagen > info["max_slagen"]:
        punten = info["verliezen"]  # Speler haalt slagen → verlies
    elif contract == "Piccolo":
        punten = info["basispunten"]  # Speler haalt geen slagen → winst
       
    # ✅ Standaardberekening voor andere contracten
    elif slagen >= info["minimum_slagen"]:
        overslagen = max(0, slagen - info["minimum_slagen"])
        punten = info["basispunten"] + (overslagen * info["overslag"])
    else:
        punten = info["verliezen"]
    else:
        punten = 0

    tegenstanders = [f"Speler {i}" for i in range(1, 5) if str(i) not in [zetter] + teamgenoten]

    # ** Correctie van de puntentelling **
    if not info["team"]:  # Solo-spellen (1 tegen 3)
        for speler in tegenstanders:
            scores["scores"][speler] -= punten  # 3 tegenstanders verliezen punten
        scores["scores"][f"Speler {zetter}"] += punten * 3  # Zetter krijgt punten van alle 3 tegenstanders

    else:  # Team-spellen (2 tegen 2)
        for speler in [f"Speler {zetter}"] + [f"Speler {i}" for i in teamgenoten]:
            scores["scores"][speler] += punten
        for speler in tegenstanders:
            scores["scores"][speler] -= punten

    scores["historiek"].append(f"Contract: {contract}, Zetter: Speler {zetter}, Punten: {punten}")

    save_scores(scores)
    return jsonify({"punten": punten, "scores": scores["scores"], "historiek": scores["historiek"]})

@app.route('/update_score', methods=['POST'])
def update_score():
    global scores
    data = request.json
    speler = data.get("speler")
    nieuwe_score = data.get("score")

    if speler in scores["scores"]:
        scores["scores"][speler] = nieuwe_score
        save_scores(scores)

    return jsonify({"scores": scores["scores"]})

@app.route('/reset', methods=['POST'])
def reset():
    global scores
    scores = {
        "scores": {"Speler 1": 0, "Speler 2": 0, "Speler 3": 0, "Speler 4": 0},
        "namen": {"Speler 1": "Speler 1", "Speler 2": "Speler 2", "Speler 3": "Speler 3", "Speler 4": "Speler 4"},
        "historiek": []
    }
    save_scores(scores)
    return jsonify({"message": "Scores en historiek gereset!"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
