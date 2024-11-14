from library import *
import os


x = 17  # Starting row index (inclusive) Row starts from 0 x=2 means Row 3
y = 22  # Ending row index (exclusive) 15 Row pomints to 14 row, but since it starts from 0 it points to 15 row


# Access secrets from environment variables
repo_owner = os.getenv('REPO_OWNER')
repo_name = os.getenv('REPO_NAME')
file_path = os.getenv('FILE_PATH')
token = os.getenv('TOKEN')
login_admin_bohit_token= os.getenv('LOGIN_TOKEN')
admin_chatID = os.getenv('ADMIN_CHATID')





# GitHub API URL to get raw content of the file
url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}'

# Fetch the JSON file metadata from the private repo
headers = {'Authorization': f'token {token}'}
response = requests.get(url, headers=headers)

if response.status_code == 200:
    # Debug: Print the full response to check the structure
    print("Response JSON structure:", response.json())

    # Get the download URL for the file
    download_url = response.json().get('download_url')

    # Fetch the raw file content using the download URL
    file_response = requests.get(download_url)

    if file_response.status_code == 200:
        # Load the JSON data from the file content
        data = file_response.json()
    else:
        print(f"Failed to fetch the file content: {file_response.status_code}")
        exit(1)
else:
    print(f"Failed to fetch file metadata: {response.status_code}")
    print(response.text)  # Print the error message from the response body
    exit(1)

# First row contains the headers (column names)
headers = data[0]

# Define your range of rows to process (x to y)


accounts = []
for row in data[x:y]:
    # Skip row if any cell is empty or only contains spaces
    if any(cell is None or str(cell).strip() == "" for cell in row):
        continue

    # Skip row if "Status" is False
    status_index = headers.index("Status")
    if row[status_index] is False:
        continue

    # Add account to list if it passes both checks
    account = dict(zip(headers, row))
    accounts.append(account)
    
def refresh_account(account):
    username = account["Username"]
    password = account["Password"]
    user_both_chatID = str(account["user_both_chatID"])
    account_name = account["Account_name"]
    user_both_token = account["user_both_token"]  # Same token for all accounts
    start_time = account["start_time"]
    end_time = account["end_time"]
    accept_option = account["accept_option"]
    
    
    # Set up Chrome WebDriver for this account
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Each account gets its own Chrome instance
    driver = webdriver.Chrome(options=options)

    # Attempt to log in
    flag_login = True
    while flag_login:
        flag_login = login_to_chegg(username, password, driver)
    login_texts = f"both currently active on {account_name}"
    #telegram_both_sendtext(login_texts,user_both_token,user_both_chatID)
    telegram_both_sendtext(login_texts,login_admin_bohit_token,admin_chatID)


    # Start refreshing for the account
    refresh_chegg(driver, accept_option, start_time, end_time, user_both_token, user_both_chatID, account_name)
    #exit_texts = f"Loop exit on {account_name}"
    #telegram_both_sendtext(exit_texts,user_both_token,user_both_chatID)  
if __name__ == "__main__":
    # Create a process for each account
    processes = []
    for account in accounts:
        process = multiprocessing.Process(target=refresh_account, args=(account,))
        processes.append(process)
        process.start()

    # Optionally join the processes to ensure the script waits for all to finish
    for process in processes:
        process.join()
