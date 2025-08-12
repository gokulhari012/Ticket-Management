from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
import shutil
from datetime import datetime

# Path to your Flask DB
# DB_PATH = "instance/your_database.db"  # change this path to match your Flask app
DB_PATH = "led_check.py"  # change this path to match your Flask app
FOLDER_ID = "1sfoiiyb-JtL4k6mUM_nNB0PtLAwyCRJB"
folder_path = "instance/backup/"
client_json_file_path = "static/client_secrets.json"

# Create folder if it doesn't exist
os.makedirs(folder_path, exist_ok=True)

# Authenticate Google Drive
gauth = GoogleAuth()
gauth.LoadClientConfigFile(client_json_file_path)
gauth.LoadCredentialsFile("mycreds.txt")

if gauth.credentials is None:
    # Authenticate if credentials not present
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    # Refresh credentials if expired
    gauth.Refresh()
else:
    # Initialize with saved creds
    gauth.Authorize()

gauth.SaveCredentialsFile("mycreds.txt")
drive = GoogleDrive(gauth)

# Prepare backup file
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

backup_filename = f"flask_db_backup_{timestamp}.db"
backup_file_path = folder_path + backup_filename
# os.system(f"cp {DB_PATH} {backup_filename}")  # Copy DB
shutil.copy(DB_PATH, backup_file_path)

# Upload to Google Drive
# file = drive.CreateFile({'title': backup_filename})

# Upload to specific folder
file = drive.CreateFile({
    'title': backup_filename,
    'parents': [{'id': FOLDER_ID}]
})
file.SetContentFile(backup_file_path)
file.Upload()

print(f"✅ Backup uploaded to Google Drive as {backup_filename}")

# Explicitly close the file handle
file.content.close()

# Optionally remove local backup copy
# Delete local backup
# try:
#     if os.path.exists(backup_filename):
#         os.remove(backup_filename)
#         print("✅ Local backup deleted")
#     else:
#         print("⚠ Backup file not found")
# except PermissionError:
#     print(f"⚠ Could not delete {backup_filename} (still in use)")