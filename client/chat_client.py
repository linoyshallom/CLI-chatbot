import dataclasses
import socket
import threading
import uuid
from tokenize import group

from utils.utils import RoomTypes

@dataclasses.dataclass
class ClientInfo:
    client_conn: socket
    username: str
    current_room = None


class ChatClient:
    def __init__(self,* , host, listen_port):
        self.client =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.client.connect((host,listen_port))
            print(f"Successfully connected to server")

        except Exception as e:
            raise Exception(f"Unable to connect to server {host,listen_port} {repr(e)} ")

        self.username = input("Enter your username:")  #todo validate username by regex and not empty
        self.choose_room()

        #displsy messages in the chosen room
        received_thread = threading.Thread(target=self.receive_message)
        received_thread.start()

        self.send_message()

    def choose_room(self):
        group_name = '' #
        print(f"Available rooms to chat:")
        for room in RoomTypes:
            print(f"- {room.value}")
        chosen_room = input("Enter room type: ")
        try:
            if room_type := RoomTypes[chosen_room.upper()]:
                self.client.send(self.username.encode('utf-8'))
                self.client.send(chosen_room.strip().upper().encode('utf-8'))

                if room_type == RoomTypes.PRIVATE:
                    group_name = input("Enter private group name you want to chat: ")
                    self.client.send(group_name.strip().encode('utf-8'))

                print(f"sending {self.username} {chosen_room} {group_name} to server")

        except KeyError:
            print(f"\n Got unexpected room name {chosen_room}, try again")

    def send_message(self):
        while True:
            self.choose_room()

            while True:
                msg = input("Write a message: ")  #validate
                #save_message?

                if msg.lower() == "/switch":
                    break

                self.client.send(msg.encode('utf-8'))  #add option to write messages during the chatting

    def receive_message(self):
        while True:
            try:
                if msg := self.client.recv(2048).decode('utf-8'):
                    print(msg) #display in room

            except Exception as e:
                raise f"Cannot receiving messages... \n {repr(e)}"



    # if msg is file:
    #     #put in q cause i can get files from many clients asyncronic and activate send file thread
    # if msg is switch room /room
    # if message is exit then break

    # def send_file(self):
    #     #handle unexist file
    #     #if msg == '/exit' break
    #     ...


def main():
    _ = ChatClient(host='127.0.0.1', listen_port=3)

if __name__ == '__main__':
    main()

#todo users can create new room rather then joining, leave a gruop
#todo room switching first global then room1 (spesifc command /room or maybe go to strat and pick)
#todo validate path, username and message
#todo File Transfer - needs to occurs parallel so maybe thread of transfer and other of the chat management