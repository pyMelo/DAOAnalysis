import sys
from bs4 import BeautifulSoup
import csv
import os

def parse_html_file(file_path):
    """
    Parse contract metrics from an HTML file and save to CSV.
    Args:
        file_path (str): Path to the HTML file to process
    """
    try:
        # Read the HTML file
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
        
        # Extract data
        contracts_data = []
        
        # Find all relevant sections in the HTML
        # Note: You'll need to adjust these selectors based on your actual HTML structure
        for contract_section in soup.find_all('div', class_='contract'):
            contract_data = {
                'Contract Name': '',
                'Lines': 0,
                'nLines': 0,
                'SLOC': 0,
                'Comment Lines': 0,
                'Complexity Score': 0
            }
            
            # Extract metrics
            # Adjust these selectors based on your HTML structure
            metrics = contract_section.find_all('div', class_='metric')
            for metric in metrics:
                text = metric.get_text(strip=True)
                
                # Parse each metric based on the text content
                if 'Lines:' in text:
                    contract_data['Lines'] = int(text.split(':')[1])
                elif 'nLines:' in text:
                    contract_data['nLines'] = int(text.split(':')[1])
                elif 'SLOC:' in text:
                    contract_data['SLOC'] = int(text.split(':')[1])
                elif 'Comment Lines:' in text:
                    contract_data['Comment Lines'] = int(text.split(':')[1])
                elif 'Complexity Score:' in text:
                    contract_data['Complexity Score'] = float(text.split(':')[1])
            
            contracts_data.append(contract_data)
        
        # Generate output filename based on input filename
        base_name = os.path.splitext(file_path)[0]
        output_file = f"{base_name}_metrics.csv"
        
        # Write to CSV
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = ['Contract Name', 'Lines', 'nLines', 'SLOC', 
                         'Comment Lines', 'Complexity Score']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(contracts_data)
            
        print(f"Successfully processed {file_path}")
        print(f"Output saved to {output_file}")
        
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
    except Exception as e:
        print(f"Error processing file: {str(e)}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_html_file>")
        sys.exit(1)
    
    html_file_path = sys.argv[1]
    parse_html_file(html_file_path)

if __name__ == "__main__":
    main()