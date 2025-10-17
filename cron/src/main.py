# import time
from flask import Flask, request, jsonify
from model.infer import predict

app = Flask(__name__)

@app.route("/predict", methods=["POST"])
def predict_route():
    data= request.get_json()
    text= data.get("text", "").strip()
    if not text:
        return jsonify({"error": "Brak tekstu do analizy."}), 400
    
    try:
        ai_prob=predict(text)
        return jsonify({"text":text, "ai_probability": ai_prob, "human_probability": 100 - ai_prob}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# def loop():
#     print("⏳ Waiting for tasks...")


if __name__ == "__main__":
    print("Cron started!")

    app.run(host="0.0.0.0", port=8080)

