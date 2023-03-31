import tkinter as tk
from tkinter import messagebox
import threading
import sys
 
class HomePage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master
        self.receiving = True  # Exit boolean to stop receive messages thread
        self.messages_list = tk.Listbox(self, height=15, width=50)
        self.messages_list.grid(row=0, column=0, rowspan=2, padx=10, pady=10)
        self.options = self.master.client.get_users()
        self.options = self.options if self.options else [" "]
        self.recipient = tk.StringVar()
        self.dropdown = tk.OptionMenu(self, self.recipient, *self.options, command=self.recipient_selected)
        self.dropdown.grid(row=0, column=1, padx=10, pady=10)
        self.message_input = tk.Text(self, height=3, width=30)
        self.message_input.grid(row=0, column=2, sticky="W", padx=10, pady=10)
        self.send_button = tk.Button(self, text="Send", command=self.send_message)
        self.send_button.grid(row=1, column=1, sticky="E", padx=10, pady=10)
        self.reset_button = tk.Button(self, text="Reset Options", command=self.reset_dropdown)
        self.reset_button.grid(row=1, column=2, sticky="E", padx=0, pady=0)
        self.delete_button = tk.Button(self, text="Delete Account", command=self.delete_account)
        self.delete_button.grid(row=2, column=2, sticky="E", padx=0, pady=0)
        threading.Thread(target = self.receive_messages).start() # Recieve messages constantly in a thread
    
    def send_message(self):
        # Send message to a recipient selected in the dropdown.
        body = self.message_input.get("1.0", 'end-1c')

        # Msg error checking
        if len(body) == 0 or len(self.recipient.get()) == 0:
            messagebox.showerror("Message Send Failed", "Cannot send empty messages")
            return
        if self.recipient.get() == self.master.client.username:
            messagebox.showerror("Message Send Failed", "Cannot send messages to yourself")
            return
        
        # Send the message to the server and add it to our message list
        response = self.master.client.send_message(self.recipient.get(), body)
        if response.success:
            self.add_message(self.recipient.get(), body)
        else:
            messagebox.showerror("Message Send Failed", response.message)
            self.reset_dropdown()

        # Reset text input
        self.message_input.delete("1.0", tk.END) 

    def receive_messages(self):
        # Receives messages and adds them to the inbox continuously
        while True and self.receiving:
            messages = self.master.client.receive_messages()
            for message in messages:
                self.add_message(message.sender, message.content, True)

    def add_message(self, other, body, receiver = False):
        # Adds a message to user's inbox
        message = f"{other}: {body}" if receiver else f"You -> {other}: {body}"
        self.messages_list.insert("end", message)

    def delete_account(self):
        # Deletes the client's account from the server's database
        result = messagebox.askquestion("Delete", "Are You Sure?", icon='warning')
        if result == 'yes':
            self.master.client.delete_account()
            # Destroy GUI and stop receiving messages
            self.receiving = False 
            self.master.destroy()

    def reset_dropdown(self):
        self.dropdown.destroy()
        self.options = self.master.client.get_users()
        self.options = self.options if self.options else [" "]
        self.recipient = tk.StringVar()
        self.dropdown = tk.OptionMenu(self, self.recipient, *self.options, command=self.recipient_selected)
        self.dropdown.grid(row=0, column=1, padx=10, pady=10)
        self.message_input.delete("1.0", tk.END)

    def recipient_selected(self, *args):
        pass