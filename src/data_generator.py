import random
import pandas as pd 
def generate_transaction(number):
    hours=list(range(24)) 
    weights=[1,1,1,1,1,1,3,3,3,5,5,5,5,5,5,5,5,5,5,5,5,5,5,2]
    transaction_type=["P2P","P2M"]
    transaction_type_weight=[7,3]
    transaction={
     "transaction_id":f"TXN{number:04}",
    "transaction_amount":max(0,random.gauss(5000,3000)),
    "transaction_hour": random.choices(population=hours,weights=weights,k=1)[0],
    "transaction_type":random.choice(transaction_type,transaction_type_weight=transaction_type_weight,k=1)[0],
    "device_type":random.choice(["Android", "iOS"]),
    "transactions_last_24h": random.randint(0, 20),
    "account_age_years": random.randint(0, 10),
    "Location_change":random.randint(0,1),
    "is_new_device":random.randint(0,1),
    "failed_attempts":random.randint(0,5)
}
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
         risk_level="Low"
    elif fraud_score<5:
          risk_level="Review"
    elif fraud_score<7:
          risk_level="High"
    elif fraud_score<=8:
          risk_level="CRITICAL"
    else:
          risk_level="Very high"
    transaction["fraud_score"]=fraud_score
    transaction["risk_level"]=risk_level
    return transaction
number = int(input("How many transactions do you want? "))
transaction=[]
for i in range(number):
     transaction_new=generate_transaction(i+1)
     transaction.append(transaction_new)
# print(transaction)
df=pd.DataFrame(transaction)
# print(df)
df.to_csv("../data/transactions.csv",index=False)
