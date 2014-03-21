from constants import username, password
from emails import email_text, subject, from_email 
import sendgrid

def sendgrid_email(user_email):
    #Securely connect to SendGrid
    sg = sendgrid.SendGridClient(username, password, secure=True)
    #Make Empty Message
    message = sendgrid.Mail()
    #Add recipient
    message.add_to(user_email)
    #set the subject of the email
    message.set_subject(subject)
    #set the body of the message
    message.set_text(email_text)
    #set the message from field
    message.set_from(from_email)
    #send the message
    status, msg = sg.send(message)
    return

def send_emails():
    text_file = raw_input("Enter the name of the text file with emails in it: ")
    with open(text_file, 'r') as f:
        for user_email in f:
            sendgrid_email(user_email)
    return 

send_emails()
