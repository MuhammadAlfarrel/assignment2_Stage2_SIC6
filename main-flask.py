from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

uri = "mongodb+srv://rifqiraehan86:YWwDS3dtPQDUdoI5@cluster0.lkusi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(uri)
db = client.MyDatabase
collection = db.SensorData

@app.route("/sensor", methods=["POST"])
def receive_sensor_data():
    try:
        data = request.get_json()
        if data and "distance" in data:
            distance = data["distance"]
            timestamp = datetime.now()
            sensor_data = {"distance": distance, "timestamp": timestamp}
            collection.insert_one(sensor_data)
            return jsonify({"message": "Data received and saved"}), 200
        else:
            return jsonify({"error": "Invalid data"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)