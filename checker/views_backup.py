from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import threading
import time
from datetime import datetime
import csv
import io

# Global variables for batch processing
checking_status = {
    'running': False,
    'progress': 0,
    'total': 0,
    'results': []
}

def check_whatsapp_registration_compose_url(number):
    '''
    Check if a phone number is registered on WhatsApp using compose URL method
    This method works for ANY number, not just non-contacts
    '''
    print(f' Checking WhatsApp registration for: {number}')
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        import re
        import os
        
        # Clean and format the number
        clean_number = re.sub(r'[^\d+]', '', number)
        if clean_number.startswith('+'):
            clean_number = clean_number[1:]  # Remove + for URL
        
        print(f' Cleaned number: {clean_number}')
        
        # Chrome profile path
        profile_path = r'C:\num\chrome_profile'
        
        # Chrome options
        chrome_options = Options()
        chrome_options.add_argument(f'--user-data-dir={profile_path}')
        chrome_options.add_argument('--profile-directory=Default')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--no-first-run')
        chrome_options.add_argument('--no-default-browser-check')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-images')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-extensions')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()
        
        # Go to WhatsApp Web compose URL
        compose_url = f'https://web.whatsapp.com/send?phone={clean_number}'
        print(f' Opening compose URL: {compose_url}')
        
        driver.get(compose_url)
        time.sleep(1)
        
        # Wait for page to load completely
        wait = WebDriverWait(driver, 5)
        
        print(' Waiting for WhatsApp Web to load...')
        
        # Check for various indicators
        try:
            # Method 1: Look for error message about number not on WhatsApp
            error_selectors = [
                '[data-testid=\"alert-phone-number-not-on-whatsapp\"]',
                '[data-testid=\"invalid-phone-number\"]',
                'div[data-animate-alert-toast=\"true\"]',
                'div[role=\"alert\"]'
            ]
            
            for selector in error_selectors:
                try:
                    error_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    error_text = error_element.text.lower()
                    print(f' Error found: {error_text}')
                    
                    if any(phrase in error_text for phrase in ['not on whatsapp', 'invalid', 'not found']):
                        print(' Number NOT registered on WhatsApp')
                        return False
                        
                except Exception:
                    continue
            
            # Method 2: Check if we reach the chat interface
            chat_selectors = [
                '[data-testid=\"conversation-compose-box-input\"]',
                'div[contenteditable=\"true\"][data-tab=\"10\"]',
                '[data-testid=\"msg-container\"]',
                'footer[data-testid=\"compose\"]'
            ]
            
            for selector in chat_selectors:
                try:
                    chat_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    print(f' Chat interface found: {selector}')
                    print(' Number IS registered on WhatsApp')
                    return True
                except Exception:
                    continue
            
            # Method 3: Check URL for success/failure patterns
            time.sleep(3)
            current_url = driver.current_url
            print(f' Current URL: {current_url}')
            
            if 'send?phone=' in current_url and clean_number in current_url:
                # Still on compose URL might mean success
                print(' Still on compose URL - likely registered')
                return True
            
            print(' Unable to determine registration status clearly')
            return False
            
        except Exception as e:
            print(f' Error during checking: {str(e)}')
            return False
            
    except Exception as e:
        print(f' WebDriver error: {str(e)}')
        return False
        
    finally:
        try:
            driver.quit()
            print(' Browser closed')
        except:
            pass

def home(request):
    return render(request, 'index.html')

@csrf_exempt
@require_http_methods(['POST'])
def initialize_session(request):
    return JsonResponse({'success': True, 'message': 'Django session ready'})

@csrf_exempt
@require_http_methods(['POST'])
def check_single(request):
    try:
        data = json.loads(request.body)
        number = data.get('number', '').strip()
        
        if not number:
            return JsonResponse({'error': 'No number provided'}, status=400)
        
        print(f'[DJANGO DEBUG] Checking {number}...')
        result = check_whatsapp_registration_compose_url(number)
        
        return JsonResponse({
            'number': number,
            'registered': result,
            'message': 'REGISTERED on WhatsApp' if result else 'NOT REGISTERED on WhatsApp',
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(['POST'])
def check_batch(request):
    global checking_status
    
    try:
        data = json.loads(request.body)
        numbers = data.get('numbers', [])
        
        if not numbers:
            return JsonResponse({'error': 'No numbers provided'}, status=400)
        
        checking_status = {'running': True, 'progress': 0, 'total': len(numbers), 'results': []}
        
        def batch_process():
            global checking_status
            print(f'[BATCH] Starting batch of {len(numbers)} numbers')
            for i, number in enumerate(numbers):
                try:
                    result = check_whatsapp_registration_compose_url(number.strip())
                    checking_status['results'].append({
                        'number': number,
                        'registered': result,
                        'message': 'REGISTERED on WhatsApp' if result else 'NOT REGISTERED on WhatsApp'
                    })
                    checking_status['progress'] = i + 1
                    time.sleep(3)
                except Exception as e:
                    checking_status['results'].append({
                        'number': number,
                        'error': str(e)
                    })
            checking_status['running'] = False
        
        thread = threading.Thread(target=batch_process)
        thread.daemon = True
        thread.start()
        
        return JsonResponse({'message': 'Batch checking started', 'total': len(numbers)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_status(request):
    return JsonResponse(checking_status)

def session_status(request):
    return JsonResponse({
        'initialized': True,
        'driver_active': True
    })


@csrf_exempt
@require_http_methods(['POST'])
def upload_file(request):
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
        
        uploaded_file = request.FILES['file']
        
        if uploaded_file.size > 5 * 1024 * 1024:  # 5MB limit
            return JsonResponse({'error': 'File too large (max 5MB)'}, status=400)
        
        numbers = []
        file_name = uploaded_file.name.lower()
        
        try:
            if file_name.endswith('.txt'):
                # Process text file
                content = uploaded_file.read().decode('utf-8')
                numbers = [line.strip() for line in content.split('\n') if line.strip()]
                
            elif file_name.endswith('.csv'):
                # Process CSV file
                content = uploaded_file.read().decode('utf-8')
                csv_reader = csv.reader(io.StringIO(content))
                
                for row in csv_reader:
                    if row and row[0].strip():
                        numbers.append(row[0].strip())
                        
            else:
                return JsonResponse({'error': 'Unsupported file format. Use .txt or .csv'}, status=400)
            
            # Clean and validate numbers
            clean_numbers = []
            for num in numbers:
                clean_num = str(num).strip()
                if clean_num and len(clean_num) >= 10:
                    clean_numbers.append(clean_num)
            
            if not clean_numbers:
                return JsonResponse({'error': 'No valid phone numbers found in file'}, status=400)
            
            return JsonResponse({
                'success': True,
                'numbers': clean_numbers,
                'count': len(clean_numbers),
                'message': f'Successfully loaded {len(clean_numbers)} phone numbers'
            })
            
        except Exception as e:
            return JsonResponse({'error': f'Error processing file: {str(e)}'}, status=500)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



def test_page(request):
    return render(request, 'test.html')

def test_api(request):
    return JsonResponse({
        'status': 'Django API is working!',
        'method': request.method,
        'timestamp': datetime.now().strftime('%H:%M:%S')
    })
