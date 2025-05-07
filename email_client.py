import smtplib
import imaplib
import poplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from getpass import getpass
import os

# Configurații Gmail
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993
POP3_SERVER = "pop.gmail.com"
POP3_PORT = 995

def send_email(sender_email, app_password):
    """Trimite un email folosind SMTP, cu opțiune pentru atașamente și reply-to."""
    try:
        # Creează mesajul
        recipient = input("Introdu adresa de email a destinatarului: ")
        subject = input("Introdu subiectul email-ului: ")
        reply_to = input("Introdu adresa Reply-To (lasă gol dacă nu dorești): ")
        body = input("Introdu mesajul: ")

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = subject
        if reply_to:
            msg['Reply-To'] = reply_to
        msg.attach(MIMEText(body, 'plain'))

        # Adaugă atașament dacă utilizatorul dorește
        add_attachment = input("Dorești să adaugi un atașament? (da/nu): ").lower()
        if add_attachment == 'da':
            file_path = input("Introdu calea completă a fișierului: ")
            if os.path.exists(file_path):
                with open(file_path, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(file_path)}'
                )
                msg.attach(part)
            else:
                print("Fișierul nu există!")

        # Conectare la serverul SMTP
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Activează TLS
        server.login(sender_email, app_password)

        # Trimite email-ul
        server.send_message(msg)
        server.quit()
        print("\nEmail trimis cu succes!")
    except Exception as e:
        print(f"\nEroare la trimiterea email-ului: {e}")

def receive_emails_imap(email_address, app_password):
    """Primește și afișează ultimele email-uri din inbox folosind IMAP, cu opțiunea de a descărca atașamente."""
    try:
        # Conectare la serverul IMAP
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(email_address, app_password)
        mail.select("inbox")

        # Caută toate email-urile
        result, data = mail.search(None, "ALL")
        email_ids = data[0].split()[-5:]  # Ultimele 5 email-uri

        print("\nUltimele 5 email-uri din inbox (IMAP):")
        for email_id in email_ids:
            result, data = mail.fetch(email_id, "(RFC822)")
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)

            # Extrage detalii
            subject = msg["subject"] if msg["subject"] else "(Fără subiect)"
            from_addr = msg["from"] if msg["from"] else "(Necunoscut)"
            print(f"De la: {from_addr}")
            print(f"Subiect: {subject}")

            # Descarcă atașamentele dacă există
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue
                    filename = part.get_filename()
                    if filename:
                        save_path = os.path.join("attachments", filename)
                        os.makedirs("attachments", exist_ok=True)
                        with open(save_path, 'wb') as f:
                            f.write(part.get_payload(decode=True))
                        print(f"Atașament salvat: {save_path}")
            print("-" * 50)

        mail.logout()
    except Exception as e:
        print(f"\nEroare la primirea email-urilor (IMAP): {e}")

def receive_emails_pop3(email_address, app_password):
    """Primește și afișează ultimele email-uri din inbox folosind POP3, cu opțiunea de a descărca atașamente."""
    try:
        # Conectare la serverul POP3
        mail = poplib.POP3_SSL(POP3_SERVER, POP3_PORT)
        mail.user(email_address)
        mail.pass_(app_password)

        # Obține numărul de email-uri
        num_messages = len(mail.list()[1])
        start_index = max(1, num_messages - 4)  # Ultimele 5 email-uri

        print("\nUltimele 5 email-uri din inbox (POP3):")
        for i in range(start_index, num_messages + 1):
            # Obține email-ul
            response, lines, octets = mail.retr(i)
            raw_email = b'\n'.join(lines)
            msg = email.message_from_bytes(raw_email)

            # Extrage detalii
            subject = msg["subject"] if msg["subject"] else "(Fără subiect)"
            from_addr = msg["from"] if msg["from"] else "(Necunoscut)"
            print(f"De la: {from_addr}")
            print(f"Subiect: {subject}")

            # Descarcă atașamentele dacă există
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue
                    filename = part.get_filename()
                    if filename:
                        save_path = os.path.join("attachments", filename)
                        os.makedirs("attachments", exist_ok=True)
                        with open(save_path, 'wb') as f:
                            f.write(part.get_payload(decode=True))
                        print(f"Atașament salvat: {save_path}")
            print("-" * 50)

        mail.quit()
    except Exception as e:
        print(f"\nEroare la primirea email-urilor (POP3): {e}")

def menu():
    """Afișează meniul și gestionează opțiunile utilizatorului."""
    # Solicită credențialele o singură dată
    sender_email = input("Introdu adresa ta de email Gmail: ")
    app_password = getpass("Introdu parola de aplicație Gmail: ")

    while True:
        print("\n=== Client Email Gmail ===")
        print("1. Trimite email")
        print("2. Primește email-uri (IMAP)")
        print("3. Primește email-uri (POP3)")
        print("4. Ieșire")

        option = input("Alege o opțiune (1-4): ")

        if option == "1":
            send_email(sender_email, app_password)
        elif option == "2":
            receive_emails_imap(sender_email, app_password)
        elif option == "3":
            receive_emails_pop3(sender_email, app_password)
        elif option == "4":
            print("La revedere!")
            break
        else:
            print("Opțiune invalidă! Te rog alege din nou.")

if __name__ == "__main__":
    menu()