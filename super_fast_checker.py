from concurrent.futures import ThreadPoolExecutor
import asyncio

def check_whatsapp_super_fast(number):
    """SUPER FAST checker with minimal waits"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.common.exceptions import TimeoutException, NoSuchElementException
        import re
        import time
        
        print(f' Super fast checking: {number}')
        
        # Clean number
        clean_number = re.sub(r'[^\d+]', '', number)
        if clean_number.startswith('+'):
            clean_number = clean_number[1:]
        
        # Lightning-fast Chrome options
        chrome_options = Options()
        chrome_options.add_argument(f'--user-data-dir=C:\\num\\chrome_profile')
        chrome_options.add_argument('--profile-directory=Default')
        chrome_options.add_argument('--headless')  # No GUI for speed
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-images')
        chrome_options.add_argument('--disable-javascript')
        chrome_options.add_argument('--disable-css')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            # Ultra-fast navigation
            compose_url = f'https://web.whatsapp.com/send?phone={clean_number}'
            driver.get(compose_url)
            
            # Minimal wait - just 2 seconds max
            time.sleep(2)
            
            # Quick DOM check
            page_source = driver.page_source.lower()
            
            # Fast text-based detection
            if any(error_text in page_source for error_text in 
                   ['invalid', 'not on whatsapp', 'phone number shared via url is invalid']):
                print(f' {number}: NOT registered')
                return False
            
            # Check for chat indicators
            if any(success_text in page_source for success_text in 
                   ['type a message', 'contenteditable', 'data-testid="compose"']):
                print(f' {number}: REGISTERED')  
                return True
            
            # URL-based check
            current_url = driver.current_url
            if 'send?phone=' in current_url and clean_number in current_url:
                print(f' {number}: REGISTERED (URL)')
                return True
            
            print(f' {number}: Unclear - assuming NOT registered')
            return False
            
        finally:
            driver.quit()
            
    except Exception as e:
        print(f' {number}: Error - {str(e)}')
        return False

def batch_check_parallel(numbers, max_workers=3):
    """Check multiple numbers in parallel"""
    print(f' Starting parallel checking of {len(numbers)} numbers with {max_workers} workers')
    
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_number = {executor.submit(check_whatsapp_super_fast, number.strip()): number.strip() 
                          for number in numbers}
        
        # Collect results as they complete
        for future in future_to_number:
            number = future_to_number[future]
            try:
                result = future.result()
                results.append({
                    'number': number,
                    'registered': result,
                    'message': 'REGISTERED' if result else 'NOT REGISTERED'
                })
                print(f' Completed: {number} -> {result}')
            except Exception as e:
                results.append({
                    'number': number,
                    'registered': False,
                    'error': str(e)
                })
                print(f' Failed: {number} -> {str(e)}')
    
    return results
