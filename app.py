import tkinter as tk
from frontend.loginpage import LoginPage
import chat_service_pb2 as chat_service_pb2
import chat_service_pb2_grpc as chat_service_pb2_grpc
from client import Client 

class Application(tk.Tk):
    """
    Tkinter GUI application.
    """

    def __init__(self):
        """
        Initializes our application with a client object. Starts at the connect page.
        """
        tk.Tk.__init__(self)
        self._frame = None
        self.title("Chatroom")
        self.geometry("850x300")
        self.client = Client() 
        self.switch_frame(LoginPage)

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()

def run():
    app = Application()
    app.mainloop()

run()