import os
import base64
import logging
import pandas as pd

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send'
]

def authenticate_gmail():
    """Authenticate and return Gmail service."""
    creds = None
    if os.path.exists(r'credentials\token.json'):
        creds = Credentials.from_authorized_user_file(r'credentials\token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(r'credentials\credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open(r'credentials\token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)


def fetch_excel_attachment(folder: str = 'INBOX') -> str | None:
    """Fetch the first .xlsx attachment from Gmail that matches the sender and subject."""
    service = authenticate_gmail()

    # Customize your query as needed
    query = 'from:noreply@healtharkacademy.moodlecloud.com subject:"monthly user report" has:attachment'

    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    if not messages:
        logging.info("No matching emails found.")
        return None

    for msg in messages:
        msg_id = msg['id']
        message = service.users().messages().get(userId='me', id=msg_id).execute()
        parts = message['payload'].get('parts', [])

        for part in parts:
            filename = part.get('filename')
            if filename and filename.lower().endswith('.xlsx'):
                attachment_id = part['body'].get('attachmentId')
                if not attachment_id:
                    continue

                attachment = service.users().messages().attachments().get(
                    userId='me', messageId=msg_id, id=attachment_id
                ).execute()

                file_data = base64.urlsafe_b64decode(attachment['data'])

                os.makedirs('Documents', exist_ok=True)
                filepath = os.path.join('Documents', filename)
                with open(filepath, 'wb') as f:
                    f.write(file_data)

                logging.info(f"Downloaded: {filepath}")
                return filepath

    return None


def load_report(filepath: str) -> pd.DataFrame:
    df = pd.read_excel(filepath)

    if 'Student progress' in df.columns:
        df['Student progress'] = pd.to_numeric(
            df['Student progress'].astype(str).str.rstrip('%'), errors='coerce'
        )
    return df