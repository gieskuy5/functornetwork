import requests
import jwt
from datetime import datetime
import time
import os

class SimplifiedAccountManager:
    def __init__(self):
        self.clear_screen()
        self.banner = """    ______                 __              
   / ____/_  ______  _____/ /_____  _____  
  / /_  / / / / __ \/ ___/ __/ __ \/ ___/  
 / __/ / /_/ / / / / /__/ /_/ /_/ / /      
/_/ _  \__,_/_/_/_/\___/\__/\____/_/   __  
   / | / /__  / /__      ______  _____/ /__
  /  |/ / _ \/ __/ | /| / / __ \/ ___/ //_/
 / /|  /  __/ /_ | |/ |/ / /_/ / /  / ,<   
/_/ |_/\___/\__/ |__/|__/\____/_/  /_/|_|  
                                           """
    
    def clear_screen(self):
        """Clear console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_banner(self):
        """Display ASCII art banner and contact information"""
        print(self.banner)
        print("===============================================")
        print("GitHub  : https://github.com/gieskuy5")
        print("Telegram: https://t.me/giemdfk")
        print("===============================================")

    def read_accounts(self):
        """Read accounts from akun.txt file"""
        accounts = []
        try:
            with open('akun.txt', 'r') as file:
                for line in file:
                    email, password = line.strip().split(':')
                    accounts.append({'email': email, 'password': password})
            return accounts
        except FileNotFoundError:
            print("Error: File akun.txt tidak ditemukan")
            return []
        except Exception as e:
            print(f"Error membaca file: {str(e)}")
            return []

    def login(self, email, password):
        """Login to API"""
        url = "https://api.securitylabs.xyz/v1/auth/signin-user"
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Origin': 'https://node.securitylabs.xyz',
            'Referer': 'https://node.securitylabs.xyz/',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.6'
        }
        
        payload = {
            "email": email,
            "password": password
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                return response.json()
            else:
                error_message = response.json().get('message', 'Unknown error') if response.text else f"HTTP {response.status_code}"
                return {"error": error_message}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def perform_checkin(self, access_token, user_id):
        """Perform checkin"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Origin': 'https://node.securitylabs.xyz',
            'Referer': 'https://node.securitylabs.xyz/'
        }
        checkin_url = f"https://api.securitylabs.xyz/v1/users/earn/{user_id}"
        try:
            response = requests.get(checkin_url, headers=headers)
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def get_user_info(self, access_token):
        """Get user information"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Origin': 'https://node.securitylabs.xyz',
            'Referer': 'https://node.securitylabs.xyz/'
        }
        url = "https://api.securitylabs.xyz/v1/users"
        response = requests.get(url, headers=headers)
        return response.json()

    def get_balance(self, access_token, user_id):
        """Get user balance"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Origin': 'https://node.securitylabs.xyz',
            'Referer': 'https://node.securitylabs.xyz/'
        }
        balance_url = f"https://api.securitylabs.xyz/v1/users/get-balance/{user_id}"
        response = requests.get(balance_url, headers=headers)
        return response.json()

    def process_accounts(self):
        """Process all accounts once"""
        accounts = self.read_accounts()
        if not accounts:
            return False

        for account in accounts:
            print(f"[ + ] Trying to login with email: {account['email']}")
            login_response = self.login(account['email'], account['password'])
            
            if 'accessToken' in login_response:
                print(f"[ + ] Login Successfull")
                token_data = jwt.decode(login_response['accessToken'], options={"verify_signature": False})
                user_id = token_data['sub']
                
                # Get user info and balance
                user_info = self.get_user_info(login_response['accessToken'])
                balance_data = self.get_balance(login_response['accessToken'], user_id)
                
                print(f"[ + ] Name      : {user_info.get('name', 'N/A')}")
                print(f"[ + ] Balance   : {balance_data.get('dipTokenBalance', 0)}")
                
                # Check for checkin availability
                init_mine_time = user_info.get('dipInitMineTime')
                if init_mine_time:
                    next_checkin = datetime.strptime(init_mine_time, "%Y-%m-%dT%H:%M:%S.%fZ")
                    time_diff = datetime.now() - next_checkin
                    hours_remaining = 24 - (time_diff.total_seconds() / 3600)
                    
                    if hours_remaining > 0:
                        print(f"[ + ] ⏰ Time to next checkin: {hours_remaining:.2f} hours")
                    else:
                        checkin_result = self.perform_checkin(login_response['accessToken'], user_id)
                        if 'error' in checkin_result:
                            print(f"[ - ] Checkin failed: {checkin_result['error']}")
                        else:
                            print(f"[ + ] Checkin successful: +{checkin_result.get('tokensToAward', 0)} DIP")
                else:
                    print("[ + ] Checkin already claimed")
            else:
                print(f"[ - ] Login Failed: {login_response.get('error', 'Unknown error')}")
            
            print()  # Empty line between accounts
            time.sleep(2)  # Wait between accounts
        
        return True

    def run(self):
        """Main program with 2-hour cycle"""
        try:
            while True:
                self.clear_screen()
                self.display_banner()
                
                if self.process_accounts():
                    print(f"[ * ] All accounts processed. Waiting 2 hours before next cycle...")
                    # Display countdown timer
                    for remaining in range(7200, 0, -1):  # 7200 seconds = 2 hours
                        hours, remainder = divmod(remaining, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        print(f"\r[ * ] Next cycle in: {hours:02d}:{minutes:02d}:{seconds:02d}", end='')
                        time.sleep(1)
                    print("\n")  # New line after countdown
                else:
                    print("[ - ] No accounts found. Please check akun.txt file.")
                    break

        except KeyboardInterrupt:
            print("\n[ ! ] Program stopped by user")

if __name__ == "__main__":
    manager = SimplifiedAccountManager()
    manager.run()