# What's actually publicly available, and what this dataset is modeled on

I looked for real, downloadable UPI fraud datasets before building this.
Here's the honest landscape:

## Why there's no real one to "combine"

UPI transaction data is held by NPCI and individual banks and is covered by
banking-privacy regulation in India — it is never released at the
transaction level, to anyone, for any reason. The only UPI data NPCI
publishes publicly is **aggregate statistics** (e.g. monthly transaction
volume/value by bank, by state) — useful for a macro dashboard, useless for
a row-level fraud classifier. See: https://www.npci.org.in and
aggregator sites like https://dataful.in/datasets/?q=UPI for those
aggregate stats if you ever want a companion macro-trends chart.

## What people actually use instead (and cite as "UPI fraud datasets")

| Source | What it actually is |
|---|---|
| Kaggle — `skullagos5246/upi-transactions-2024-dataset` | Synthetic simulated UPI transactions (merchant category, state, device, senior-citizen flag) |
| Kaggle — `willianoliveiragibin` UPI Payment dataset | Synthetic, only ~1,000 rows, sender/receiver VPA fields |
| Kaggle — PaySim (`ealaxi/paysim1`) | Synthetic **mobile-money** simulation (not UPI-specific, but the most commonly reused dataset in "UPI fraud detection" student projects/papers) |
| Kaggle — IEEE-CIS Fraud Detection | Real e-commerce card-not-present fraud (Vesta Corp) — not UPI, but a common stand-in for feature-engineering practice |
| Kaggle — `mlg-ulb/creditcardfraud` | Real European credit-card fraud, heavily anonymized (PCA-transformed features) |
| Hugging Face — `AgamiAI/Indian-Bank-Statements` | Synthetic Indian bank statements incl. UPI line items — explicitly **no fraud labels** |
| Academic papers (e.g. Atlantis Press, SDMIMD conference proceedings) | Nearly all state they trained on a "synthetic dataset" or on PaySim — confirming no real labeled UPI fraud data is used anywhere in published research either |

None of these are a single authoritative "UPI fraud dataset" — and none of
them were downloadable here without a Kaggle login (Kaggle requires
authentication for CSV downloads, which this environment doesn't have).

## What I built instead

Rather than present a login-walled Kaggle file as something I'd "combined,"
I generated a new synthetic dataset from scratch (`generate.py` in this
folder — fully readable/editable) engineered to carry the **same feature
categories** these sources use in combination:

- Transaction/merchant structure → from the `upi-transactions-2024-dataset` style
- VPA sender/receiver fields → from the `willianoliveiragibin` style
- Velocity + behavioural-deviation features → standard in PaySim/IEEE-CIS-style fraud modeling
- Device/SIM-change risk signals + named fraud typologies → from the applied
  UPI fraud research papers found during search (SDMIMD conference
  proceedings, Atlantis Press chapter on ML-based UPI fraud detection)

This gives you a single, large, internally-consistent CSV that's realistic
enough to do real feature engineering and model evaluation on, without
misrepresenting where the data came from.

## If you want to add a *real* dataset alongside this one

Two genuinely real, downloadable options worth layering in for comparison
or extra practice (both need a free Kaggle account):

1. **PaySim** — `kaggle datasets download -d ealaxi/paysim1` (synthetic but
   widely cited; same mobile-money transaction shape UPI papers reuse)
2. **Credit Card Fraud (ULB)** — `kaggle datasets download -d mlg-ulb/creditcardfraud`
   (real fraud labels, though features are PCA-anonymized so there's
   limited feature-engineering story to tell)

If you set up a Kaggle API token (`~/.kaggle/kaggle.json`) you can pull
either with the `kaggle` CLI and `pd.concat`/merge them alongside this
dataset's schema for an even larger combined corpus.
