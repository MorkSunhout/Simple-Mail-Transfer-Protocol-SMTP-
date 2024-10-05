import threading
import socket
from datetime import datetime

# server config
PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

# create socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = {}
clients_lock = threading.Lock()

def get_current_time():
    """Returns the current time formatted as a string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# handle client connections
def handle_client(conn, addr):
    try:
        username = conn.recv(1024).decode(FORMAT)
        print(f"\r\033[1m[{get_current_time()}] [NEW CONNECTION]\033[0m {addr} with username: \033[1m{username}\033[0m connected.\n\033[1;36m[Server Message]:\033[0m ", end="", flush=True)
        
        with clients_lock:
            clients[username] = conn
        
        join_message = f"\033[3m{username} joined the room\033[0m"
        broadcast_message(join_message, conn)

        connected = True
        while connected:
            msg = conn.recv(1024).decode(FORMAT)
            if not msg:
                break

            if msg == DISCONNECT_MESSAGE:
                connected = False
                disconnect_message = f"\033[3m{username} has left the chat.\033[0m"
                print(disconnect_message)
                broadcast_message(disconnect_message, conn)
            elif msg.startswith('@'):
                target_usr_name = msg.split('@')[1].split()[0]
                with clients_lock:
                    if target_usr_name in clients:
                        private_msg = f'\033[1;33m[PRIVATE] {username}: {msg}\033[0m'
                        target_conn = clients[target_usr_name]
                        try:
                            target_conn.send(private_msg.encode(FORMAT))
                            print(f'\r\033[1;33m[PRIVATE] {username} to {target_usr_name}: {msg} \033[0m\n\033[1;36m[Server Message]:\033[0m', end='', flush=True)
                        except Exception as e:
                            print(f"\033[1;31m[ERROR] Could not send private message: {e}\033[0m")
                    else:
                        error_msg = f'\033[1;31mUser @{target_usr_name} not found!\033[0m'.encode(FORMAT)
                        conn.send(error_msg)
            elif msg.startswith('-'):
                target_usr_name = msg[1::]
                with clients_lock:
                    if target_usr_name in clients:
                        email_noti = f'\033[1;33mYou have received an email from {username}.\033[0m'
                        target_conn = clients[target_usr_name]
                        try:
                            target_conn.send(email_noti.encode(FORMAT))
                            print(f'\r\033[1;33m{get_current_time()} {username} has sent email to {target_usr_name} \033[0m\n\033[1;36m[Server Message]:\033[0m', end='', flush=True)
                        except Exception as e:
                            print(f"\033[1;31m[ERROR] Could not send email notification: {e}\033[0m")
                    else:
                        error_msg = f'\033[1;31mUser @{target_usr_name} not found!\033[0m'.encode(FORMAT)
                        conn.send(error_msg)
            else:
                formatted_message = f"[{get_current_time()}] {username}: {msg}             "
                print(f"\r\033[1m{formatted_message}\033[0m\n\033[1;36m[Server Message]:\033[0m ", end="", flush=True)
                broadcast_message(formatted_message, conn)

    finally:
        with clients_lock:
            del clients[username]
        conn.close()

# broadcast message
def broadcast_message(message, sender_conn=None):
    with clients_lock:
        for c_username, c_conn in clients.items():
            if c_conn != sender_conn:
                try:
                    c_conn.sendall(message.encode(FORMAT))
                except Exception as e:
                    print(f"\033[1;31m[ERROR] Failed to send message to {c_username}: {e}\033[0m")

# handle server-side input
def server_input():
    while True:
        message = input("\033[1;36m[Server Message]:\033[0m ")
        if message:
            broadcast_message(f"\033[1;36m[Server]: {message}        \033[0m")

# start the server
def start():
    print('\033[1;32m[SERVER STARTED]!\033[0m')
    server.listen()

    threading.Thread(target=server_input, daemon=True).start()

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        
start()
