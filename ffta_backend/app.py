from flask import Flask, jsonify, request
import pandas as pd

app = Flask(__name__)

# Percorsi dei file Excel
FILES = {
    "razze": "data/razze.xlsx",
    "job": "data/job.xlsx",
    "abilita": "data/abilita.xlsx",
}

# Funzione per leggere i file Excel
def read_excel(entity):
    return pd.read_excel(FILES[entity])

# Funzione per scrivere nei file Excel
def write_excel(entity, data):
    df = pd.DataFrame(data)
    df.to_excel(FILES[entity], index=False)

# Endpoint: Leggi i dati (Read)
@app.route('/api/<entity>', methods=['GET'])
def get_entity(entity):
    if entity not in FILES:
        return jsonify({"error": "Entity not found"}), 404

    try:
        data = read_excel(entity).to_dict(orient='records')
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint: Aggiungi un nuovo record (Create)
@app.route('/api/<entity>', methods=['POST'])
def add_entity(entity):
    if entity not in FILES:
        return jsonify({"error": "Entity not found"}), 404

    try:
        # Leggi il nuovo record dal corpo della richiesta
        new_record = request.json
        df = read_excel(entity)
        
        # Usa pd.concat invece di append
        new_row = pd.DataFrame([new_record])
        df = pd.concat([df, new_row], ignore_index=True)
        
        write_excel(entity, df)
        return jsonify({"message": "Record added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Endpoint: Aggiorna un record esistente (Update)
@app.route('/api/<entity>/<int:record_id>', methods=['PUT'])
def update_entity(entity, record_id):
    if entity not in FILES:
        return jsonify({"error": "Entity not found"}), 404

    try:
        # Leggi i dati aggiornati dal corpo della richiesta
        updated_record = request.json
        df = read_excel(entity)

        if record_id >= len(df):
            return jsonify({"error": "Record not found"}), 404

        # Aggiorna il record
        for key, value in updated_record.items():
            df.loc[record_id, key] = value

        write_excel(entity, df)
        return jsonify({"message": "Record updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint: Elimina un record (Delete)
@app.route('/api/<entity>/<int:record_id>', methods=['DELETE'])
def delete_entity(entity, record_id):
    if entity not in FILES:
        return jsonify({"error": "Entity not found"}), 404

    try:
        df = read_excel(entity)

        if record_id >= len(df):
            return jsonify({"error": "Record not found"}), 404

        # Elimina il record
        df = df.drop(index=record_id)
        write_excel(entity, df)
        return jsonify({"message": "Record deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Esegui l'app
if __name__ == "__main__":
    app.run(debug=True)
