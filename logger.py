import logging
import os
from datetime import datetime

def setup_logger():
    
    base_path = os.path.dirname(__file__)


    # Create output directory in parent folder
    output_dir = os.path.join(base_path, 'logs')
    os.makedirs(output_dir, exist_ok=True)

    # Log filename in dd-mm-yyyy format
    date_str = datetime.now().strftime("%d-%m-%Y")
    log_file = os.path.join(output_dir, f"rpa_log_{date_str}.log")

    

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, mode='a', encoding='utf-8'),
            # logging.StreamHandler(sys.stdout)
        ]

    )
