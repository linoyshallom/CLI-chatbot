import dataclasses
import socket
import threading
import typing
from datetime import datetime

from utils.utils import RoomTypes


@dataclasses.dataclass
class ClientInfo:
    client_conn: socket.socket
    username: str
    room_type: RoomTypes = None #no room at first
    current_room: typing.Optional[str] = None
    user_joined_timestamp:typing.Optional[datetime] = None


class ChatClient:
    def __init__(self,* , host, listen_port):
        self.client =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.received_history_flag = threading.Event()
        self.receive_message_flag = threading.Event()

        try:
            self.client.connect((host,listen_port))
            print(f"Successfully connected to server")

        except Exception as e:
            raise Exception(f"Unable to connect to server {host,listen_port} {repr(e)} ")

        self.username = input("Enter your username:")  #todo validate username by regex and not empty
        self.client.send(self.username.encode('utf-8'))


        self.choose_room()

        send_thread = threading.Thread(target=self.send_message(), daemon=True)
        send_thread.start()

    def choose_room(self):
        while True:
            group_name = '' #
            print(f"Available rooms to chat:")
            for room in RoomTypes:
                print(f"- {room.value}")

            chosen_room = input("Enter room type: ").strip().upper()
            try:

                if room_type := RoomTypes[chosen_room.upper()]:
                    self.client.send(chosen_room.encode('utf-8'))

                    if room_type == RoomTypes.PRIVATE:
                        group_name = input("Enter private group name you want to chat: ").strip()
                        self.client.send(group_name.encode('utf-8'))

                        join_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        self.client.send(join_timestamp.encode('utf-8'))

                    print(f"Joined {chosen_room} {group_name}")
                    print(f"receives all past messages before sending messages")
                    received_thread = threading.Thread(target=self.receive_message,
                                                       daemon=True)  # Automatically stop when the main program exits.
                    received_thread.start()

                    self.received_history_flag.wait() #waiting this to be set before sending a message
                    self.receive_message_flag.wait()

                    break

            except KeyError:
                print(f"\n Got unexpected room name {chosen_room}, try again")

    def receive_message(self):
        while True:
            try:
                if msg := self.client.recv(2048).decode('utf-8'):
                    if msg == 'END_HISTORY_RETRIEVAL':
                        self.received_history_flag.set()
                        self.receive_message_flag.set()
                        continue

                    print(msg)
                    self.receive_message_flag.set()

            except Exception as e:
                # Ensure conn.recv() doesn’t block forever (consider adding a timeout if needed).
                self.client.close()
                raise f"Cannot receiving messages... \n {repr(e)}"

    def send_message(self):
        # Wait until history is completely received, waiting for .set()
        self.received_history_flag.wait()

        while True:
            if self.receive_message_flag.wait(3):
                msg = input(f"Enter your message :  ")

            else:
                msg = input(f"Enter your message :  ") #still send a message if flag wasn't set

            try:
                if msg.lower() == "/switch":
                    self.client.send(msg.encode('utf-8'))
                    self.received_history_flag.clear()
                    self.choose_room()
                else:
                    self.client.send(msg.encode('utf-8'))

                #block writing before receiving again
                self.receive_message_flag.clear()

            except Exception as e:
                raise f"Error sending message: {repr(e)}"


def main():
    _ = ChatClient(host='127.0.0.1', listen_port=1)

if __name__ == '__main__':
    main()


    # if msg is file:
    #     #put in q cause I can get files from many clients asyncronic and activate send file thread
    # def send_file(self):
    #     #handle unexist file , chunkify

#todo validate path, username and message
#todo File Transfer - needs to occurs parallel so maybe thread of transfer and other of the chat management