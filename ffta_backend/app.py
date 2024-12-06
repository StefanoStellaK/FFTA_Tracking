from flask import Flask, jsonify, request
import pandas as pd

app = Flask(__name__)

# Percorsi dei file Excel
FILES = {
    "razze": "data/razze.xlsx",
    "job": "data/job.xlsx",
    "abilita": "data/abilita.xlsx",
}

# Endpoint per ottenere dati
@app.route('/api/<entity>', methods=['GET'])
def get_entity(entity):
    if entity not in FILES:
        return jsonify({"error": "Entity not found"}), 404

    # Leggi il file Excel
    try:
        data = pd.read_excel(FILES[entity]).to_dict(orient='records')
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Esegui l'app
if __name__ == "__main__":
    app.run(debug=True)
