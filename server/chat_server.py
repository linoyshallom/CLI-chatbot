import socket
import sqlite3
import threading
import typing
from datetime import datetime
from collections import defaultdict
from tokenize import group

from client.chat_client import ClientInfo
from utils import RoomTypes

# from utils import RoomTypes

LISTENER_LIMIT = 5

class ChatServer:
    def __init__(self, *, host, listen_port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server.bind((host, listen_port))
        except Exception as e:
            print(f"Unable to bind to host and port : {repr(e)}")

        self.server.listen(5)

        self.active_clients: typing.Set[ClientInfo] = set() # send msg to all active and update db, i wont send to unconnected client , hw will fetch it when he only gt to the room
        self.rooms_to_clients: typing.DefaultDict[RoomTypes,typing.List[ClientInfo]]= defaultdict(list)
        self.db = sqlite3.connect('chat.db')
        self.cursor = self.db.cursor()



    def client_handler(self, conn):       #update db, clients duplicate manage
        username= conn.recv(1024).decode('utf-8')
        client_info = ClientInfo(client_conn=conn, username=username)
        user_id = ...
        #self.save_usr_name()
        room_type= conn.recv(1024).decode('utf-8')
        group_name = conn.recv(1024).decode('utf-8')

        print(f"server got room {room_type}, {type(room_type)}")

        while True:
            msg = conn.recv(2048).decode('utf-8')
            print(f"server got msg {msg}")
            if RoomTypes[room_type.upper()] == RoomTypes.PRIVATE:

                print(f"server got group name {group_name}")
                #save_message()
                #save_message_in_rooom?

            else:
                group_name = room_type
                self.broadcast(username, room_type, msg)
                # self.save_message()

            # room_creation() , get_room_id()

            client_info.current_room = group_name

            self.active_clients.add(client_info)
            self.rooms_to_clients[RoomTypes[room_type]].append(client_info)
            print(self.rooms_to_clients)


    def send_message_to_room(self, conn, room_id):
        ...


    # Send messages to all clients that are currently connected to the server
    def broadcast(self, sender_username, room, msg):
        a = self.rooms_to_clients.get(RoomTypes[room])
        print(a)
        if clients_in_room  := self.rooms_to_clients.get(RoomTypes[room]):
            print(f"clients in room {clients_in_room}")
            for client in clients_in_room:
                final_msg = f"{datetime.now()} {sender_username} {msg}"
                client.client_conn.send(final_msg.encode('utf-8'))  #json with time-user-msg
        else:
            print("Message")

    def setup_database(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL
            );
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_name TEXT UNIQUE NOT NULL
            );
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            room_id INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users(id), 
            FOREIGN KEY (room_id) REFERENCES rooms(id) 
            );
        ''')

        #rooms- messages
        self.db.commit()

    def store_user(self, username):
        self.cursor.execute('INSERT IGNORE INTO users (usernames) VALUES (?)', (username,))
        self.db.commit()
        ...

    def store_message(self, text_message, sender_id, room_id, timestamp):
        self.cursor.execute('''
        INSERT INTO messages (text_message, sender_id, room_id, timestamp)
        VALUES (?,?,?,?)''', (text_message, sender_id, room_id, timestamp))
        self.db.commit()

    def get_stored_messages(self, room_id):
        ...

    def send_messages_for_room(self, conn, room_id):
        ...

    def room_creation(self, room_name):
        self.cursor.execute('INSERT IGNORE INTO rooms (room_name) VALUES (?)', (room_name,))
        self.db.commit()

    def get_room_id(self, room_name) -> int:
        self.cursor.execute('SELECT id FROM rooms WHERE room_name = ?', (room_name,))
        return self.cursor.fetchone()[0]






    #
    # def table_creation(self):
    #     ...
    #
    # def store_message(self):
#          ...
    # def file_transfer_handler(self):
    #     ...



    def start(self):
        print("Server started...")
        while True:
            client_sock, addr = self.server.accept()
            print(f"Successfully connected client {addr[0]} {addr[1]}")
            thread = threading.Thread(target=self.client_handler, args=(client_sock,))
            thread.start()



def main():
    server = ChatServer(host='127.0.0.1', listen_port=3)
    server.start()

if __name__ == '__main__':
    main()


#todo upload and download files form other computers using q and threading
#todo if i have the same functionality create utils.py
#todo manage mapping room_to_clients
#todo clients in global are clients that have login or just clients that picks this ?
# add some ttl if x not happens in x time
#todo solving switching port all the time
