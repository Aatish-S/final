import os
import platform
import json
import datetime
import boto3
from botocore.exceptions import ClientError
import time

region = 'ap-south-1'

def login(access_key,secret_access,startdate,enddate):
    session = boto3.Session(
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_access,
    region_name=region
)

    # Now use 'session' to interact with AWS services
    s3 = session.client('s3')

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
    username = input("Enter access key: ")
    password = input("Enter secret access key: ")
    config_data['user']['username'] = username
    config_data['user']['password'] = password
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

            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")

            return date_str
        except ValueError:
            print("Invalid date format. Please enter the date in yyyy-mm-dd format.")

username = "null"
userlogin = 0
exit_commands = {'exit','quit','q','e'}
commands = "1.Login\n2.Monitor Cost\n3.Email Bill\n4.Logout"
config_file_path = 'config.json'

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
            create_user()
        print("\nLogin successful")
        time.sleep(1)
        
            
        
    elif user_input.lower() == '2':
        first_run()
        print("Cost Monitoring...\nPlease enter the dates to analyze the cost")
        date2 = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
        date1 = get_date()

        if username != "null":
            login(username, password,date1,date2)

    elif user_input.lower() == '4':
        log_out()

    elif user_input.lower() == '3':
        first_run()
        recip_email = user_data.get('email')
        if recip_email == "null":
            print("Before using the email, please verify that the email has been configured on aws")
            recip_email = input("Enter your email address:")
            config_data['user']['email'] = recip_email
            save_config(config_data)

        ses_send(recip_email,username,password)
        time.sleep(1)


    print(f"You entered: {user_input}")


