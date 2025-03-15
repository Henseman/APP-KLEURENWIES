from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__, template_folder="templates", static_folder="static")

# Bestandspad
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
}

# Scores laden
def load_scores():
    if not os.path.exists(SCORES_FILE):
        save_scores({
            "scores": {"Speler 1": 0, "Speler 2": 0, "Speler 3": 0, "Speler 4": 0},
            "namen": {"Speler 1": "Speler 1", "Speler 2": "Speler 2", "Speler 3": "Speler 3", "Speler 4": "Speler 4"},
            "historiek": [],
            "deler": 1,
            "ronde": 1
        })
    try:
        with open(SCORES_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return {
            "scores": {"Speler 1": 0, "Speler 2": 0, "Speler 3": 0, "Speler 4": 0},
            "namen": {"Speler 1": "Speler 1", "Speler 2": "Speler 2", "Speler 3": "Speler 3", "Speler 4": "Speler 4"},
            "historiek": [],
            "deler": 1,
            "ronde": 1
        }

# Scores opslaan
def save_scores(data):
    with open(SCORES_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Laad bestaande scores
scores = load_scores()

@app.route('/')
def index():
    return render_template("index.html", 
                           namen=scores["namen"], 
                           ronde=scores.get("ronde", 1), 
                           deler=scores.get("deler", 1),
                           scores=scores["scores"],
                           historiek=scores["historiek"])

@app.route('/bereken', methods=['POST'])
def bereken():
    global scores
    try:
        data = request.json
        contract = data.get("contract")
        slagen = int(data.get("slagen", 0))
        zetter = data.get("zetter")
        teamgenoten = data.get("teamgenoten", [])

        if contract not in punten_tabel:
            return jsonify({"error": "Ongeldig contract!"}), 400

        info = punten_tabel[contract]

        if not info["team"]:
            teamgenoten = []

        if info["team"] and len(teamgenoten) == 0:
            return jsonify({"error": "Je moet een extra speler aanduiden bij dit contract!"}), 400

        if not info["team"] and len(teamgenoten) > 0:
            return jsonify({"error": "Je mag geen extra spelers aanduiden bij een solo-contract!"}), 400

        if str(zetter) in teamgenoten:
            return jsonify({"error": "De speler die zet mag niet ook als teamgenoot geselecteerd worden!"}), 400

        punten = info["basispunten"] if slagen >= info["minimum_slagen"] else info["verliezen"]

        tegenstanders = [f"Speler {i}" for i in range(1, 5) if str(i) not in [zetter] + teamgenoten]

        if info["team"]:
            for speler in [f"Speler {zetter}"] + [f"Speler {i}" for i in teamgenoten]:
                scores["scores"][speler] += punten
            for speler in tegenstanders:
                scores["scores"][speler] -= punten
        else:
            for speler in tegenstanders:
                scores["scores"][speler] -= punten
            scores["scores"][f"Speler {zetter}"] += punten * 3

        # ✅ Correcte historiek-opslag
        scores["historiek"].append(
            f"Ronde {scores['ronde']}: Contract: {contract}, Zetter: {scores['namen'].get(f'Speler {zetter}', 'Onbekend')}, "
            f"Punten: {punten}"
        )

        scores["ronde"] += 1
        scores["deler"] = (scores["deler"] % 4) + 1

        save_scores(scores)

        return jsonify(scores)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# **🔴 API: Reset scores**
@app.route('/reset', methods=['POST'])
def reset():
    global scores
    scores = {
        "scores": {"Speler 1": 0, "Speler 2": 0, "Speler 3": 0, "Speler 4": 0},
        "namen": {"Speler 1": "Speler 1", "Speler 2": "Speler 2", "Speler 3": "Speler 3", "Speler 4": "Speler 4"},
        "historiek": [],
        "deler": 1,
        "ronde": 1
    }
    save_scores(scores)
    return jsonify({"message": "Scores en historiek gereset!"})

# **✅ Start server**
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
