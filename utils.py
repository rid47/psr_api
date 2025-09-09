import requests
from decouple import config


# ------------------- Get file with specific status and RPA type -------------------
def get_file_path(status: str = 'Processing', rpa_type: str = 'PSR'):
    url = config('get_file_url')
    payload = {"status": status, "rpa_type": rpa_type}
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        # Returns the file path from the DB
        return data["file_path"], data["id"]
    else:
        print(f"response={response.json()}")
        return None, None

# ------------------- Update file status and remarks -------------------
def update_file_status(file_id: int, status: str, remarks: str = ""):
    url = config('update_file_url')
    payload = {"file_id": file_id, "status": status, "remarks": remarks}
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print(f"File updated successfully: {response.json()}")
        return True
    else:
        print(f"response={response.json()}")
        return False


# # ------------------- Example Usage -------------------
# if __name__ == "__main__":
#     # Get next processing file for RPA type 'PSR'
#     file_path, file_id = get_file_path(status="Processing", rpa_type="PSR")
#     if file_path:
#         print(f"Processing file: {file_path}")
        
#         # Do some processing here...
        
#         # Update status to Complete
#         update_file_status(file_id=file_id, status="Complete", remarks="Processed successfully")
#     else:
#         print("No file found to process")
