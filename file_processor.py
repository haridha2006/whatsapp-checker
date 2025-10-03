import pandas as pd
import csv
import io

def process_uploaded_file(uploaded_file):
    """Process uploaded file and extract phone numbers"""
    numbers = []
    
    try:
        file_name = uploaded_file.name.lower()
        
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
                    
        elif file_name.endswith(('.xlsx', '.xls')):
            # Process Excel file
            try:
                df = pd.read_excel(uploaded_file)
                first_col = df.iloc[:, 0]
                numbers = [str(val).strip() for val in first_col if pd.notna(val)]
            except ImportError:
                return [], 'Excel support requires: pip install pandas openpyxl'
                
        else:
            return [], 'Unsupported file format. Use .txt, .csv, or .xlsx'
            
        # Clean numbers
        clean_numbers = []
        for num in numbers:
            clean_num = str(num).strip()
            if clean_num and len(clean_num) >= 10:
                clean_numbers.append(clean_num)
                
        return clean_numbers, None
        
    except Exception as e:
        return [], f'Error processing file: {str(e)}'
