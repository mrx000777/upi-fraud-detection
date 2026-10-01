"""
UPI Fraud Detection - Synthetic Dataset Generator
===================================================
Generates a large, realistic, labeled dataset of UPI (Unified Payments
Interface) transactions for a fraud-detection portfolio project.

IMPORTANT / HONESTY NOTE (also see DATA_SOURCES.md):
No bank, NPCI, or the RBI publishes real transaction-level UPI data to the
public (for obvious privacy/regulatory reasons) - what circulates online as
"UPI fraud datasets" (Kaggle, GitHub, etc.) is, without exception, synthetic
data too. This script generates its own synthetic dataset from scratch,
engineered to mirror the feature sets and fraud typologies seen across the
real published research + public synthetic datasets referenced in
DATA_SOURCES.md, rather than literally merging files that don't actually
exist in a downloadable, licensed form.

The result is a single combined-style CSV with:
  - realistic Indian UPI transaction fields (VPA, bank, state, device, app)
  - behavioural/velocity features used in real fraud models
  - several distinct fraud typologies, each with its own feature signature
  - deliberate label noise so the problem isn't trivially separable
"""

import csv
import random
import uuid
from datetime import datetime, timedelta
import numpy as np
from faker import Faker

fake = Faker("en_IN")
Faker.seed(42)
random.seed(42)
np.random.seed(42)

N_ROWS = 200_000
FRAUD_RATE = 0.032  # ~3.2% - in line with industry-reported digital-payment fraud rates

# ---------------------------------------------------------------- reference data
BANKS = [
    ("State Bank of India", "oksbi"), ("HDFC Bank", "okhdfcbank"),
    ("ICICI Bank", "okicici"), ("Axis Bank", "okaxis"),
    ("Kotak Mahindra Bank", "kotak"), ("Punjab National Bank", "pnb"),
    ("Bank of Baroda", "barodampay"), ("Canara Bank", "cnrb"),
    ("Union Bank of India", "unionbank"), ("IDFC First Bank", "idfcbank"),
    ("Yes Bank", "ybl"), ("Paytm Payments Bank", "paytm"),
    ("Indian Bank", "indianbank"), ("IndusInd Bank", "indus"),
]

APPS = ["Google Pay", "PhonePe", "Paytm", "BHIM", "Amazon Pay", "WhatsApp Pay"]
APP_WEIGHTS = [0.34, 0.33, 0.18, 0.06, 0.06, 0.03]

STATES = [
    "Maharashtra", "Uttar Pradesh", "Karnataka", "Tamil Nadu", "Delhi",
    "Gujarat", "West Bengal", "Rajasthan", "Madhya Pradesh", "Punjab",
    "Telangana", "Andhra Pradesh", "Bihar", "Kerala", "Haryana",
    "Odisha", "Assam", "Jharkhand", "Chhattisgarh", "Uttarakhand",
]
STATE_WEIGHTS = np.array([14, 11, 9, 8, 7, 7, 6, 5, 5, 5, 5, 4, 4, 4, 3, 2, 2, 2, 1, 1], dtype=float)
STATE_WEIGHTS /= STATE_WEIGHTS.sum()

DEVICE_TYPES = ["Android", "iOS"]
NETWORKS = ["Mobile Data", "WiFi"]

MERCHANT_CATEGORIES = [
    "Grocery", "Food Delivery", "Shopping", "Bill Payment", "Mobile Recharge",
    "Fuel", "Entertainment", "Travel & Transport", "Healthcare", "Education",
    "Investment", "Gaming", "Rent", "Insurance", "DTH/Cable",
]
MERCHANT_WEIGHTS = np.array([14, 11, 11, 10, 9, 8, 7, 7, 6, 5, 4, 3, 3, 1, 1], dtype=float)
MERCHANT_WEIGHTS /= MERCHANT_WEIGHTS.sum()

FRAUD_TYPES = [
    "Phishing Link", "Fake QR Code", "Fake Payment Request", "SIM Swap",
    "Account Takeover", "Social Engineering (Vishing)", "Money Mule Transfer",
    "Fake Customer Care", "Lottery/Prize Scam", "Investment Scam",
]

AGE_GROUPS = ["18-25", "26-35", "36-45", "46-60", "60+"]
AGE_WEIGHTS = [0.22, 0.33, 0.21, 0.16, 0.08]

START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2024, 12, 31, 23, 59, 59)
TOTAL_SECONDS = int((END_DATE - START_DATE).total_seconds())


def random_timestamp():
    return START_DATE + timedelta(seconds=random.randint(0, TOTAL_SECONDS))


def make_vpa(name_hint, bank_suffix):
    base = "".join(ch for ch in name_hint.lower().replace(" ", ".") if ch.isalnum() or ch == ".")
    num = random.randint(1, 9999)
    return f"{base}{num}@{bank_suffix}"


def pick_bank():
    return random.choice(BANKS)


def generate_rows(n):
    rows = []

    # Pre-build a pool of "sender personas" so the same sender appears across
    # multiple transactions with consistent bank/state/device/behavioural baseline
    # -- this is what makes velocity & "new payee" features meaningful.
    n_senders = max(2000, n // 12)
    senders = []
    for _ in range(n_senders):
        name = fake.name()
        bank_name, bank_suffix = pick_bank()
        state = np.random.choice(STATES, p=STATE_WEIGHTS)
        age_group = np.random.choice(AGE_GROUPS, p=AGE_WEIGHTS)
        device = random.choice(DEVICE_TYPES)
        avg_amount = float(np.random.lognormal(mean=6.6, sigma=0.9))  # ~ INR 300-4000 typical
        senders.append({
            "name": name,
            "vpa": make_vpa(name, bank_suffix),
            "bank": bank_name,
            "state": state,
            "age_group": age_group,
            "device": device,
            "avg_amount": round(min(avg_amount, 25000), 2),
            "known_payees": set(),
            "txn_count": 0,
        })

    # a pool of merchant/person receivers reused across transactions
    n_receivers = max(3000, n // 8)
    receivers = []
    for _ in range(n_receivers):
        is_merchant = random.random() < 0.55
        if is_merchant:
            cat = np.random.choice(MERCHANT_CATEGORIES, p=MERCHANT_WEIGHTS)
            name = fake.company()
        else:
            cat = "P2P Transfer"
            name = fake.name()
        bank_name, bank_suffix = pick_bank()
        receivers.append({
            "name": name,
            "vpa": make_vpa(name, bank_suffix),
            "bank": bank_name,
            "category": cat,
            "is_merchant": is_merchant,
        })

    n_fraud_target = int(n * FRAUD_RATE)
    fraud_flags = np.array([1] * n_fraud_target + [0] * (n - n_fraud_target))
    np.random.shuffle(fraud_flags)

    # receivers grouped by category, for mild category skew on fraud rows
    receivers_by_category = {}
    for r in receivers:
        receivers_by_category.setdefault(r["category"], []).append(r)
    fraud_prone_categories = ["Investment", "Gaming", "Travel & Transport", "P2P Transfer"]

    for i in range(n):
        sender = random.choice(senders)
        is_fraud = bool(fraud_flags[i])

        ts = random_timestamp()
        if is_fraud and random.random() < 0.55:
            # fraud skews toward late-night / early-morning hours
            night_hour = random.choice([23, 0, 1, 2, 3, 4])
            ts = ts.replace(hour=night_hour, minute=random.randint(0, 59), second=random.randint(0, 59))
        hour = ts.hour
        is_night = hour >= 23 or hour < 5
        is_weekend = ts.weekday() >= 5

        # --- choose receiver & payee familiarity -------------------------
        if is_fraud and random.random() < 0.78:
            # fraud overwhelmingly targets a payee the sender has not paid before,
            # with a mild skew toward historically fraud-prone categories
            if random.random() < 0.4:
                cat = random.choice(fraud_prone_categories)
                receiver = random.choice(receivers_by_category.get(cat, receivers))
            else:
                receiver = random.choice(receivers)
            is_new_payee = receiver["vpa"] not in sender["known_payees"]
            if random.random() < 0.9:
                is_new_payee = True  # force for a fresh-looking scam payee most of the time
        else:
            if sender["known_payees"] and random.random() < 0.6:
                receiver = random.choice(
                    [r for r in receivers if r["vpa"] in sender["known_payees"]]
                    or [random.choice(receivers)]
                )
                is_new_payee = False
            else:
                receiver = random.choice(receivers)
                is_new_payee = receiver["vpa"] not in sender["known_payees"]

        sender["known_payees"].add(receiver["vpa"])
        sender["txn_count"] += 1

        txn_type = "P2M" if receiver["is_merchant"] else "P2P"
        merchant_category = receiver["category"]

        # --- amount --------------------------------------------------------
        base_amount = float(np.random.lognormal(mean=np.log(max(sender["avg_amount"], 50)), sigma=0.55))
        if is_fraud:
            # fraud amounts cluster either unusually high (scam payout) or
            # suspiciously round "testing" amounts
            if random.random() < 0.65:
                amount = base_amount * np.random.uniform(3, 18)
            else:
                amount = float(random.choice([1, 2, 10, 50, 100, 500]))
        else:
            amount = base_amount
        amount = round(min(max(amount, 1), 200000), 2)
        amount_to_avg_ratio = round(amount / max(sender["avg_amount"], 1), 2)

        # --- velocity / behavioural features --------------------------------
        if is_fraud and random.random() < 0.55:
            sender_txn_count_24h = np.random.poisson(9) + 3
        else:
            sender_txn_count_24h = np.random.poisson(2)

        payee_txn_count_30d = 0 if is_new_payee else np.random.poisson(4) + 1

        # --- device / network risk signals ----------------------------------
        if is_fraud and random.random() < 0.5:
            device_change_flag = True
        else:
            device_change_flag = random.random() < 0.03

        if is_fraud and random.random() < 0.22:
            sim_change_recent_flag = True
        else:
            sim_change_recent_flag = random.random() < 0.01

        network_type = np.random.choice(NETWORKS, p=[0.72, 0.28])
        app = np.random.choice(APPS, p=APP_WEIGHTS)

        # --- outcome status ---------------------------------------------------
        if is_fraud:
            status = np.random.choice(["SUCCESS", "FAILED"], p=[0.84, 0.16])
        else:
            status = np.random.choice(["SUCCESS", "FAILED", "PENDING"], p=[0.94, 0.045, 0.015])

        # --- fraud typology assignment (adds realistic sub-structure) --------
        fraud_type = ""
        if is_fraud:
            if sim_change_recent_flag and device_change_flag:
                fraud_type = np.random.choice(["SIM Swap", "Account Takeover"], p=[0.6, 0.4])
            elif merchant_category == "Investment":
                fraud_type = "Investment Scam"
            elif merchant_category in ("Grocery", "Fuel", "Shopping") and txn_type == "P2M":
                fraud_type = np.random.choice(["Fake QR Code", "Phishing Link"], p=[0.6, 0.4])
            elif is_night and is_new_payee:
                fraud_type = np.random.choice(
                    ["Fake Payment Request", "Social Engineering (Vishing)", "Phishing Link"],
                    p=[0.4, 0.35, 0.25],
                )
            else:
                fraud_type = np.random.choice(
                    ["Money Mule Transfer", "Fake Customer Care", "Lottery/Prize Scam", "Phishing Link"],
                    p=[0.3, 0.25, 0.2, 0.25],
                )
            # small amount of label noise: ~6% of fraud rows get no strong
            # feature signature at all (mimics real-world "clean-looking" fraud)
            if random.random() < 0.06:
                device_change_flag = False
                sim_change_recent_flag = False
                is_new_payee = random.random() < 0.3

        # a touch of noise on the legit side too: ~1.5% look a bit risky but aren't fraud
        if not is_fraud and random.random() < 0.015:
            device_change_flag = True
            amount = round(amount * np.random.uniform(2, 5), 2)

        rows.append({
            "transaction_id": f"TXN{uuid.uuid4().hex[:12].upper()}",
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "hour_of_day": hour,
            "day_of_week": ts.strftime("%A"),
            "is_weekend": is_weekend,
            "is_night": is_night,
            "sender_vpa": sender["vpa"],
            "sender_bank": sender["bank"],
            "sender_state": sender["state"],
            "sender_age_group": sender["age_group"],
            "is_senior_citizen": sender["age_group"] == "60+",
            "sender_device_type": sender["device"],
            "receiver_vpa": receiver["vpa"],
            "receiver_bank": receiver["bank"],
            "transaction_type": txn_type,
            "merchant_category": merchant_category,
            "payment_app": app,
            "network_type": network_type,
            "amount_inr": amount,
            "transaction_status": status,
            "is_new_payee": is_new_payee,
            "sender_txn_count_last_24h": int(sender_txn_count_24h),
            "payee_txn_count_last_30d": int(payee_txn_count_30d),
            "sender_avg_amount_30d": sender["avg_amount"],
            "amount_to_avg_ratio": amount_to_avg_ratio,
            "device_change_flag": device_change_flag,
            "sim_change_recent_flag": sim_change_recent_flag,
            "is_fraud": int(is_fraud),
            "fraud_type": fraud_type,
        })

    return rows


if __name__ == "__main__":
    print(f"Generating {N_ROWS:,} rows...")
    data = generate_rows(N_ROWS)
    random.shuffle(data)  # de-correlate from generation order

    fieldnames = list(data[0].keys())
    out_path = "/home/claude/upi_dataset/upi_fraud_dataset.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    n_fraud = sum(r["is_fraud"] for r in data)
    print(f"Done. Wrote {len(data):,} rows to {out_path}")
    print(f"Fraud rows: {n_fraud:,} ({n_fraud/len(data)*100:.2f}%)")
