import socket
import threading

HOST = input("Hostname: ")
PORT = 50051

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

nickname = input("Nickname: ")

def receive():
    while True:
        try:
            message = client.recv(1024).decode("ascii")
            if message == "NICK":
                client.send(nickname.encode("ascii"))
            else:
                print(message)
        except:
            print("error occurred")
            client.close()
            break

def send():
    while True:
        message = f"{nickname}: {input('Enter a message: ')}"
        client.send(message.encode("ascii"))
        
threading.Thread(target=receive).start()
threading.Thread(target=send).start()