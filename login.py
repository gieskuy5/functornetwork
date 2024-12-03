import requests
import json
import time
from datetime import datetime, timedelta
import threading
import sys
import os
from colorama import init, Fore, Style

# Initialize colorama
init()

ASCII_ART = f"""{Fore.CYAN}
______                _               _   _      _                      _    
|  ___|              | |             | \\ | |    | |                    | |   
| |_ _   _ _ __   ___| |_ ___  _ __  |  \\| | ___| |___      _____  _ __| | __
|  _| | | | '_ \\ / __| __/ _ \\| '__| | . ` |/ _ \\ __\\ \\ /\\ / / _ \\| '__| |/ /
| | | |_| | | | | (__| || (_) | |    | |\\  |  __/ |_ \\ V  V / (_) | |  |   < 
\\_|  \\__,_|_| |_|\\___|\__\\___/|_|    \\_| \\_/\\___|\\__| \\_/\\_/ \\___/|_|  |_|\\_\\
{Style.RESET_ALL}"""

class OpenLoopNode:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.access_token = None
        self.base_url = 'https://api.openloop.so'
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.last_checkin_time = None

    def login(self):
        """Login to OpenLoop API"""
        url = f'{self.base_url}/users/login'
        payload = {
            'username': self.email,
            'password': self.password
        }
        
        try:
            print(f"{Fore.BLUE}| INFO    |{Style.RESET_ALL} Processing account: {self.email}")
            response = requests.post(url, json=payload, headers=self.headers)
            data = response.json()
            
            if data['code'] == 2000:
                self.access_token = data['data']['accessToken']
                self.headers['Authorization'] = f'Bearer {self.access_token}'
                print(f"{Fore.GREEN}| SUCCESS |{Style.RESET_ALL} Login successful!")
                return True
            else:
                print(f"{Fore.RED}| ERROR   |{Style.RESET_ALL} Login failed: {data['message']}")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}| ERROR   |{Style.RESET_ALL} Login error: {str(e)}")
            return False

    def get_point_balance(self):
        """Get current point balance"""
        try:
            url = f'{self.base_url}/bandwidth/info'
            response = requests.get(url, headers=self.headers)
            data = response.json()
            
            if data['code'] == 2000:
                balance = data['data']['balances'].get('POINT', 0)
                print(f"{Fore.BLUE}| INFO    |{Style.RESET_ALL} Balance: {balance}")
                return balance
            return 0
        except Exception as e:
            print(f"{Fore.RED}| ERROR   |{Style.RESET_ALL} Error getting balance: {str(e)}")
            return 0

    def checkin(self):
        """Perform daily checkin"""
        try:
            url = f'{self.base_url}/bandwidth/share'
            payload = {"quality": 100}
            
            response = requests.post(url, json=payload, headers=self.headers)
            data = response.json()
            
            if data['code'] == 2000:
                print(f"{Fore.GREEN}| SUCCESS |{Style.RESET_ALL} Success checkin {data.get('data', {}).get('point', 'unknown')} points")
                self.last_checkin_time = datetime.now()
                return True
            else:
                print(f"{Fore.RED}| ERROR   |{Style.RESET_ALL} Already checkin")
                return False
        except Exception as e:
            print(f"{Fore.RED}| ERROR   |{Style.RESET_ALL} Error during checkin: {str(e)}")
            return False

def read_accounts(filename):
    """Read accounts from file"""
    accounts = []
    try:
        with open(filename, 'r') as file:
            for line in file:
                if ':' in line:
                    email, password = line.strip().split(':')
                    accounts.append({'email': email, 'password': password})
    except FileNotFoundError:
        print(f"{Fore.RED}| ERROR   |{Style.RESET_ALL} {filename} not found")
        return []
    return accounts

def countdown(seconds):
    """Display countdown timer"""
    while seconds:
        hours, remainder = divmod(seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        timer = f"{hours:02d}:{minutes:02d}:{secs:02d}"
        print(f"{Fore.YELLOW}Waiting for next cycle...{Style.RESET_ALL}")
        print(f"{Fore.BLUE}Next cycle in{Style.RESET_ALL}: {Fore.YELLOW}{timer}{Style.RESET_ALL}", end='\r')
        time.sleep(1)
        seconds -= 1
        # Clear the current line
        print(' ' * 50, end='\r')

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print(ASCII_ART)
    print(f"{Fore.CYAN}=================================================={Style.RESET_ALL}")
    print(f"{Fore.CYAN}Github : https://github.com/gieskuy5{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Telegram : https://t.me/giemdfk{Style.RESET_ALL}")
    print(f"{Fore.CYAN}=================================================={Style.RESET_ALL}\n")
    
    accounts = read_accounts('akun.txt')
    
    while True:
        try:
            for account in accounts:
                node = OpenLoopNode(account['email'], account['password'])
                if node.login():
                    initial_balance = node.get_point_balance()
                    node.checkin()
                    updated_balance = node.get_point_balance()
                    print(f"{Fore.BLUE}| INFO    |{Style.RESET_ALL} Updated balance: {updated_balance}")
                    print("")
            
            # 90-minute countdown (5400 seconds)
            countdown(5400)
            
            os.system('cls' if os.name == 'nt' else 'clear')
            print(ASCII_ART)
            print(f"{Fore.CYAN}=================================================={Style.RESET_ALL}")
            print(f"{Fore.CYAN}Github : https://github.com/gieskuy5{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Telegram : https://t.me/giemdfk{Style.RESET_ALL}")
            print(f"{Fore.CYAN}=================================================={Style.RESET_ALL}\n")
            
        except KeyboardInterrupt:
            print(f"\n{Fore.BLUE}| INFO    |{Style.RESET_ALL} Bot stopped by user")
            break
        except Exception as e:
            print(f"{Fore.RED}| ERROR   |{Style.RESET_ALL} Unexpected error: {str(e)}")
            time.sleep(30)

if __name__ == "__main__":
    main()
