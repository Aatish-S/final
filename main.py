import os
import platform
import json
import datetime
from datetime import timedelta,datetime
import boto3
from botocore.exceptions import ClientError
import time
import subprocess

region = 'ap-south-1'
username = "null"
userlogin = 0
exit_commands = {'exit','quit','q','e'}
commands = "1.Login\n2.Monitor Cost\n3.Email Bill\n4.Cost Alarm\n5.Logout"
config_file_path = 'config.json'

def userlogver(access_key,secret_access):
    ce_client = boto3.client('ce',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_access,
    region_name=region
)
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')

    try:
        response = ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity='DAILY',
            Metrics=['BlendedCost']
        )

    except Exception as e:
        print("INVALID CREDENTIALS!!!\nPlease check your credentials")
        return False
    
    return True

def cost_alarm(recip_email,cost_alrm):
    if cost_alrm == 'ready':
        money = input("Enter the daily budget limit for sending an email notification( in $ ): ")  
        command = ["python", "child_script.py", money]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    else:
        print("Please run Email Bill command before cost alarm and setup email notification!!!")


def login(access_key,secret_access,startdate,enddate):
    session = boto3.Session(
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_access,
    region_name=region
)

    ce = session.client('ce')
    response_ce = ce.get_cost_and_usage(TimePeriod={'Start':startdate,
                                        'End':enddate},
                                        Granularity='MONTHLY',
                                        Metrics=['BlendedCost'])

    for result in response_ce['ResultsByTime']:
            print(f"Start Date: {result['TimePeriod']['Start']}, End Date: {result['TimePeriod']['End']}")
            print(f"Blended Cost: {result['Total']['BlendedCost']['Amount']} {result['Total']['BlendedCost']['Unit']}")
            print("-" * 50)

    with open('cost_data.txt', 'w') as file:
        # Iterate through the results and write to the file
        for result in response_ce['ResultsByTime']:
            file.write(f"Start Date: {result['TimePeriod']['Start']}, End Date: {result['TimePeriod']['End']}\n")
            file.write(f"Blended Cost: {result['Total']['BlendedCost']['Amount']} {result['Total']['BlendedCost']['Unit']}\n")
            file.write("-" * 50 + "\n")
    
    exi = input("...")
    
def create_user():
    print("Creating user...")
    username = input("Enter access key: ")
    password = input("Enter secret access key: ")
    if userlogver(username, password) == False:
        create_user()
    else:
        config_data['user']['username'] = username
        config_data['user']['password'] = password
        config_data['user']['cost_alarm'] = 'null'
        save_config(config_data)

def ses_send(recip_email, username, password):
    with open('cost_data.txt', 'r') as file:
        email_body = file.read()

    sender_email = 'miniprojectreva@gmail.com'
    recipient_email = recip_email

    if 'Blended Cost' in email_body:
        ses_client = boto3.client('ses',
    aws_access_key_id=username,
    aws_secret_access_key=password,
    region_name=region
)
        try:
            response = ses_client.send_email(
                Source=sender_email,
                Destination={
                    'ToAddresses': [recipient_email],
                },
                Message={
                    'Subject': {
                        'Data': 'Cost Data Report',
                },
                'Body': {
                    'Text': {
                        'Data': email_body,
                    },
                },
            },
        )
            print("Email sent! Message ID:", response['MessageId'])

        except ClientError as e:
            print("Error:", e.response['Error']['Message'])
    else:
        print("Billing report not found in the email. Email will not be sent.")
        time.sleep(2)

def log_out():
    config_data['user']['username'] = "null"
    config_data['user']['password'] = "null"
    config_data['user']['email'] = "null"
    save_config(config_data)

def user_login():
    username = user_data.get('username')
    password = user_data.get('password')
    recip_email = user_data.get('email')
    

def get_date():
    while True:
        try:
            # Get user input
            date_str = input(f"Enter a date for (yyyy-mm-dd): ")

            date_obj = datetime.strptime(date_str, "%Y-%m-%d")

            return date_str
        except ValueError:
            print("Invalid date format. Please enter the date in yyyy-mm-dd format.")

def load_config():
    with open(config_file_path, 'r') as config_file:
        return json.load(config_file)

# Save user data to the config file
def save_config(config_data):
    with open(config_file_path, 'w') as config_file:
        json.dump(config_data, config_file, indent=4)

def first_run():
    system_info = platform.system()
    if system_info == 'Windows':
        os.system('cls')
    elif system_info == 'Linux':
        os.system('clear') 
    

while True:
    with open('config.json', 'r') as config_file:
        config_data = json.load(config_file)
        user_data = config_data.get('user', {})
    first_run()
    username = user_data.get('username')
    password = user_data.get('password')
    cost_alrm = user_data.get('cost_alarm')
    print("\nUsername = ",username)
    if username == "null":
        print("No User Login\n")
    print(commands)
    
    user_input = input("\nEnter a command (or 'exit' to quit): ")
    

    if user_input.lower() in exit_commands:
        print("Exiting the program. Goodbye!")
        break
    

    if user_input.lower() == '1':
        user_login()
        if username == "null":
            first_run()
            create_user()
        print("\nLogin successful")
        exi = input("...")
        
            
        
    elif user_input.lower() == '2':
        first_run()
        print("Cost Monitoring...\nPlease enter the dates to analyze the cost")
        date2 = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        date1 = get_date()

        if username != "null":
            login(username, password,date1,date2)

    elif user_input.lower() == '5':
        log_out()

    elif user_input.lower() == '3':
        first_run()
        recip_email = user_data.get('email')
        if recip_email == "null":
            print("Before using the email, please verify that the email has been configured on aws")
            recip_email = input("Enter your email address:")
        try:
            ses_send(recip_email,username,password)
        except Exception as e:
            print("Email ID error")
            time.sleep(3)
        else:
            config_data['user']['email'] = recip_email
            config_data['user']['cost_alarm'] = 'ready'
            save_config(config_data)
        time.sleep(1)

    if user_input.lower() == '4':
        recip_email = user_data.get('email')
        first_run()
        cost_alarm(recip_email,cost_alrm)
        time.sleep(2)

    print(f"You entered: {user_input}")


