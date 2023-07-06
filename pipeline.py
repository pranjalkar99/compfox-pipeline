import os
import aspose.words as aw
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader, PdfWriter
from fastapi import FastAPI, UploadFile
import json
import PyPDF2
import requests
import uuid
import requests
from tqdm import tqdm
import shutil
from google.cloud import storage
from split import make_batch
from upload_gcp import upload_folder_to_gcs
import io
from googleapiclient.http import MediaIoBaseDownload
gcs_new_input_bucket="compfox-pipeline-cases"
import ast
## fun for download from drive
from fastapi import FastAPI
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = FastAPI()
SCOPES = ['https://www.googleapis.com/auth/drive']
folder_id = '1bcSMpMHuojzK2eZD734PXSMPbgJo9WJ8'

# Load the service account key file
credentials = service_account.Credentials.from_service_account_file('compfox-367313-0c3890a157f2.json')
credentials = credentials.with_scopes(SCOPES)

# Configure the Google Drive client
drive_service = build('drive', 'v3', credentials=credentials)
with open('last_done.txt','r') as f:
    data = f.read()
last_list = ast.literal_eval(data)
def download_files_from_folder(folder_id, destination_folder):
    # Create destination folder if it doesn't exist
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # List all files in the folder
    response = drive_service.files().list(
        q=f"'{folder_id}' in parents and trashed=false",
        fields="files(id, name)"
    ).execute()
    files = response.get('files', [])
    print(last_list)
    org_list = [file['name'] for file in files]
    print(org_list)
    diff_list = [file for file in org_list if file not in last_list]
    print(diff_list)
    if diff_list:
        for file in files:
            if file['name'] in diff_list:
                file_id = file['id']
                file_name = file['name']
                file_path = os.path.join(destination_folder, file_name)

                # Download each file
                request = drive_service.files().get_media(fileId=file_id)
                fh = io.FileIO(file_path, mode='wb')
                downloader = MediaIoBaseDownload(fh, request)

                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    print(f"Downloaded {file_name}: {int(status.progress() * 100)}%")
    else:
        return "all files are already uploaded",diff_list
    return "Downloading finished",diff_list

@app.get("/")
def hello():
    return {"message": "Hello World"}

@app.get("/process_files")
def process_files():
    # Retrieve files from the Google Drive folder
    response = drive_service.files().list(q=f"'{folder_id}' in parents").execute()
    files = response.get('files')
    try:
        status,diff_list = download_files_from_folder(folder_id, 'static')
    
    except Exception as e:
        return {"message": f"error in drive download {str(e)}"}
    if diff_list:
        try:
            succes = make_batch('static','temp_output')
            shutil.rmtree('static')
        except Exception as e:
            return {"message": f"error in proccesing the files {str(e)}"}
        try:
            gcp_status = upload_folder_to_gcs(gcs_new_input_bucket,'temp_output/json_files')
            for f in diff_list:
                last_list.append(f)
            with open('last_done.txt','w') as s:
                s.write(str(last_list))
            shutil.rmtree('temp_output')
        except Exception as e:
            return {"message": f"error in gcp upload files {str(e)}"}
    else:
        return "all files are already proccesed"
    return {"gdrive": status,"proccsing":succes,"gcp":gcp_status}

@app.get("/remove_extra_png")
def remove_extra_png_files():
    folder_path = "."

    # Get a list of all files in the folder
    files = os.listdir(folder_path)

    # Filter the list to include only .png files
    png_files = [file for file in files if file.endswith(".png")]

    # Remove the extra .png files
    for png_file in png_files:
        file_path = os.path.join(folder_path, png_file)
        os.remove(file_path)

    return {"message": "Extra .png files removed"}
@app.get("/get_status")
def get_files():
    with open('last_done.txt','r') as f:
        data = f.read()
    files_list = ast.literal_eval(data)
    # List all files in the folder
    response = drive_service.files().list(
        q=f"'{folder_id}' in parents and trashed=false",
        fields="files(id, name)"
    ).execute()
    files = response.get('files', [])
    print(last_list)
    org_list = [file['name'] for file in files]
    print(org_list)
    diff_list = [file for file in org_list if file not in files_list]
    new_files = len(diff_list)
    print(diff_list)
    already_proccesed_files = len(files_list)
    return {'already_proccesed':already_proccesed_files,'new_files':new_files}
@app.get("/get_file_name")
def get_file_names():
    with open('last_done.txt','r') as f:
        data = f.read()
    files_name = ast.literal_eval(data)
    # List all files in the folder
    response = drive_service.files().list(
        q=f"'{folder_id}' in parents and trashed=false",
        fields="files(id, name)"
    ).execute()
    files = response.get('files', [])
    print(last_list)
    org_list = [file['name'] for file in files]
    print(org_list)
    diff_list = [file for file in org_list if file not in files_name]
    print(diff_list)
    already_proccesed_files = len(files_name)
    return {'already_proccesed':files_name,'new_files':diff_list}
