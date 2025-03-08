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
        self.chat_db.setup_database()

        self.room_setup_done_flag = threading.Event()

    def client_handler(self, conn):
        sender_username = conn.recv(1024).decode('utf-8')
        print(f"Got username {sender_username}")
        self.chat_db.store_user(sender_username.strip())

        client_info = ClientInfo(client_conn=conn, username=sender_username)

        print(f"setup")
        room_setup_thread = threading.Thread(target=self.room_setup, args=(conn, client_info))
        room_setup_thread.start()

        #listen for massages after setup
        print("listen")
        received_messages_thread = threading.Thread(target=self.receiving_messages, args=(conn,client_info,)) #get client info?
        received_messages_thread.start()

    def room_setup(self, conn, client_info):
        while True:
            room_type = conn.recv(1024).decode('utf-8')

            if RoomTypes[room_type.upper()] == RoomTypes.PRIVATE:
                group_name = conn.recv(1024).decode('utf-8')
                user_join_timestamp = conn.recv(1024).decode('utf-8')
                client_info.user_joined_timestamp = user_join_timestamp
                print(f"user join to room timestamp {user_join_timestamp}")

                self.chat_db.create_room(group_name)
                self.chat_db.send_previous_messages_in_room(client_info.client_conn, group_name, user_join_timestamp )
            else:
                group_name = room_type
                self.chat_db.create_room(group_name)
                self.chat_db.send_previous_messages_in_room(client_info.client_conn, group_name)


            client_info.room_type = room_type
            client_info.current_room = group_name
            self.room_name_to_active_clients[group_name].append(client_info)  # remove from mapping after client leave this room by switch or exit, check if noe exist

            self.room_setup_done_flag.set()

            print(f"client in setup: {client_info}")
            print(f"mapping room to clients: {self.room_name_to_active_clients}")

            break

    def receiving_messages(self, conn, client_info):
        #if not set dont send here
        print(f"client in receiving  {client_info}")
        while True:
                self.room_setup_done_flag.wait()

                if msg := conn.recv(2048).decode('utf-8'):
                    if msg == '/switch':
                        self.room_setup_done_flag.clear()

                        self.room_name_to_active_clients[client_info.current_room] =\
                            [client for client in self.room_name_to_active_clients[client_info.current_room]
                             if client.username != client_info.username]

                        print(f"removing client mapping: {self.room_name_to_active_clients}")

                        self.room_setup(conn, client_info)

                    else:
                        print(f"got message {msg}")
                        msg_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                        self.broadcast_to_all_clients_in_room(msg, client_info.current_room, client_info.username,msg_timestamp)
                        self.chat_db.store_message(msg, client_info.username, client_info.current_room, msg_timestamp)

    def broadcast_to_all_clients_in_room(self, msg, room_name, sender_name, msg_timestamp):
        #send to all active clients in the room
        if clients_in_room := self.room_name_to_active_clients.get(room_name):
            for client in clients_in_room:
                if client.current_room == room_name:
                    final_msg = f"[{msg_timestamp}] [{sender_name}]: {msg} "
                    client.client_conn.send(final_msg.encode('utf-8'))
                    print(f"send to {client.username}")

    def start(self):
        print("Server started...")
        while True:
            client_sock, addr = self.server.accept()
            print(f"Successfully connected client {addr[0]} {addr[1]}")
            thread = threading.Thread(target=self.client_handler, args=(client_sock,))
            thread.start()


def main():
    server = ChatServer(host='127.0.0.1', listen_port=1)
    server.start()


if __name__ == '__main__':
    main()

# todo upload and download files form other computers using q and threading
# todo add some ttl if x not happens in x time
