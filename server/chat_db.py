import sqlite3
import typing

END_HISTORY_RETRIEVAL = "END_HISTORY_RETRIEVAL"

class ChatDB:

    @staticmethod
    def setup_database():
        db = sqlite3.connect('chat.db')
        cursor = db.cursor()

        cursor.execute('''
           CREATE TABLE IF NOT EXISTS users (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               username TEXT UNIQUE NOT NULL
               );
           ''')

        cursor.execute('''
           CREATE TABLE IF NOT EXISTS rooms (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               room_name TEXT UNIQUE NOT NULL
               );
           ''')

        cursor.execute('''
           CREATE TABLE IF NOT EXISTS messages (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               text_message TEXT NOT NULL,
               sender_id INTEGER NOT NULL,
               room_id INTEGER NOT NULL,
               timestamp DATETIME NOT NULL,
               FOREIGN KEY (sender_id) REFERENCES users(id), 
               FOREIGN KEY (room_id) REFERENCES rooms(id) 
               );
           ''')
        db.commit()
        db.close()

    @staticmethod
    def send_previous_messages_in_room(conn, room_name: str, join_timestamp: typing.Optional[str] = None):
        db = sqlite3.connect('chat.db')
        cursor = db.cursor()

        room_id = ChatDB.get_room_id_from_rooms(room_name, cursor)
        print(f"room name: {room_name}, room id {room_id}, joined timestamp {join_timestamp}")

        if join_timestamp:
            cursor.execute('''
              SELECT text_message, sender_id, timestamp FROM messages
               WHERE room_id = ? 
               AND timestamp > ? 
               ORDER BY timestamp ASC
               ''', (room_id, join_timestamp))

        else:
            cursor.execute('''
                 SELECT text_message, sender_id, timestamp FROM messages
                  WHERE room_id = ? 
                  ORDER BY timestamp ASC
                  ''', (room_id,))

        if old_messages := cursor.fetchall():
            for text_message, sender_id, timestamp in old_messages:
                old_msg_sender = ChatDB.get_user_name_from_users(sender_id, cursor)
                final_msg = f"[{timestamp}] [{old_msg_sender}]: {text_message} "
                conn.send(final_msg.encode('utf-8'))

            conn.send(END_HISTORY_RETRIEVAL.encode())

        else:
            print("No messages in this chat yet ...".encode('utf-8'))
            conn.send("No messages in this chat yet ...".encode('utf-8'))

        db.close()

    @staticmethod
    def store_user(username):
        db = sqlite3.connect('chat.db')
        cursor = db.cursor()

        cursor.execute('INSERT OR IGNORE INTO users (username) VALUES (?)', (username,))
        db.commit()
        db.close()

        # check if user is None conn.send() to user to write again

    @staticmethod
    def store_message(text_message, username, room_name, timestamp):  # not sent to db as well
        db = sqlite3.connect('chat.db')
        cursor = db.cursor()

        sender_id = ChatDB.get_user_id_from_users(username, cursor)
        room_id = ChatDB.get_room_id_from_rooms(room_name, cursor)

        cursor.execute('''
           INSERT INTO messages (text_message, sender_id, room_id, timestamp)
           VALUES (?,?,?,?)''', (text_message, sender_id, room_id, timestamp))
        db.commit()
        db.close()

    @staticmethod
    def get_user_id_from_users(username, cursor) -> int:  # check if i need to validate return value not None else raise ValueError don't exist
        cursor.execute('SELECT id FROM users where username = ?', (username,))
        return cursor.fetchone()[0]

    @staticmethod
    def get_user_name_from_users(user_id, cursor) -> int:  # check if i need to validate return value not None else raise ValueError don't exist
        cursor.execute('SELECT username FROM users where id = ?', (user_id,))
        return cursor.fetchone()[0]

    @staticmethod
    def get_room_id_from_rooms(room_name, cursor) -> int:
        cursor.execute('SELECT id FROM rooms WHERE room_name = ?', (room_name,))
        return cursor.fetchone()[0]

    @staticmethod
    def create_room(room_name):
        print("creation room")
        db = sqlite3.connect('chat.db')
        cursor = db.cursor()

        cursor.execute('INSERT OR IGNORE INTO rooms (room_name) VALUES (?)', (room_name,))
        db.commit()
        db.close()

