import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def send_email_with_attachment(smtp_server, smtp_port, sender_email, sender_password, recipient_email, subject, body_html, pdf_path):
    # Create a multipart message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Attach the HTML body to the message
    msg.attach(MIMEText(body_html, 'html'))

    # Attach the PDF file
    with open(pdf_path, 'rb') as f:
        pdf_attachment = MIMEApplication(f.read(), _subtype="pdf")
        pdf_attachment.add_header('Content-Disposition', 'attachment', filename=pdf_path.split('/')[-1])
        msg.attach(pdf_attachment)

    # Set up the SMTP server connection
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
        server.login(sender_email, sender_password)
        server.send_message(msg)
        print("Email sent successfully!")

# Example usage
smtp_server = 'smtp.example.com'   # Replace with actual SMTP server
smtp_port = 587                    # Usually 587 for TLS
sender_email = 'your_email@example.com'
sender_password = 'your_password'
recipient_email = 'recipient@example.com'
subject = 'Test Email with PDF Attachment'
body_html = '<h1>This is a test email</h1><p>Check the attached PDF.</p>'
pdf_path = '/path/to/your/file.pdf'  # Replace with actual PDF path

send_email_with_attachment(smtp_server, smtp_port, sender_email, sender_password, recipient_email, subject, body_html, pdf_path)
