from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from predict import predict_fraud

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = Flask(
    __name__,
    static_folder=str(FRONTEND_DIR),
    static_url_path="/frontend"
)


@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        input_data = request.get_json(silent=True)

        if not isinstance(input_data, dict):
            return jsonify({"error": "Please submit transaction details as JSON."}), 400

        required_fields = [
            "amount_inr",
            "hour_of_day",
            "day_of_week",
            "sender_age_group",
            "sender_avg_amount_30d",
        ]
        missing_fields = [field for field in required_fields if field not in input_data]
        if missing_fields:
            return jsonify({
                "error": "Missing required fields: " + ", ".join(missing_fields)
            }), 400

        result = predict_fraud(input_data)
        prediction = int(result["prediction"])

        return jsonify({
            "prediction": prediction,
            "fraud_probability": float(result["fraud_probability"]),
            "message": (
                "Potential Fraud Detected"
                if prediction == 1
                else "Likely Legitimate Transaction"
            ),
        })

    except Exception as error:
        return jsonify({"error": str(error)}), 400


if __name__ == "__main__":
    app.run(debug=True)
