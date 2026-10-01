import random
import pandas as pd 
def generate_transaction(number):
    hours=list(range(24)) 
    weights=[1,1,1,1,1,1,3,3,3,5,5,5,5,5,5,5,5,5,5,5,5,5,5,2]
    transaction_type=["P2P","P2M"]
    transaction_type_weight=[7,3]
    device_type=["Android","iOS"]
    device_type_weight=[7,3]
    low=[0,1,2,3]
    medium=[4,5,6,7,8,9]
    high=[10,11,12,13,14,15]
    rare=[16,17,18,19,20]
    transaction_count=low+medium+high+rare
    transaction_count_weight=[7,7,7,7,4,4,4,4,4,4,2,2,2,2,2,2,1,1,1,1,1]
    new_account=[0,1]
    establish_account=[2,3,4,5]
    old_account=[6,7,8,9,10]
    all_account=new_account+establish_account+old_account
    all_account_weight=[1,1,5,5,5,5,2,2,2,2,2]
    location_change = [0, 1]
    location_change_weight=[7,3]
    is_new_device=[0,1]
    is_new_device_weight=[6,4]
    low_attempts=[0,1,2]
    medium_attempts=[3]
    high_attempts=[4,5]
    total_falied_attempts=low_attempts+medium_attempts+high_attempts
    total_falied_attempts_weight=[6,6,6,3,1,1]

    transaction={
     "transaction_id":f"TXN{number:04}",
    "transaction_amount":max(0,random.gauss(5000,3000)),
    "transaction_hour": random.choices(hours,weights=weights,k=1)[0],
    "transaction_type":random.choices(transaction_type,weights=transaction_type_weight,k=1)[0],
    "device_type":random.choices(device_type,weights=device_type_weight,k=1)[0],
    "transactions_last_24h": random.choices(transaction_count,weights=transaction_count_weight,k=1)[0],
    "account_age_years": random.choices(all_account,weights=all_account_weight,k=1)[0],
    "Location_change":random.choices(location_change,weights=location_change_weight,k=1)[0],
    "is_new_device":random.choices(is_new_device,weights=is_new_device_weight,k=1)[0],
    "failed_attempts":random.choices(total_falied_attempts,weights=total_falied_attempts_weight,k=1)[0]
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
