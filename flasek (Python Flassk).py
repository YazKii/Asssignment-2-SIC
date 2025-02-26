from flask import Flask, request, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

mongoDBku = os.getenv("MONGODB_URI", "mongodb+srv://sigma:sigma@has.k1ypw.mongodb.net/?retryWrites=true&w=majority&appName=Has")
DBku = "sic"
koleksyen = "sigma"

client = MongoClient(mongoDBku)
db = client[DBku]
collection = db[koleksyen]

@app.route('/save', methods=["POST"])
def save_data():
    try:
        data = request.get_json()
        suhu = data.get("suhu")
        kelembaban = data.get("kelembaban")

        if suhu is None or kelembaban is None:
            return jsonify({"error": "Suhu dan kelembaban harus diisi!"}), 400
        if not isinstance(suhu, (int, float)) or not isinstance(kelembaban, (int, float)):
            return jsonify({"error": "Data harus berupa angka!"}), 400

        simpan = {"suhu": suhu, "kelembaban": kelembaban}
        collection.insert_one(simpan)
        
        return jsonify({"message": "success"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5003)

