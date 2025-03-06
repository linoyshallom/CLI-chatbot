import dataclasses
import socket
import threading
from datetime import datetime

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

        #displsy messages in the chosen room
        print(f"receiving messages section")
        received_thread = threading.Thread(target=self.receive_message, daemon=True)  #Automatically stop when the main program exits.
        received_thread.start()

        self.choose_room()

        send_thread = threading.Thread(target=self.send_message(), daemon=True)
        send_thread.start()

        send_thread.join()


    def choose_room(self):
        while True:
            group_name = '' #
            print(f"Available rooms to chat:")
            for room in RoomTypes:
                print(f"- {room.value}")

            chosen_room = input("Enter room type: ").strip().upper()
            try:

                if room_type := RoomTypes[chosen_room.upper()]:
                    self.client.send(self.username.encode('utf-8'))
                    self.client.send(chosen_room.encode('utf-8'))

                    if room_type == RoomTypes.PRIVATE:
                        group_name = input("Enter private group name you want to chat: ").strip()
                        self.client.send(group_name.encode('utf-8'))

                        join_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        self.client.send(join_timestamp.encode('utf-8'))

                    print(f"Joined {chosen_room} {group_name}")
                    break

            except KeyError:
                print(f"\n Got unexpected room name {chosen_room}, try again")

    def receive_message(self):
        while True:
            try:
                if msg := self.client.recv(2048).decode('utf-8'):
                    print(msg)

            except Exception as e:
                self.client.close()
                raise f"Cannot receiving messages... \n {repr(e)}"

    def send_message(self):
        while True:
            msg = input(f"Enter your message :  ")

            try:
                if msg.lower() == "/switch":
                    self.choose_room()
                    continue
                    #removing from rooms_to_clients, event send something
                self.client.send(msg.encode('utf-8'))

            except Exception as e:
                raise f"Error sending message: {repr(e)}"



def main():
    _ = ChatClient(host='127.0.0.1', listen_port=8)

if __name__ == '__main__':
    main()



    # if msg is file:
    #     #put in q cause I can get files from many clients asyncronic and activate send file thread
    # def send_file(self):
    #     #handle unexist file , chunkify
#todo users can joining, and leave a gruop  room_to_active_clients.remove(client)
#todo room switching first global then room1 (spesifc command /room or maybe go to strat and pick)
#todo validate path, username and message
#todo File Transfer - needs to occurs parallel so maybe thread of transfer and other of the chat management