import socket
import threading
import typing
from collections import defaultdict
from datetime import datetime

from client.chat_client import ClientInfo
from server.chat_db import ChatDB
from utils import RoomTypes

LISTENER_LIMIT = 5


class ChatServer:
    def __init__(self, *, host, listen_port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server.bind((host, listen_port))
        except Exception as e:
            print(f"Unable to bind to host and port : {repr(e)}")

        self.server.listen(5)

        self.active_clients: typing.Set[ClientInfo] = set()
        self.room_name_to_active_clients: typing.DefaultDict[str, typing.List[ClientInfo]] = defaultdict(list)

        self.chat_db = ChatDB()
        # self.chat_db.delete()
        self.chat_db.setup_database()

    def client_handler(self, conn):
        sender_username = conn.recv(1024).decode('utf-8')
        self.chat_db.store_user(sender_username.strip())

        client_info = ClientInfo(client_conn=conn, username=sender_username)

        room_type = conn.recv(1024).decode('utf-8')

        if RoomTypes[room_type.upper()] == RoomTypes.PRIVATE:
            group_name = conn.recv(1024).decode('utf-8')
            user_join_timestamp = conn.recv(1024).decode('utf-8')
            print(f"user join to room timestamp {user_join_timestamp}")

            self.chat_db.create_room(group_name)
            self.chat_db.send_previous_messages_in_room(client_info.client_conn, group_name, user_join_timestamp)
        else:
            group_name = room_type
            self.chat_db.create_room(group_name)
            self.chat_db.send_previous_messages_in_room(self.chat_db,client_info.client_conn, group_name)

        self.room_name_to_active_clients[group_name].append(client_info)  #remove from mapping after client leave this room by switch or exit, check if noe exist
        print(f"mapping room to clients: {self.room_name_to_active_clients}")

        while True:
            msg = conn.recv(2048).decode('utf-8')
            msg_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            self.broadcast_to_all_clients_in_room(msg, group_name, sender_username, msg_timestamp) #dont go to the receive section when user connected
            self.chat_db.store_message(msg, sender_username, group_name, msg_timestamp)

    def broadcast_to_all_clients_in_room(self, msg, room_name, sender_name, msg_timestamp):
        if clients_in_room := self.room_name_to_active_clients.get(room_name):
            for client in clients_in_room:
                if client.current_room == room_name: #check their conn
                    final_msg = f"[{msg_timestamp}] [{sender_name}]: {msg} \n"
                    client.client_conn.send(final_msg.encode('utf-8'))
                    print(f"print to {client.username}")
        print(f"broadcast messages to {clients_in_room} now supposed to receive")

    def start(self):
        print("Server started...")
        while True:
            client_sock, addr = self.server.accept()
            print(f"Successfully connected client {addr[0]} {addr[1]}")
            thread = threading.Thread(target=self.client_handler, args=(client_sock,))
            thread.start()


def main():
    server = ChatServer(host='127.0.0.1', listen_port=8)
    server.start()


if __name__ == '__main__':
    main()

# todo upload and download files form other computers using q and threading
# todo if i have the same functionality create utils.py
# todo manage mapping room_to_clients
# todo add some ttl if x not happens in x time
#todo when server exit then db will be deleted