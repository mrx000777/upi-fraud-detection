
import streamlit as st
from predict import load_model_and_features, prepare_input

st.set_page_config(
    page_title="UPI Fraud Detection",
    layout="wide"
)

model, feature_names = load_model_and_features()

st.sidebar.title("FraudGuard")
st.sidebar.caption("UPI Transaction Intelligence")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Fraud Prediction",
        "Transaction Explorer",
        "Model Performance"
    ]
)

st.title("UPI Fraud Detection")
st.caption("Machine learning powered transaction monitoring")

if page == "Dashboard":
    st.subheader("Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Transactions", "200,000")
    col2.metric("Fraudulent Transactions", "6,400")
    col3.metric("Fraud Rate", "3.2%")
    col4.metric("Model Recall", "89.92%")

    st.divider()
    st.subheader("Welcome to FraudGuard")
    st.write(
        "Explore transaction patterns, assess potential fraud risk, "
        "and review model performance."
    )

elif page == "Fraud Prediction":
    st.subheader("Check a UPI Transaction")
    st.write("Enter transaction details to assess potential fraud risk.")

    with st.form("fraud_prediction_form"):
        col1, col2 = st.columns(2)

        with col1:
            amount = st.number_input(
                "Transaction Amount (₹)",
                min_value=1.0,
                value=1500.0,
                step=100.0
            )

            hour = st.slider("Hour of Transaction", 0, 23, 14)

            day = st.selectbox(
                "Day of Week",
                [
                    "Monday", "Tuesday", "Wednesday", "Thursday",
                    "Friday", "Saturday", "Sunday"
                ]
            )

            month = st.selectbox("Month", list(range(1, 13)), index=9)

            sender_bank = st.selectbox(
                "Sender Bank",
                [
                    "Axis Bank", "Bank of Baroda", "Canara Bank",
                    "HDFC Bank", "ICICI Bank", "IDFC First Bank",
                    "Indian Bank", "IndusInd Bank",
                    "Kotak Mahindra Bank", "Paytm Payments Bank",
                    "Punjab National Bank", "State Bank of India",
                    "Union Bank of India", "Yes Bank"
                ]
            )

            sender_state = st.selectbox(
                "Sender State",
                [
                    "Andhra Pradesh", "Assam", "Bihar", "Chhattisgarh",
                    "Delhi", "Gujarat", "Haryana", "Jharkhand",
                    "Karnataka", "Kerala", "Madhya Pradesh",
                    "Maharashtra", "Odisha", "Punjab", "Rajasthan",
                    "Tamil Nadu", "Telangana", "Uttar Pradesh",
                    "Uttarakhand", "West Bengal"
                ]
            )

            age_group = st.selectbox(
                "Sender Age Group",
                ["18-25", "26-35", "36-45", "46-60", "60+"]
            )

            receiver_bank = st.selectbox(
                "Receiver Bank",
                [
                    "Axis Bank", "Bank of Baroda", "Canara Bank",
                    "HDFC Bank", "ICICI Bank", "IDFC First Bank",
                    "Indian Bank", "IndusInd Bank",
                    "Kotak Mahindra Bank", "Paytm Payments Bank",
                    "Punjab National Bank", "State Bank of India",
                    "Union Bank of India", "Yes Bank"
                ]
            )

        with col2:
            transaction_type = st.selectbox(
                "Transaction Type", ["P2P", "P2M"]
            )

            merchant_category = st.selectbox(
                "Merchant Category",
                [
                    "Bill Payment", "DTH/Cable", "Education",
                    "Entertainment", "Food Delivery", "Fuel",
                    "Gaming", "Grocery", "Healthcare", "Insurance",
                    "Investment", "Mobile Recharge", "P2P Transfer",
                    "Rent", "Shopping", "Travel & Transport"
                ]
            )

            payment_app = st.selectbox(
                "Payment App",
                [
                    "Amazon Pay", "BHIM", "Google Pay",
                    "Paytm", "PhonePe", "WhatsApp Pay"
                ]
            )

            network_type = st.selectbox(
                "Network Type", ["Mobile Data", "WiFi"]
            )

            device_type = st.selectbox(
                "Sender Device Type", ["Android", "iOS"]
            )

            is_new_payee = st.checkbox("New payee?")
            device_change = st.checkbox("Recent device change?")
            sim_change = st.checkbox("Recent SIM change?")

            sender_txn_count = st.number_input(
                "Sender Transactions in Last 24 Hours",
                min_value=0,
                max_value=100,
                value=2
            )

            payee_txn_count = st.number_input(
                "Payee Transactions in Last 30 Days",
                min_value=0,
                max_value=10000,
                value=10
            )

            sender_avg_amount = st.number_input(
                "Sender Average Amount (Last 30 Days, ₹)",
                min_value=0.01,
                value=1000.0,
                step=100.0
            )

        submitted = st.form_submit_button(
            "Assess Transaction Risk",
            use_container_width=True
        )

    if submitted:
        input_data = {
            "hour_of_day": hour,
            "day_of_week": day,
            "month": month,
            "amount_inr": amount,
            "sender_avg_amount_30d": sender_avg_amount,
            "amount_to_avg_ratio": amount / sender_avg_amount,
            "is_new_payee": is_new_payee,
            "sender_txn_count_last_24h": sender_txn_count,
            "payee_txn_count_last_30d": payee_txn_count,
            "device_change_flag": device_change,
            "sim_change_recent_flag": sim_change,
            "is_senior_citizen": age_group == "60+",
            "is_weekend": day in ["Saturday", "Sunday"],
            "is_night": hour <= 4 or hour == 23,
            "sender_bank": sender_bank,
            "sender_state": sender_state,
            "sender_age_group": age_group,
            "receiver_bank": receiver_bank,
            "transaction_type": transaction_type,
            "merchant_category": merchant_category,
            "payment_app": payment_app,
            "network_type": network_type,
            "sender_device_type": device_type
        }

        try:
            prepared = prepare_input(input_data, feature_names)
            
            
            prediction = model.predict(prepared)[0]
            probability = model.predict_proba(prepared)[0][1]

            st.subheader("Assessment Result")

            if prediction == 1:
                st.error("The model classifies this transaction as potentially fraudulent.")
            else:
                st.success("The model classifies this transaction as likely legitimate.")

            st.metric("Estimated Fraud Probability", f"{probability:.2%}")
            st.caption(
                "This is a model estimate, not confirmation that a transaction is fraudulent."
            )

        except Exception as error:
            st.error(f"Unable to assess transaction: {error}")

elif page == "Transaction Explorer":
    st.subheader("Transaction Explorer")
    st.info("Dataset exploration will be added here.")

elif page == "Model Performance":
    st.subheader("Model Performance")
    st.info("Evaluation metrics will be added here.")
