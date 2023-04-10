import grpc, time, random, threading, socket
import chat_service_pb2
import chat_service_pb2_grpc
from helpers import TwoFaultStub

class Client:
    def __init__(self) -> None:
        self.stub = TwoFaultStub()
        self.connected = self.stub.connect()
        self.username = None
    
    def receive_messages(self):
        """
        Retrieve messages from the server/stub associated with our current user 
        """
        message = self.stub.ReceiveMessage(chat_service_pb2.User(username = self.username))
        if message.sender == "":
            return []      
        return [message]

    def send_message(self, recipient, content):
        """
        Sends a message (content) to the recipient.
        """
        # Create a message request
        request = chat_service_pb2.SendRequest(sender = self.username, recipient = recipient, content = content)
            
        # Send message to the server via stub
        response = self.stub.SendMessage(request)

        return response

    def get_users(self):
        """
        Returns a list of usernames currently stored with the server's database. 
        """
        userObjs = self.stub.GetUsers(chat_service_pb2.Empty()) 
        users = [userObj.username for userObj in userObjs]
        users.remove(self.username)
        return users

    def login(self, username, password):
        """
        Tries to login by checking credentials with the server. 

        Returns a response code representing login success/error. 
        """
        request = chat_service_pb2.LoginRequest(username=username, password=password)
        response = self.stub.Login(request)

        # Sets global user given login success
        if response.success:
            self.username = username

        return response
    
    def delete_account(self):
        """
        Delete's the client's account from the server's database.
        """
        request = chat_service_pb2.DeleteRequest(username = self.username)
        response = self.stub.Delete(request)
        return response

    def register(self, username, password):
        """
        Registers a user with the server's database with given credentials. 

        Returns a response code representing register success/error. 
        """
        request = chat_service_pb2.RegisterRequest(username=username, password=password)
        response = self.stub.Register(request)

        # Sets global user given register success
        if response.success:
            self.username = username

        return response 


