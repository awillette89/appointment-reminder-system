import os
import pandas as pd
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def load_appointments():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, 'appointments.xlsx')
    print(f"Loading appointments from {file_path}")
    df = pd.read_excel(file_path)
    print("Appointments loaded successfully")
    return df

def get_upcoming_appointments(df):
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    print(f"Today's date: {today}")
    print(f"Looking for appointments on: {tomorrow}")

    df['AppointmentDate'] = pd.to_datetime(df['AppointmentDate'])
    upcoming_appointments = df[df['AppointmentDate'].dt.date == tomorrow.date()]
    print(f"Found {len(upcoming_appointments)} upcoming appointments")
    return upcoming_appointments

def create_message(row):
    appointment_time = row['AppointmentDate'].strftime('%I:%M %p')
    appointment_date = row['AppointmentDate'].strftime('%B %d, %Y')

    message = f"""
    Dear {row['PatientName']},

    This is a friendly reminder of your appointment scheduled for:
    Date: {appointment_date}
    Time: {appointment_time}

    Please arrive 15 minutes early to complete any necessary paperwork.

    If you need to reschedule, please call us at (555) 555-5555.

    Best regards,
    Your Medical Office
    """
    print(f"Created message for {row['PatientName']}")
    return message

def send_email(service, sender_email, recipient_email, subject, message_text):
    message = MIMEMultipart()
    message['to'] = recipient_email
    message['from'] = sender_email
    message['subject'] = subject
    message.attach(MIMEText(message_text, 'plain'))
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    body = {'raw': raw}
    try:
        message = service.users().messages().send(userId='me', body=body).execute()
        print(f"Message Id: {message['id']}")
        return message
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    credentials_path = os.path.join(script_dir, 'credentials.json')
    token_path = os.path.join(script_dir, 'token.json')

    print(f"Current working directory: {os.getcwd()}")
    print(f"Credentials file exists: {os.path.exists(credentials_path)}")

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    sender_email = "YOUREMAILCHANGETHIS@gmail.com"

    appointments_df = load_appointments()
    tomorrow_apps = get_upcoming_appointments(appointments_df)

    for index, row in tomorrow_apps.iterrows():
        print(f"\nProcessing appointment for {row['PatientName']}")
        message_text = create_message(row)
        recipient_email = row['Email']
        send_email(service, sender_email, recipient_email, "Appointment Reminder", message_text)

    print("\nAll reminders sent.")

if __name__ == '__main__':
    main()