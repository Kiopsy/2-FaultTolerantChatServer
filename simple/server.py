import socket
import threading
import multiprocessing

host = socket.gethostbyname(socket.gethostname())
port = 50051

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()
print(f"Listening at {host}:{port}.")

clients = []
nicknames = []

def broadcast(message):
    for client in clients:
        client.send(message)

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f"{nickname} left the chat".encode("ascii"))
            nicknames.remove(nickname)
            break

def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with {address}")
        
        client.send("NICK".encode("ascii"))
        nickname = client.recv(1024).decode("ascii")
        nicknames.append(nickname)
        clients.append(client)

        broadcast(f"{nickname} joined the chat".encode("ascii"))
        # client.send("Connected to server".encode("ascii"))

        threading.Thread(target=handle, args=(client,)).start()

print(f"Server is listening at {host} : {port}....")
receive() 
