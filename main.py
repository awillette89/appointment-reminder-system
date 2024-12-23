import pandas as pd
from datetime import datetime, timedelta
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

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

def setup_email():
    smtp_server = "localhost"
    port = 1025
    print(f"Setting up email server at {smtp_server}:{port}")
    server = smtplib.SMTP(smtp_server, port)
    print("Email server setup successfully")
    return server, "sender@example.com"

print("Starting appointment reminder script")

appointments_df = load_appointments()
tomorrow_apps = get_upcoming_appointments(appointments_df)

server, sender_email = setup_email()

for index, row in tomorrow_apps.iterrows():
    print(f"\nProcessing appointment for {row['PatientName']}")
    message = create_message(row)
    recipient = row['Email']
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = "Appointment Reminder"
        msg.attach(MIMEText(message, 'plain'))
        server.sendmail(sender_email, recipient, msg.as_string())
        print(f"Reminder sent to {recipient}")
    except Exception as e:
        print(f"Error sending email to {recipient}: {str(e)}")

server.quit()
print("\nAll reminders sent.")