# import base64
# import os
# from email import encoders
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from email.mime.base import MIMEBase
#
# from utils.gmail.google import create_service
#
# CLIENT_SECRET_FILE = os.path.join('utils', 'gmail', 'client_secret.json')
# API_NAME = 'gmail'
# API_VERSION = 'v1'
# SCOPES = ['https://mail.google.com/']
#
# service = create_service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
# # emailMsg = 'You won $100,000'
# # address_me = 'alkin.denis@gmail.com'
# # msg_subject = 'Message Test'
#
#
# def send_message(email_msg, file, address, subject):
#     mime_message = MIMEMultipart()
#     mime_message['to'] = address
#     mime_message['subject'] = subject
#     mime_message.attach(MIMEText(email_msg, 'plain'))
#     record = MIMEBase('application', 'octet-stream')
#     with open(file, 'rb') as f:
#         file_b = f.read()
#     record.set_payload(file_b)
#     encoders.encode_base64(record)
#     record.add_header('Content-Disposition', 'attachment', filename=file)
#     mime_message.attach(record)
#     raw_string = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
#     message = service.users().messages().send(userId='me', body={'raw': raw_string}).execute()
#     print(message)
