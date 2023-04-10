# cs262-design-exercise3

## Installation
Clone the repository
```bash
git clone https://github.com/jared-ni/cs262-design-exercise3.git
```
```bash
pip install -r requirements.txt 
```

## Setting up Servers and Clients
cd into the repository, then cd into the chat directory.
For each of the 3 servers, run the server by typing:
```bash
python server.py <port>
```
where <port> is the port that you want to server to connect on, and follow instructions to correctly set up this replica with other replicas.
Then, run the corresponding client:
```bash
python client.py
```
and follow the instructions to set up the connection to the server accordingly.
If multiple clients want to connect, repeat the above step in another terminal.

## Navigating the Chat App
The process when first connecting to the chat app as a client is intuitive and follows that of any other chat app (Messenger, WhatsApp, etc.)
Once the client connects to the server, the chat app prompts you to register for a user. If the client already is a 
registered user, then it can simply type "no". Then, chat app then prompts you to log in. Once logged in, the user receives any unseen messages sent to them while they were logged out and has the ability to access the main functionalities of the app.

Now, the user can assess various functionalities by typing:

**\<username\>: \<message\>**: sends \<message\> to \<username\> if \<username\> exists; sends immediately if \<username\> is logged on, else queues the message on the server.

**./register**: registers another user

**./login**: logs in another user

__./list *__: lists all users registered in the server; * is the text wildcard

**./delete \<username\>**: deletes \<username\> from server (prompts for \<username\> password)

**./disconnect**: logs user out (if logged in) and disconnects client, ending session

**./help**: lists these above commands in case user forgets

If the user receives a message from another user, it will show up on the user's 
terminal in the format **([\<username\>] \<message\>)**.


## Running Unit Tests
For running unit testts,s open up a terminal and nagivate to the 
directory containing server.py and client.py. Start the servers by typing
```bash
python server.py 12350
```
```bash
python server.py 12351
```
```bash
python server.py 12352
```
as the unit tests were written with the server ports being 12345, 12346, and 12347.

Now, open up another terminal and nagivate to the same directory and type
```bash
python -m unittest client.py
```
This will run all unit tests, testing individual functions of client.py and making
sure that messages are sent correctly from client to server to client.
