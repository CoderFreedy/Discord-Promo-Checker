import requests
import re
import os
import time
import threading
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore, Style, init


init(autoreset=True)

class DiscordPromoChecker:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.input_dir = os.path.join(self.base_dir, 'Input')
        self.output_dir = os.path.join(self.base_dir, 'Output')
        self.proxy_file = os.path.join(self.input_dir, 'proxies.txt')
        self.promo_file = os.path.join(self.input_dir, 'promotion_links.txt')
        
        self.setup_directories()
        
        # Load proxy from file
        self.proxy_url = self.load_proxy()
        self.proxy = {
            'http': f'http://{self.proxy_url}',
            'https': f'http://{self.proxy_url}'
        } if self.proxy_url else {}
        
        self.headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.9,ar;q=0.8,en-GB;q=0.7,it;q=0.6',
            'content-type': 'application/json',
            'referer': 'https://discord.com/billing/promotions/',
            'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'x-debug-options': 'bugReporterEnabled',
            'x-discord-locale': 'en-US',
            'x-discord-timezone': 'Africa/Cairo',
            'x-super-properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiaGFzX2NsaWVudF9tb2RzIjpmYWxzZSwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzE0MC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTQwLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiJodHRwczovL2Rpc2NvcmQuY29tL2Rpc2NvdmVyeS9xdWVzdHMiLCJyZWZlcnJpbmdfZG9tYWluIjoiZGlzY29yZC5jb20iLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6NDUwNjkyLCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsLCJjbGllbnRfbGF1bmNoX2lkIjoiYzM2MjBmMjgtNjJjNS00NGFjLTk3YWUtOWZkOThjZGExYjc5IiwibGF1bmNoX3NpZ25hdHVyZSI6bnVsbCwiY2xpZW50X2hlYXJ0YmVhdF9zZXNzaW9uX2lkIjoiMDA1ZjllYTAtZTkyMC00ODZlLWE2MjAtNGIxMWRhYTgwNDI0IiwiY2xpZW50X2FwcF9zdGF0ZSI6InVuZm9jdXNlZCJ9'
        }
        
        self.output_file = os.path.join(self.output_dir, 'valid_promotions.txt')
        self.lock = threading.Lock()
        self.processed_count = 0
        self.valid_count = 0
    
    def setup_directories(self):
        """Create input and output directories if they don't exist"""
        os.makedirs(self.input_dir, exist_ok=True)
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        if not os.path.exists(self.proxy_file):
            with open(self.proxy_file, 'w', encoding='utf-8') as f:
                f.write('# Add your proxy here in format: username:password@host:port\n')
            print(f"{Style.BRIGHT}{Fore.YELLOW}Created proxy file: {self.proxy_file}{Style.RESET_ALL}")
            print(f"{Style.BRIGHT}{Fore.YELLOW}Please configure your proxy in this file.{Style.RESET_ALL}\n")
        
        if not os.path.exists(self.promo_file):
            with open(self.promo_file, 'w', encoding='utf-8') as f:
                pass
            print(f"{Style.BRIGHT}{Fore.YELLOW}Created promotion links file: {self.promo_file}{Style.RESET_ALL}")
            print(f"{Style.BRIGHT}{Fore.YELLOW}Please add promotion links to this file.{Style.RESET_ALL}\n")
    
    def load_proxy(self):
        """Load proxy from proxy file"""
        if not os.path.exists(self.proxy_file):
            print(f"{Fore.RED}Proxy file not found: {self.proxy_file}{Style.RESET_ALL}")
            return None
        
        try:
            with open(self.proxy_file, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]
            
            if lines:
                proxy_url = lines[0]
                print(f"{Style.BRIGHT}{Fore.GREEN}Loaded proxy: {proxy_url[:50]}...{Style.RESET_ALL}")
                return proxy_url
            else:
                print(f"{Fore.YELLOW}No proxy found in file. Add a proxy to: {self.proxy_file}{Style.RESET_ALL}")
                return None
        except Exception as e:
            print(f"{Fore.RED}Error loading proxy: {e}{Style.RESET_ALL}")
            return None
        
    def extract_promo_code(self, url):
        """Extract promo code from Discord URLs"""
        
        pattern1 = r'discord\.com/billing/promotions/([A-Za-z0-9]+)'
         
        pattern2 = r'promos\.discord\.gg/([A-Za-z0-9]+)'
        
        match = re.search(pattern1, url) or re.search(pattern2, url)
        return match.group(1) if match else None
    
    def check_promo(self, promo_code, max_retries=3):
        """Check if promo code is valid and working with retry mechanism"""
        url = f"https://discord.com/api/v9/entitlements/gift-codes/{promo_code}"
        params = {
            'country_code': 'EE',
            'payment_source_id': '1412547701505261578',
            'with_application': 'false',
            'with_subscription_plan': 'true'
        }
        
        for attempt in range(max_retries):
            try:

                if attempt > 0:
                    delay = (2 ** attempt) + random.uniform(0, 1)  
                    time.sleep(delay)
                
                response = requests.get(
                    url, 
                    headers=self.headers, 
                    params=params, 
                    proxies=self.proxy, 
                    timeout=15  
                )
                
                if response.status_code == 200:
                    data = response.json()
                    

                    subscription_trial = data.get('subscription_trial', {})
                    trial_interval_count = subscription_trial.get('interval_count', 0)
                    
                    
                    uses = data.get('uses', 0)  
                    redeemed = data.get('redeemed', False)  
                    
                    is_3_month = trial_interval_count == 3
                    is_unused = uses == 0 and not redeemed
                    

                    is_working = is_unused
                    
                    return {
                        'valid': True,
                        'working': is_working,
                        'unused': is_unused,
                        'is_3_month': is_3_month,
                        'uses': uses,
                        'redeemed': redeemed,
                        'data': data
                    }
                elif response.status_code == 404:
                    return {'valid': False, 'working': False, 'error': 'Promo code not found'}
                elif response.status_code == 400:
                    return {'valid': False, 'working': False, 'error': 'Invalid promo code'}
                elif response.status_code == 429:

                    if attempt < max_retries - 1:
                        delay = 5 + (2 ** attempt) + random.uniform(0, 2)
                        time.sleep(delay)
                        continue
                    return {'valid': False, 'working': False, 'error': 'Rate limited after retries'}
                else:
                    return {'valid': False, 'working': False, 'error': f'HTTP {response.status_code}'}
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    continue  
                return {'valid': False, 'working': False, 'error': 'Connection timeout after retries'}
            except requests.exceptions.ConnectionError:
                if attempt < max_retries - 1:
                    continue  
                return {'valid': False, 'working': False, 'error': 'Connection error after retries'}
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    continue  
                return {'valid': False, 'working': False, 'error': f'Request failed after retries: {str(e)}'}
        
        return {'valid': False, 'working': False, 'error': 'Max retries exceeded'}
    
    def print_success(self, index, total, promo_link, status_info=""):
        """Print success message in bold pink and white"""
        status = f" ({status_info})" if status_info else ""
        print(f"[{index}/{total}] {Style.BRIGHT}{Fore.MAGENTA}(working){Style.RESET_ALL} {Style.BRIGHT}{Fore.WHITE}valid promo{Style.RESET_ALL} {Style.BRIGHT}{Fore.MAGENTA}{promo_link}{Style.RESET_ALL}{status}")
    
    def print_failure(self, index, total, promo_link, reason="used/invalid"):
        """Print failure message in bold red"""
        print(f"[{index}/{total}] {Style.BRIGHT}{Fore.RED}({reason}){Style.RESET_ALL} {Style.BRIGHT}{Fore.RED}{promo_link}{Style.RESET_ALL}")
    
    def process_promo(self, link_data, total_count):
        """Process a single promo link"""
        index, link = link_data
        promo_code = self.extract_promo_code(link)
        
        if not promo_code:
            with self.lock:
                print(f"[{index}/{total_count}] {Fore.YELLOW}Invalid URL format: {link}{Style.RESET_ALL}")
            return None

        time.sleep(random.uniform(0.1, 0.5))
        
        result = self.check_promo(promo_code)
        
        with self.lock:
            if result.get('valid', False) and result.get('working', False):

                status_parts = []
                if result.get('is_3_month', False):
                    status_parts.append("3-month")
                if result.get('unused', False):
                    status_parts.append("unused")
                elif result.get('uses', 0) > 0:
                    status_parts.append(f"used {result['uses']} times")
                
                status_info = ", ".join(status_parts) if status_parts else "working"
                
                self.print_success(index, total_count, link, status_info)
                self.save_valid_promotion(link, status_info)
                self.valid_count += 1
                return link
            else:
                error_msg = result.get('error', 'invalid/expired')
                self.print_failure(index, total_count, link, error_msg)
                return None
    
    def read_promotion_links(self):
        """Read promotion links from input file"""
        if not os.path.exists(self.promo_file):
            print(f"{Fore.RED}Input file not found: {self.promo_file}{Style.RESET_ALL}")
            return []
        
        with open(self.promo_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]
        
        return lines
    
    def save_valid_promotion(self, promo_link, status_info=""):
        """Save valid working promotion to output file (thread-safe)"""
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        
        with open(self.output_file, 'a', encoding='utf-8') as f:
            f.write(f"{promo_link}\n")
    
    def run(self):
        """Main function to check all promotion links using multithreading"""
        print(f"{Style.BRIGHT}{Fore.CYAN}Discord Promo Checker Started{Style.RESET_ALL}")
        
        if not self.proxy_url:
            print(f"{Fore.RED}Error: No proxy configured. Please add a proxy to: {self.proxy_file}{Style.RESET_ALL}")
            return
        
        print(f"{Style.BRIGHT}{Fore.CYAN}Using proxy: {self.proxy_url[:50]}...{Style.RESET_ALL}")
        print(f"{Style.BRIGHT}{Fore.CYAN}Using 50 threads with retry mechanism for reliability{Style.RESET_ALL}")
        print(f"{Style.BRIGHT}{Fore.CYAN}Checking for working promos (will show all valid ones)...{Style.RESET_ALL}\n")
        

        if os.path.exists(self.output_file):
            open(self.output_file, 'w').close()
        
        promotion_links = self.read_promotion_links()
        
        if not promotion_links:
            print(f"{Fore.YELLOW}No promotion links found in input file.{Style.RESET_ALL}")
            return
        
        total_count = len(promotion_links)
        self.valid_count = 0
        

        enumerated_links = [(i + 1, link) for i, link in enumerate(promotion_links)]
        

        with ThreadPoolExecutor(max_workers=50) as executor:

            futures = {executor.submit(self.process_promo, link_data, total_count): link_data for link_data in enumerated_links}

            for future in as_completed(futures):
                try:
                    result = future.result()
                except Exception as e:
                    print(f"{Fore.RED}Error processing promo: {e}{Style.RESET_ALL}")
        
        print(f"\n{Style.BRIGHT}{Fore.CYAN}Checking complete!{Style.RESET_ALL}")
        print(f"{Style.BRIGHT}{Fore.GREEN}Working promos found: {self.valid_count}/{total_count}{Style.RESET_ALL}")
        
        if self.valid_count > 0:
            print(f"{Style.BRIGHT}{Fore.GREEN}Valid promotions saved to: {self.output_file}{Style.RESET_ALL}")

if __name__ == "__main__":
    checker = DiscordPromoChecker()
    checker.run()