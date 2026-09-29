import random
def generate_transaction():
    transaction={
    "transaction_id":"TXN001",
    "transaction_amount":random.randint(0,50000),
    "transaction_hour": random.randint(0,23),
    "transaction_type":random.choice(["P2P","P2M"]),
    "device_type":random.choice(["Android", "iOS"]),
    "transactions_last_24h": random.randint(0, 20),
    "account_age_years": random.randint(0, 10),
    "Location_change":random.randint(0,1),
    "is_new_device":random.randint(0,1),
    "failed_attempts":random.randint(0,5)
}
    print(transaction)
    fraud_score=0
    if transaction["transaction_amount"]>30000:
        fraud_score+=2
    if 0 <= transaction["transaction_hour"] <= 5:
          fraud_score+=1
    if transaction["is_new_device"]==1:
         fraud_score+=2
    if transaction["failed_attempts"]>=3:
         fraud_score+=2
    if transaction["transactions_last_24h"]>=10:
         fraud_score+=2
    if transaction["account_age_years"]<=1:
         fraud_score+=2
    if transaction["Location_change"]==1:
         fraud_score+=1
    print(f"the fraud score is {fraud_score}")

    if fraud_score<3:
         print("Risk Level: LOW - Transaction looks normal")
    elif fraud_score<5:
         print("Risk Level: REVIEW - Some suspicious signals detected")
    elif fraud_score<7:
         print("Risk Level: HIGH - Multiple suspicious signals detected")
    elif fraud_score<=8:
        print("Risk Level: CRITICAL - Strong suspicious activity detected")
    else:
         print("Risk Level: VERY HIGH - Additional verification required")
    transaction["fraud_score"]=fraud_score
    return transaction

transaction=generate_transaction()
print(transaction)
