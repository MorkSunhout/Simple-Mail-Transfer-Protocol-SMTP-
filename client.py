import socket
import threading
import getpass
import smtplib
from datetime import datetime

# constants for the socket connection
PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

# socket

def get_current_time():
    """Returns the current time formatted as a string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def connect():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    return client

def send(client, msg):
    try:
        message = msg.encode(FORMAT)
        client.sendall(message)
    except Exception as e:
        print(f"\033[1;31m[ERROR] Failed to send message: {e}\033[0m")

def receive(client):
    while True:
        try:
            message = client.recv(1024).decode(FORMAT)
            if message:
                print(f"\r\033[1;34m{message}\033[0m\n\033[1;32m{username}:\033[0m ", end="", flush=True)
        except Exception as e:
            print(f"\033[1;31m[ERROR] {e}\033[0m")
            break

# SMTP

def smtp(sender_email, receiver_email):
    """Send an email synchronously."""
    subject = input('SUBJECT: ')
    message = input('MESSAGE: ')
    
    text = f'Subject: {subject}\n\n{message}'
    
    # initializing connection
    smtp_client = smtplib.SMTP("smtp.gmail.com", 587)
    smtp_client.starttls()

    # login
    pwd = getpass.getpass(f'Enter password for {sender_email}: ')
    smtp_client.login(sender_email, pwd)

    # sending email
    smtp_client.sendmail(sender_email, receiver_email, text)
    print("\033[1;32m[EMAIL SENT] Your email has sent successfully.\033[0m")
    smtp_client.quit()

def handle_email():
    """Handle email sending process."""
    
    sender_email = input('Enter your email (sender): ')
    receiver_username = input('Enter receiver username: ')
    if not receiver_username.startswith('-'):
        receiver_username = f'-{receiver_username}'
    
    receiver_email = input('Enter receiver email: ')
    smtp(sender_email, receiver_email)
    send(connection, receiver_username)

# main

def start():
    global username, connection
    username = input('Enter username: ')
    answer = input(f'Would you like to connect with email: {username} (yes/no)? ')
    if answer.lower() != 'yes':
        return

    connection = connect()
    send(connection, username)

    # Start a thread to handle incoming messages
    receive_thread = threading.Thread(target=receive, args=(connection,))
    receive_thread.daemon = True
    receive_thread.start()

    while True:
        msg = input(f"\033[1;32m{username}:\033[0m ")  # Display username in green

        if msg.lower() == 'quit':
            send(connection, DISCONNECT_MESSAGE)
            break
        elif msg == '/email':
            print("\033[1;36m[Switching to Email Operation]\033[0m")
            handle_email()
            print("\033[1;36m[Back to Message Operation]\033[0m")
        else:
            send(connection, msg)

    print('\033[1;33mDisconnected\033[0m')
    connection.close()

start()
