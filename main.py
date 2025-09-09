import time
import json
import pandas as pd
from decouple import config
import tax_return
from logger import setup_logger
import logging
from utils import get_file_path, update_file_status

def verify_tax_return_using_api(file_path):
    
    # Load the Excel file
    df = pd.read_excel(file_path)
    
    # Ensure that the relevant columns are of type object (string)
    assessment_years = json.loads(config("assessment_years")) # change based on assessment year 
    for assessment_year in assessment_years:
        # Columns to ensure exist and are of type object
        columns_to_process = [f'PSR For {year}' for year in assessment_years] + ['Name from PSR','Is TIN Verified']

        for col in columns_to_process:
            if col not in df.columns:
                df[col] = pd.Series(dtype='object')
            else:
                df[col] = df[col].astype(object)


    # Counter for filled responses
    filled_count = 0

    for index, row in df.iterrows():
        if row.isna().all():
            break
        tin_no = row['TIN No.']
        name_from_psr_found = False
        is_tin_verified = False
        for assessment_year in assessment_years:
            if pd.isna(row[f'PSR For {assessment_year}']):
                print(f"INDEX: {index} --- TIN: {tin_no} --- Assessment Year: {assessment_year}")
                logging.info(f"INDEX: {index} --- TIN: {tin_no} --- Assessment Year: {assessment_year}")
                response , status_code = tax_return.verify_tax_using_post_request(tin_no=tin_no, assessment_year=assessment_year)
                print("response---", response, "status_code--------", status_code)
                logging.info(f"{response=},{status_code=}")
                if status_code == 200:
                    if response['success'] is False:
                        df.at[index, f'PSR For {assessment_year}'] = 'No'
                    else:
                        df.at[index, f'PSR For {assessment_year}'] = 'YES'

                        if name_from_psr_found is False:
                            df.at[index, 'Name from PSR'] = response['replyMessage']['assesName']
                            name_from_psr_found = True
                        if is_tin_verified is False:
                            df.at[index, 'Is TIN Verified'] = 'YES'
                            is_tin_verified = True

                else:
                    df.at[index, f'PSR For {assessment_year}'] = 'NO'

                # Increment the filled count
                filled_count += 1

                # Check if we have filled 10 responses
                if filled_count >= 10:
                    # Write back to the existing Excel file after reaching the count
                    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                        df.to_excel(writer, index=False, sheet_name='For PSR Checking-With TIN No.')
                    print("Data has been written to Excel after filling 10 responses.")
                    # Reset the filled count
                    logging.info("Data has been written to Excel after filling 10 responses.")
                    filled_count = 0

                print(f"Data for TIN: {tin_no} and Assessment Year: {assessment_year} has been updated successfully.")
                logging.info(f"Data for TIN: {tin_no} and Assessment Year: {assessment_year} has been updated successfully.")
            else:
                print(f"Skipping TIN: {tin_no} for Assessment Year: {assessment_year} as PSR is already filled.")
                logging.info(f"Skipping TIN: {tin_no} for Assessment Year: {assessment_year} as PSR is already filled.")
    # If there are any remaining filled responses that haven't been written
    if filled_count > 0:
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, index=False, sheet_name='For PSR Checking-With TIN No.')
        print("Data has been written to Excel for remaining responses.")

    print("No more date available to process")




setup_logger()

while True:
    try:
        file_path, file_id = get_file_path(status="Processing", rpa_type="PSR")
        if file_path:
            try:
                verify_tax_return_using_api(file_path)
                update_file_status(file_id=file_id, status='Complete', remarks='')
            except Exception as e:
                print(f"Exception occurred: {e}")
                logging.error(f"Exception occurred: {e}")
                
                update_file_status(file_id=file_id, status='Error', remarks=f'{e}')
        else:
            print("No file found to process")
            logging.info("No file found to process")
            time.sleep(10)
    except Exception as e:
        print(f"Exception occured in get file api call: {e}")
        logging.error(f"Exception occurred in get file api call:{e}")
        time.sleep(30)