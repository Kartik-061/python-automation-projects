import time
import sys
import os
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILE_PATH = os.path.join(SCRIPT_DIR, "jumptask_main_profile") 
 
REAL_QUERIES = [
    "weather in Mumbai", "Virat Kohli stats", "how to make tea", 
    "latest bollywood news", "gold price today", "train pnr status",
    "IPL 2026 schedule", "best phones under 20000", "meaning of love",
    "top 10 tourist places in India", "stock market live", "news headlines",
    "Google translate", "YouTube", "Facebook login", "Amazon India sale",
    "Flipkart offers", "how to learn coding", "history of India",
    "best movies on Netflix", "cricket score", "currency converter",
    "temperature in Delhi", "Bangalore traffic news", "jobs in IT sector"
]

def get_stable_driver():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled") 
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--start-maximized")
    
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0")
    
    if not os.path.exists(PROFILE_PATH): os.makedirs(PROFILE_PATH)
    options.add_argument(f"user-data-dir={PROFILE_PATH}")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def human_type(element, text):
    """Types text one character at a time with random delays"""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.2))

def main_loop():
    print("=======================================")
    print("   MICROSOFT REWARDS v3.1 (MANUAL)     ")
    print("=======================================")
    
    try:
        driver = get_stable_driver()
    except Exception as e:
        print(f"CRASH: {e}")
        return

    print("[Setup] Opening Bing...")
    driver.get("https://www.bing.com")
    
    print("\n-------------------------------------------------")
    print("🛑 PAUSED FOR MANUAL CHECK")
    print("1. Look at the browser window.")
    print("2. If you see a CAPTCHA or Login screen, SOLVE IT NOW.")
    print("3. Wait until you see the normal Bing search bar.")
    print("-------------------------------------------------")
    input(">>> PRESS ENTER HERE WHEN YOU ARE READY <<<") 
    print("-------------------------------------------------")
    
    daily_searches = random.sample(REAL_QUERIES, k=5) 
    
    for i, query in enumerate(daily_searches):
        print(f"\n[Bot] ⌨️ ({i+1}/5) Typing: '{query}'")
        
        try:
        
            try:
                search_box = driver.find_element(By.NAME, "q")
            except:
                try: search_box = driver.find_element(By.ID, "sb_form_q")
                except: search_box = driver.find_element(By.CSS_SELECTOR, "textarea[type='search']")
            
           
            search_box.clear()
            time.sleep(1)
            human_type(search_box, query) 
            time.sleep(1)
            
            
            search_box.send_keys(Keys.RETURN)
            
            
            wait_time = random.uniform(15.0, 20.0)
            sys.stdout.write(f"       ⏳ 'Reading' results ({int(wait_time)}s)... ")
            sys.stdout.flush()
            
            time.sleep(3)
            driver.execute_script("window.scrollBy(0, 300);")
            
            time.sleep(wait_time)
            print("Done.")
            
        except Exception as e:
            print(f"[Error] Search failed: {e}")
            driver.get("https://www.bing.com") 
            time.sleep(5)

    print("\n[Bot] ✅ Daily limit reached (15 pts). Closing...")
    print("⚠️ DO NOT RUN AGAIN UNTIL TOMORROW.")
    time.sleep(5)
    driver.quit()

if __name__ == "__main__":

    main_loop()
