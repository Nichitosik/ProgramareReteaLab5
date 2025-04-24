import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from getpass import getpass

# Configurații Gmail
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993


def send_email(sender_email, app_password):
    """Trimite un email folosind SMTP."""
    try:
        # Creează mesajul
        recipient = input("Introdu adresa de email a destinatarului: ")
        subject = input("Introdu subiectul email-ului: ")
        body = input("Introdu mesajul: ")

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

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


def receive_emails(email_address, app_password):
    """Primește și afișează ultimele email-uri din inbox."""
    try:
        # Conectare la serverul IMAP
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(email_address, app_password)
        mail.select("inbox")

        # Caută toate email-urile
        result, data = mail.search(None, "ALL")
        email_ids = data[0].split()[-5:]  # Ultimele 5 email-uri

        print("\nUltimele 5 email-uri din inbox:")
        for email_id in email_ids:
            result, data = mail.fetch(email_id, "(RFC822)")
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)

            # Extrage detalii
            subject = msg["subject"]
            from_addr = msg["from"]
            print(f"De la: {from_addr}")
            print(f"Subiect: {subject}")
            print("-" * 50)

        mail.logout()
    except Exception as e:
        print(f"\nEroare la primirea email-urilor: {e}")


def menu():
    """Afișează meniul și gestionează opțiunile utilizatorului."""
    # Solicită credențialele o singură dată
    sender_email = input("Introdu adresa ta de email Gmail: ")
    app_password = getpass("Introdu parola de aplicație Gmail: ")

    while True:
        print("\n=== Client Email Gmail ===")
        print("1. Trimite email")
        print("2. Primește email-uri")
        print("3. Ieșire")

        option = input("Alege o opțiune (1-3): ")

        if option == "1":
            send_email(sender_email, app_password)
        elif option == "2":
            receive_emails(sender_email, app_password)
        elif option == "3":
            print("La revedere!")
            break
        else:
            print("Opțiune invalidă! Te rog alege din nou.")


if __name__ == "__main__":
    menu()