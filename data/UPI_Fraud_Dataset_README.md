# UPI Fraud Detection Dataset — Data Dictionary & Notes

## File
`upi_fraud_dataset.csv` — 200,000 rows × 29 columns, ~49 MB.
Fraud rate: **3.2%** (6,400 fraudulent transactions) — deliberately imbalanced
to match real-world digital-payment fraud rates (published research puts UPI/
digital-payment fraud rates in the 2–8% range depending on definition).

## ⚠️ Please read before you present this anywhere

**This is a synthetic dataset.** No real UPI transaction-level data is
publicly available anywhere — not on Kaggle, not on GitHub, not from NPCI/RBI
— because releasing it would violate banking privacy law. Every "UPI fraud
dataset" you'll find online (Kaggle included) is synthetic for the same
reason. See `DATA_SOURCES.md` for exactly what's out there and what this
dataset is modeled on.

That's not a weakness to hide — it's completely standard for this kind of
project (the same is true of the popular PaySim and IEEE-CIS fraud datasets
everyone uses for portfolio work). Just be upfront about it if asked in an
interview: *"I built a synthetic dataset with realistic UPI transaction
patterns and multiple fraud typologies, modeled on the structure of public
research and datasets in this space, since real transaction data isn't
publicly releasable."* That's a genuinely good answer — it shows you
understand the data, not just that you downloaded a CSV.

## Column reference

| Column | Type | Description |
|---|---|---|
| `transaction_id` | string | Unique transaction reference (TXN + hex) |
| `timestamp` | datetime | Transaction date & time (2023–2024) |
| `hour_of_day` | int (0–23) | Hour extracted from timestamp |
| `day_of_week` | string | Day name |
| `is_weekend` | bool | Saturday/Sunday flag |
| `is_night` | bool | Between 11 PM and 5 AM (common fraud window) |
| `sender_vpa` | string | Sender's UPI Virtual Payment Address |
| `sender_bank` | string | Sender's bank |
| `sender_state` | string | Sender's Indian state (population-weighted) |
| `sender_age_group` | string | 18-25 / 26-35 / 36-45 / 46-60 / 60+ |
| `is_senior_citizen` | bool | Age group 60+ |
| `sender_device_type` | string | Android / iOS |
| `receiver_vpa` | string | Receiver's UPI VPA |
| `receiver_bank` | string | Receiver's bank |
| `transaction_type` | string | P2P (person-to-person) or P2M (to merchant) |
| `merchant_category` | string | Category for P2M, "P2P Transfer" otherwise |
| `payment_app` | string | Google Pay / PhonePe / Paytm / BHIM / etc. |
| `network_type` | string | Mobile Data / WiFi |
| `amount_inr` | float | Transaction amount in ₹ |
| `transaction_status` | string | SUCCESS / FAILED / PENDING |
| `is_new_payee` | bool | First time this sender has paid this receiver |
| `sender_txn_count_last_24h` | int | Velocity feature — sender's txn count in 24h |
| `payee_txn_count_last_30d` | int | How often this sender has paid this payee in 30d |
| `sender_avg_amount_30d` | float | Sender's typical (baseline) transaction size |
| `amount_to_avg_ratio` | float | This transaction's amount ÷ sender's baseline — a key anomaly signal |
| `device_change_flag` | bool | Transaction made from an unrecognized/new device |
| `sim_change_recent_flag` | bool | SIM changed recently on sender's number |
| `is_fraud` | int (0/1) | **Target variable** |
| `fraud_type` | string | Fraud typology (empty for legitimate transactions) |

## Fraud typologies included

| Type | Typical signature baked into the data |
|---|---|
| SIM Swap / Account Takeover | `device_change_flag` + `sim_change_recent_flag` both true |
| Fake QR Code | P2M at Grocery/Fuel/Shopping with payee mismatch |
| Phishing Link | New payee, often at night, mixed category |
| Fake Payment Request | New payee, night-time, P2P |
| Social Engineering (Vishing) | New payee, night-time, elevated amount |
| Money Mule Transfer | High velocity, unusual amount jump |
| Fake Customer Care | New payee, round "testing" amounts |
| Lottery/Prize Scam | New payee, round amounts, broad time spread |
| Investment Scam | Merchant category = Investment, high amount |

## Deliberately realistic imperfections

A clean, perfectly-separable dataset makes for a boring (and unrealistic)
ML project, so:
- **~6% of fraud rows carry no strong risk signal** (no device/SIM change,
  familiar-looking payee) — mimics sophisticated fraud that evades
  obvious rules.
- **~1.5% of legitimate rows look risky** (device change + amount spike)
  but are not fraud — mimics false-positive-prone legitimate behaviour
  (e.g., genuinely buying a new phone, one unusually large but real gift).

This means a model that only memorizes `device_change_flag` or
`is_new_payee` will plateau well short of 100% — you'll need real feature
engineering and a sensible precision/recall trade-off, same as a real
fraud team would.

## Suggested starting points for the portfolio project

- **EDA**: fraud rate by hour/day, by merchant category, by state
- **Class imbalance handling**: SMOTE / class weights / undersampling
- **Feature engineering**: you already have velocity + baseline-deviation
  features; try adding payee-network features (how many distinct senders
  pay this receiver) for a graph-style angle
- **Models**: Logistic Regression baseline → Random Forest/XGBoost →
  compare precision/recall/PR-AUC (not just accuracy — with 3.2% fraud,
  accuracy is a meaningless metric)
- **Explainability**: SHAP values on the tree model make a strong
  portfolio talking point for a fraud use case
