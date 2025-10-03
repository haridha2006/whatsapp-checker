def check_whatsapp_registration_fast(number):
    """
    FAST WhatsApp registration checker - optimized for speed
    Uses persistent browser session and minimal waits
    """
    print(f' Fast checking: {number}')
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException
        import re
        import time
        
        # Clean and format the number
        clean_number = re.sub(r'[^\d+]', '', number)
        if clean_number.startswith('+'):
            clean_number = clean_number[1:]
        
        # Use global persistent browser if available
        if not hasattr(check_whatsapp_registration_fast, 'driver') or check_whatsapp_registration_fast.driver is None:
            print(' Starting persistent browser...')
            
            chrome_options = Options()
            chrome_options.add_argument(f'--user-data-dir=C:\\num\\chrome_profile')
            chrome_options.add_argument('--profile-directory=Default')
            chrome_options.add_argument('--disable-notifications')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-images')
            
            check_whatsapp_registration_fast.driver = webdriver.Chrome(options=chrome_options)
            check_whatsapp_registration_fast.driver.get('https://web.whatsapp.com')
            time.sleep(3)
        
        driver = check_whatsapp_registration_fast.driver
        
        # Fast navigation
        compose_url = f'https://web.whatsapp.com/send?phone={clean_number}'
        driver.get(compose_url)
        
        # Quick detection with short timeout
        wait = WebDriverWait(driver, 3)
        
        try:
            # Quick error check
            error_element = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'invalid')]")))
            print(' FAST: NOT registered')
            return False
        except TimeoutException:
            pass
        
        try:
            # Quick chat check
            chat_element = driver.find_element(By.CSS_SELECTOR, 'div[contenteditable="true"]')
            if chat_element.is_displayed():
                print(' FAST: REGISTERED')
                return True
        except:
            pass
        
        # URL check as fallback
        if 'send?phone=' in driver.current_url:
            print(' FAST: REGISTERED (URL)')
            return True
        
        print(' FAST: Assuming NOT registered')
        return False
        
    except Exception as e:
        print(f' FAST error: {str(e)}')
        return False

# Initialize driver
check_whatsapp_registration_fast.driver = None
