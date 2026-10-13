# FraudGuard: UPI Transaction Fraud Detection

## Overview

FraudGuard is a machine learning portfolio project designed to estimate the potential fraud risk of UPI transactions. It combines a Random Forest classification model with a web-based dashboard that allows users to enter transaction details and receive a prediction.

The project demonstrates an end-to-end machine learning workflow, including synthetic data analysis, feature engineering, model training, evaluation, and web application integration.

**Note:** This is an educational prototype developed using synthetic data. Its predictions have not been validated for real-world financial transactions.

## Features

- Machine learning-based UPI transaction fraud classification.
- Web dashboard for transaction insights and model metrics.
- Transaction prediction form connected to a Flask backend.
- Feature engineering and input validation.
- Model evaluation using precision, recall, and F1-score.
- Responsive user interface built with HTML and CSS.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Pandas and NumPy | Data processing and analysis |
| Scikit-learn | Machine learning model |
| Random Forest Classifier | Fraud classification |
| Flask | Backend and prediction API |
| HTML and CSS | Frontend interface |
| Joblib | Saving and loading the trained model |
| Jupyter Notebook | Exploratory data analysis |

## Dataset

The project uses a synthetic UPI transaction dataset containing 200,000 records and 29 columns.

| Dataset characteristic | Value |
|---|---:|
| Total transactions | 200,000 |
| Fraud-labelled transactions | 6,400 |
| Fraud-labelled percentage | 3.2% |
| Number of columns | 29 |

The dataset contains transaction-related information such as transaction amount, transaction time, sender and receiver banks, device information, payment methods, and other transaction characteristics.

These records are synthetic and do not represent actual customer transactions.

## Model Performance

The Random Forest model achieved the following results on a held-out synthetic test set.

| Metric | Score |
|---|---:|
| Fraud Precision | 98.04% |
| Fraud Recall | 89.92% |
| Fraud F1-Score | 93.81% |

These results reflect performance on synthetic test data only. They should not be interpreted as evidence of equivalent performance on real-world UPI transactions.

The prediction pipeline and feature preparation require further validation before the model can be considered reliable for practical fraud detection.

## Project Structure

```text
upi-fraud-detection/
├── data/
│   ├── transactions.csv
│   └── upi_fraud_dataset.csv
├── models/
│   ├── upi_fraud_model.pkl
│   └── feature_names.pkl
├── notebooks/
│   └── fraud_analysis.ipynb
├── src/
│   ├── data_generator.py
│   ├── app.py
│   ├── predict.py
│   ├── server.py
│   └── frontend/
│       ├── index.html
│       └── style.css
├── requirements.txt
└── README.md
```

The exact files may vary depending on which parts of the project are included in the repository.

## Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd upi-fraud-detection
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your actual repository URL.

### 2. Create a virtual environment

On Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If Flask is not listed in your requirements file, install it with:

```bash
pip install flask
```

### 4. Run the application

Start the Flask backend from the project root:

```bash
python src/server.py
```

Open the following address in your browser:

```text
http://127.0.0.1:5000
```

The trained model and feature-name files must be available in the expected `models/` directory.

## How It Works

1. Transaction details are entered through the web interface.
2. The Flask backend receives the submitted information.
3. Python validates the