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

# Endpoint: Leggi i dati (Read) con filtro avanzato per Job
@app.route('/api/<entity>', methods=['GET'])
def get_entity(entity):
    if entity not in FILES:
        return jsonify({"error": "Entity not found"}), 404

    try:
        # Leggi il file Excel
        df = read_excel(entity)

        # Converti i nomi delle colonne in lowercase
        df.columns = df.columns.str.lower()

        # Filtra i JOB per razza o abilità
        if entity == "job":
            razza = request.args.get('razza')
            abilita = request.args.get('abilita')
            
            # Confronto case-insensitive
            if razza:
                df = filtroPerColonneMultiple(df, ['razza1', 'razza2', 'razza3'], razza)

            if abilita:
                # Rimuovi spazi dal parametro e trasformalo in lowercase
                abilita = abilita.replace(" ", "").lower()

                # Rimuovi spazi dai valori nella colonna 'nome' e confronta
                df = df[df['nome'].str.replace(" ", "").str.lower().str.contains(abilita)]

        # Filtra le ABILITA per razza, job o nome
        if entity == "abilita":
            razza = request.args.get('razza')
            job = request.args.get('job')
            abilita = request.args.get('abilita')
            
            # filtro delle abilità per razza
            if razza:
                df = filtroPerColonneMultiple(df, ['razza'], razza)

            if job:
                # Rimuovi spazi dal parametro e trasformalo in lowercase
                job = job.replace(" ", "").lower()
                # Rimuovi spazi dai valori nella colonna 'nome' e confronta
                df = df[df['job'].str.replace(" ", "").str.lower().str.contains(job)]

            if abilita:
                # Rimuovi spazi dal parametro e trasformalo in lowercase
                abilita = abilita.replace(" ", "").lower()
                # Rimuovi spazi dai valori nella colonna 'nome' e confronta
                df = df[df['nome'].str.replace(" ", "").str.lower().str.contains(abilita)]

        # Converti i dati filtrati in dizionario
        data = df.to_dict(orient='records')

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

#funzione per filtrare un dizionario per uno o + colonne
def filtroPerColonneMultiple(df, colonne, valore):
    if valore:
        valore = valore.lower()
        # Applica il filtro su tutte le colonne specificate
        conditions = [df[col].str.lower() == valore for col in colonne]
        return df[pd.concat(conditions, axis=1).any(axis=1)]
    return df


# Esegui l'app
if __name__ == "__main__":
    app.run(debug=True)

