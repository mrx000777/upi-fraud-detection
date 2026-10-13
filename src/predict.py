
from pathlib import Path

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "upi_fraud_model.pkl"
FEATURES_PATH = BASE_DIR / "models" / "feature_names.pkl"


def load_model_and_features():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}")

    if not FEATURES_PATH.exists():
        raise FileNotFoundError(f"Feature list not found: {FEATURES_PATH}")

    model = joblib.load(MODEL_PATH)
    feature_names = list(joblib.load(FEATURES_PATH))

    if model.n_features_in_ != len(feature_names):
        raise ValueError(
            f"Model expects {model.n_features_in_} features, "
            f"but feature list contains {len(feature_names)}."
        )

    if len(feature_names) != len(set(feature_names)):
        raise ValueError("The feature list contains duplicate feature names.")

    return model, feature_names


def prepare_input(input_data, feature_names):
    data = input_data.copy()

    required_fields = [
        "amount_inr",
        "hour_of_day",
        "day_of_week",
        "sender_age_group",
        "sender_avg_amount_30d",
    ]

    missing_fields = [
        field for field in required_fields if field not in data
    ]

    if missing_fields:
        raise ValueError(
            "Missing required fields: " + ", ".join(missing_fields)
        )

    try:
        data["amount_inr"] = float(data["amount_inr"])
        data["hour_of_day"] = int(data["hour_of_day"])
        data["sender_avg_amount_30d"] = float(
            data["sender_avg_amount_30d"]
        )
    except (TypeError, ValueError):
        raise ValueError("Amount and hour fields must contain valid numbers.")

    if data["amount_inr"] <= 0:
        raise ValueError("Transaction amount must be greater than zero.")

    if not 0 <= data["hour_of_day"] <= 23:
        raise ValueError("Transaction hour must be between 0 and 23.")

    if data["sender_avg_amount_30d"] <= 0:
        raise ValueError(
            "Average transaction amount must be greater than zero."
        )

    valid_days = {
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday"
    }

    if data["day_of_week"] not in valid_days:
        raise ValueError("Invalid day of week.")

    valid_age_groups = {"18-25", "26-35", "36-45", "46-60", "60+"}

    if data["sender_age_group"] not in valid_age_groups:
        raise ValueError("Invalid sender age group.")

    hour = data["hour_of_day"]

    data["is_night"] = int(hour <= 4 or hour == 23)
    data["is_weekend"] = int(
        data["day_of_week"] in {"Saturday", "Sunday"}
    )
    data["is_senior_citizen"] = int(
        data["sender_age_group"] == "60+"
    )
    data["amount_to_avg_ratio"] = (
        data["amount_inr"] / data["sender_avg_amount_30d"]
    )

    input_df = pd.DataFrame([data])

    input_df = pd.get_dummies(
        input_df,
        columns=[
            column
            for column in [
                "day_of_week",
                "sender_age_group",
                "sender_bank",
                "sender_state",
                "sender_device_type",
                "receiver_bank",
                "transaction_type",
                "merchant_category",
                "payment_app",
                "network_type",
            ]
            if column in input_df.columns
        ],
        dtype=int,
    )

    input_df = input_df.reindex(
        columns=feature_names,
        fill_value=0,
    )

    input_df = input_df.apply(pd.to_numeric, errors="raise")

    if input_df.isnull().any().any():
        raise ValueError("Prepared features contain missing values.")

    return input_df


def predict_fraud(input_data):
    model, feature_names = load_model_and_features()
    prepared = prepare_input(input_data, feature_names)

    prediction = int(model.predict(prepared)[0])
    probabilities = model.predict_proba(prepared)[0]

    classes = list(model.classes_)
    fraud_index = classes.index(1) if 1 in classes else None

    if fraud_index is None:
        raise ValueError(
            "The trained model does not contain fraud class 1."
        )

    return {
        "prediction": prediction,
        "fraud_probability": float(probabilities[fraud_index]),
        "prepared_features": prepared.shape[1],
    }


if __name__ == "__main__":
    model, feature_names = load_model_and_features()

    print("Model loaded:", model.__class__.__name__)
    print("Expected features:", model.n_features_in_)
    print("Feature count matches:", model.n_features_in_ == len(feature_names))

    sample = {
        "hour_of_day": 23,
        "day_of_week": "Saturday",
        "sender_age_group": "60+",
        "amount_inr": 5000,
        "sender_avg_amount_30d": 1000,
    }

    prepared = prepare_input(sample, feature_names)

    print("Prepared shape:", prepared.shape)
    print("Night:", prepared["is_night"].iloc[0])
    print("Weekend:", prepared["is_weekend"].iloc[0])
    print("Senior citizen:", prepared["is_senior_citizen"].iloc[0])
    print("Amount ratio:", prepared["amount_to_avg_ratio"].iloc[0])

    result = predict_fraud(sample)

    print("Predicted class:", result["prediction"])
    print("Fraud probability:", f'{result["fraud_probability"]:.2%}')
