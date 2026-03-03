import time
import sys
import os
import re
import random
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILE_PATH = os.path.join(SCRIPT_DIR, "jumptask_main_profile") 

completed_task_fingerprints = [] 

def get_stable_driver():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled") 
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--mute-audio")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    options.add_argument("--restore-last-session") 
    
    if not os.path.exists(PROFILE_PATH): os.makedirs(PROFILE_PATH)
    options.add_argument(f"user-data-dir={PROFILE_PATH}")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def human_click_offset(driver, element, x, y):
    action = ActionChains(driver)
    action.move_to_element(element).move_by_offset(x, y)
    action.pause(random.uniform(0.3, 0.7)) 
    action.click_and_hold()
    action.pause(random.uniform(0.08, 0.15)) 
    action.release()
    action.perform()

def human_click_element(driver, element):
    action = ActionChains(driver)
    action.move_to_element(element)
    action.pause(random.uniform(0.3, 0.7))
    action.click_and_hold()
    action.pause(random.uniform(0.08, 0.15))
    action.release()
    action.perform()

def solve_checkbox_and_start(driver):
    print("[Bot] 🟢 Popup Detected! Waiting for text to render...")
    time.sleep(5.0) 
    
    search_query = None
    
    try:
        dialog = driver.find_element(By.CSS_SELECTOR, "div[role='dialog']")
        text = dialog.text
        match = re.search(r'(?:Search|Type in)\s*["“]([^"”\n]{3,60})["”]', text, re.IGNORECASE)
        if match:
            candidate = match.group(1)
            if " " in candidate and "Mui" not in candidate:
                search_query = candidate
    except: pass
    
    if not search_query:
        print("[Bot] ⚠️ Standard read failed. Scanning source code...")
        try:
            src = driver.page_source
            matches = re.findall(r'["“]([a-zA-Z0-9 ]{4,50})["”]', src)
            for m in matches:
                if "Mui" in m or "css" in m or "http" in m or "width" in m: continue
                if "money" in m or "earn" in m or "best" in m or "review" in m:
                    search_query = m
                    break
        except: pass

    if not search_query:
        print("[Bot] ❌ Could not decipher text. Defaulting to 'earn money online'...")
        search_query = "earn money online"
    else:
        print(f"[Bot] 🧠 LOCKED TARGET: '{search_query}'")

    try:
        start_btn = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, "//button[contains(., 'Start Task')]"))
        )
        
        print("[Bot] Clicking Checkbox...")
        human_click_offset(driver, start_btn, 0, -50)
        time.sleep(3.0) 
        
        print("[Bot] Clicking Start...")
        initial_tabs = len(driver.window_handles)
        human_click_element(driver, start_btn)
        time.sleep(5)
        
        if len(driver.window_handles) > initial_tabs:
            print("[Bot] 🚀 SUCCESS: Tab opened!")
            return True, search_query
            
        print("[Bot] Retrying Start Click...")
        human_click_element(driver, start_btn)
        time.sleep(5)

        if len(driver.window_handles) > initial_tabs:
            print("[Bot] 🚀 SUCCESS: Tab opened on retry!")
            return True, search_query

        return False, None

    except Exception as e:
        print(f"[Bot] Interaction Error: {e}")
        return False, None

def handle_youtube_tab(driver, main_window, search_query):
    try:
        new_tab = driver.window_handles[-1]
        if new_tab == main_window: return False 
        driver.switch_to.window(new_tab)
        
    
        print("[Bot] ⏳ Waiting for YouTube to load (Max 20s)...")
        valid_url = False
        for _ in range(20): 
            try:
                current = driver.current_url
                if "youtube.com" in current or "youtu.be" in current:
                    valid_url = True
                    break
            except: pass
            time.sleep(1)
            
        if not valid_url:
            print(f"[Bot] ⚠️ Timeout: URL never became YouTube. Current: {driver.current_url}")
            driver.close()
            driver.switch_to.window(main_window)
            return False

        print("[Bot] 📺 Switched to YouTube (Confirmed).")
        
        current_url = driver.current_url
        if "watch?v=" in current_url:
            print("[Bot] Direct link. Watching...")
        else:
            print(f"[Bot] 🚀 FORCE SEARCH: {search_query}")
            safe_query = search_query.replace(" ", "+")
            driver.get(f"https://www.youtube.com/results?search_query={safe_query}")
            time.sleep(5)
            
            print("[Bot] Clicking first video...")
            try: 
                video_title = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, "video-title"))
                )
                video_title.click()
            except: 
                 try: driver.find_element(By.TAG_NAME, "ytd-video-renderer").click()
                 except: pass
        
        time.sleep(5) 
        
        try:
            toggle = driver.find_element(By.CSS_SELECTOR, "button.ytp-autonav-toggle-button")
            if "true" in toggle.get_attribute("aria-checked"):
                driver.execute_script("arguments[0].click();", toggle)
                print("[Bot] Autoplay OFF")
        except: pass

        try:
            driver.execute_script("document.querySelector('video').loop = true;")
            print("[Bot] Video Loop ON")
        except: pass

        print("[Bot] Watching (130s)...")
        action = ActionChains(driver)
        for i in range(130, 0, -10):
            sys.stdout.write(f"\r[Bot] Time remaining: {i}s... ")
            sys.stdout.flush()
            try: action.move_by_offset(1, 1).perform()
            except: pass
            time.sleep(10)
        print("\n[Bot] Time up!")

        try:
            like_btn = driver.find_element(By.XPATH, '//button[contains(@aria-label,"like this video")]')
            driver.execute_script("arguments[0].click();", like_btn)
            print("[Bot] Liked video.")
        except: pass
        
        time.sleep(2)

        print("[Bot] 📜 Engaging Link Priority Scan...")
        try:
            try:
                driver.execute_script("document.querySelectorAll('#expand, #description-inline-expander').forEach(b => b.click())")
                time.sleep(2)
            except: pass

            try:
                desc_container = driver.find_element(By.ID, "description-inner")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", desc_container)
                time.sleep(2)
            except:
                desc_container = driver.find_element(By.ID, "columns")

            all_links = desc_container.find_elements(By.TAG_NAME, "a")
            
            tier_1_jumptask = []
            tier_2_honeygain = []
            tier_3_generic = []
            
            blacklist = ["facebook", "instagram", "tiktok", "twitter", "youtubekids", "accounts.google", "support.google", "youtube.com/channel", "youtube.com/hashtag"]

            for link in all_links:
                raw_href = str(link.get_attribute("href"))
                decoded_href = urllib.parse.unquote(raw_href).lower()
                
                if any(b in decoded_href for b in blacklist): continue
                if "http" not in decoded_href: continue
                if "youtube.com/watch" in decoded_href: continue

                if "jmpt.network" in decoded_href or "jumptask.io" in decoded_href:
                    tier_1_jumptask.append(link)
                elif "honeygain" in decoded_href or "vpnpro" in decoded_href:
                    tier_2_honeygain.append(link)
                else:
                    tier_3_generic.append(link)

            target_link = None
            if tier_1_jumptask:
                target_link = tier_1_jumptask[0]
                print(f"[Bot] 🥇 TIER 1 MATCH: JumpTask/JMPT Link found!")
            elif tier_2_honeygain:
                target_link = tier_2_honeygain[0]
                print(f"[Bot] 🥈 TIER 2 MATCH: Honeygain Link found.")
            elif tier_3_generic:
                target_link = tier_3_generic[0]
                print(f"[Bot] 🥉 TIER 3 MATCH: Generic external link found.")

            if target_link:
                driver.execute_script("arguments[0].style.border='5px solid #00FF00';", target_link)
                print(f"[Bot] 🖱️ Clicking: {target_link.get_attribute('href')}")
                time.sleep(1)
                driver.execute_script("arguments[0].click();", target_link)
                print("[Bot] ⏳ Waiting on sponsor site (15s)...")
                time.sleep(15)
            else:
                print("[Bot] ❌ No valid money links found.")

        except Exception as e:
            print(f"[Bot] Link error: {e}")

        print("[Bot] Closing YouTube...")
        driver.close()
        driver.switch_to.window(main_window)
        return True
        
    except Exception as e:
        print(f"[Bot] YouTube Error: {e}")
        if len(driver.window_handles) > 1:
            driver.switch_to.window(main_window)
        return False

def navigate_to_youtube_section(driver):
    print("[Nav] Locating YouTube Category...")
    try:
        tiles = driver.find_elements(By.XPATH, "//*[contains(text(), 'YouTube')]")
        for tile in tiles:
            if tile.is_displayed():
                print("[Nav] Found YouTube Tile! Clicking...")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tile)
                time.sleep(1)
                try: tile.find_element(By.XPATH, "./..").click()
                except: tile.click()
                time.sleep(5)
                return True
    except: pass
    return False

def find_and_click_task(driver):
    print(f"[Bot] Scanning for FRESH tasks... (Ignored: {len(completed_task_fingerprints)})")
    
    for scroll_attempt in range(5):
        try:
            cards = driver.find_elements(By.XPATH, "//*[contains(text(), 'YouTube') or contains(text(), 'Video')]")
            
            for card in cards:
                try:
                    if not card.is_displayed() or card.location['x'] < 250: continue
                    
                    text = card.text.strip()
                    if not text: text = card.find_element(By.XPATH, "./..").text.strip()
                    
                    try:
                        href = card.find_element(By.XPATH, "./..").get_attribute("href")
                    except: href = "no_link"
                    
                    fingerprint = f"{text[:40]}_{href}"
                    
                    if fingerprint in completed_task_fingerprints:
                        driver.execute_script("arguments[0].style.border='3px solid red';", card)
                        continue

                    print(f"[Picker] ✅ Found NEW Task: '{text[:30]}...'")
                    driver.execute_script("arguments[0].style.border='3px solid #00FF00';", card)
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
                    time.sleep(1)
                    
                    try: card.find_element(By.XPATH, "./..").click()
                    except: card.click()
                    
                    print("[Picker] Waiting for popup...")
                    try:
                        WebDriverWait(driver, 5).until(
                            EC.visibility_of_element_located((By.XPATH, "//button[contains(., 'Start Task')]"))
                        )
                        print(f"[Picker] ✅ Popup confirmed!")
                        completed_task_fingerprints.append(fingerprint)
                        return True
                    except:
                        print(f"[Picker] ❌ Click failed. Trying next.")
                        continue
                        
                except Exception as e:
                    continue

            print(f"[Picker] Scrolling down ({scroll_attempt+1}/5)...")
            driver.execute_script("window.scrollBy(0, 600);")
            time.sleep(2)
            
        except: pass
        
    print("[Picker] ⚠️ No reachable tasks found.")
    return False

def main_loop():
    print("=======================================")
    print("   JUMPTASK ULTIMATE BOT v83.0         ")
    print("   (PATIENCE & MEMORY EDITION)         ")
    print("=======================================")
    
    try:
        driver = get_stable_driver()
    except Exception as e:
        print(f"CRASH: {e}")
        return

    print("[Setup] Opening JumpTask Earn Dashboard...")
    driver.get("https://app.jumptask.io/earn") 
    main_window = driver.current_window_handle
    
    print("\n-------------------------------------------------")
    print("🛑 ONE-TIME SETUP")
    print("1. Log in (if needed).")
    print("2. Bot will auto-run.")
    input(">>> PRESS ENTER TO START <<<") 
    print("-------------------------------------------------")
    
    navigate_to_youtube_section(driver)
    
    while True:
        try:
            start_btn_visible = False
            try:
                btn = driver.find_element(By.XPATH, "//button[contains(., 'Start Task')]")
                if btn.is_displayed(): start_btn_visible = True
            except: pass

            if start_btn_visible:
                success, search_query = solve_checkbox_and_start(driver)
                if success:
                    handle_youtube_tab(driver, main_window, search_query)
                    print("[Bot] Task Done. Refreshing & Returning to List...")
                    driver.get("https://app.jumptask.io/earn")
                    time.sleep(5)
                    navigate_to_youtube_section(driver)
                else:
                    print("[Bot] Start failed. Reloading...")
                    driver.refresh()
                    time.sleep(5)
            else:
                if not find_and_click_task(driver):
                    print("[Bot] No new tasks. Waiting 15s...")
                    time.sleep(15)
                    driver.refresh()
                    time.sleep(5)
                    navigate_to_youtube_section(driver)

        except Exception as e:
            print(f"[Error] {e}")
            time.sleep(5)

if __name__ == "__main__":

    main_loop()
