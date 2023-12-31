import boto3
import json
import sys
from datetime import datetime, timedelta
import csv
import time

with open('config.json', 'r') as config_file:
        config_data = json.load(config_file)
        user_data = config_data.get('user', {})

access_key = user_data.get('username')
secret_access = user_data.get('password')
recip_email = user_data.get('email')
region = 'ap-south-1'

def save_to_csv(date, cost):
    # Append data to the CSV file
    with open('cost_data.csv', 'a', newline='') as csvfile:
        fieldnames = ['Date', 'Cost']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if csvfile.tell() == 0:
            writer.writeheader()

        writer.writerow({'Date': date, 'Cost': cost})

money = sys.argv[1]

with open('cost_data.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Extract date and cost from the CSV row
            date = row['Date']
            cost = float(row['Cost'])


def send_email(date, cost):
    sender_email = 'miniprojectreva@gmail.com'
    recipient_email = recip_email

    ses_client = boto3.client('ses',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_access,
        region_name=region
    )

    subject = f"Cost Exceeded Threshold on {date}"
    body = f"Alert: The cost on {date} has exceeded the threshold. Cost: {cost}"

    response = ses_client.send_email(
        Source=sender_email,
        Destination={'ToAddresses': [recipient_email]},
        Message={
            'Subject': {'Data': subject},
            'Body': {'Text': {'Data': body}}
        }
    )

    print(f"Email sent. Message ID: {response['MessageId']}")



while True:
    if cost > money:
        send_email(date,cost)
        
    ce_client = boto3.client('ce',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_access,
    region_name=region
)
    current_date = datetime.utcnow().strftime('%Y-%m-%d')

    start_date = current_date
    end_date = (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%d')  # Next day

    query = {
        'TimePeriod': {
            'Start': start_date,
            'End': end_date
        },
        'Granularity': 'DAILY',
        'Metrics': ['BlendedCost']
    }

    # Get cost and usage data
    response = ce_client.get_cost_and_usage(**query)

    # Print the total blended cost for the current day
    results_by_time = response['ResultsByTime']
    total_cost = results_by_time[0]['Total']['BlendedCost']['Amount']
    currency = results_by_time[0]['Total']['BlendedCost']['Unit']

    print(f"Total blended cost for {current_date}: {total_cost} {currency}")
    save_to_csv(current_date, total_cost)
    
    time.sleep(86400)



