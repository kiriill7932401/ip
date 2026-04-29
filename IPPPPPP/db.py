from config import DB_FILE
import os

def read_db():
    data = {}
    if not os.path.exists(DB_FILE):
        return data
    with open(DB_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("|")
            if len(parts) == 5:
                user_id = int(parts[0])
                name = parts[1]
                lastname = parts[2]
                city = parts[3]
                balance = int(parts[4])
                data[user_id] = [name, lastname, city, balance]
    return data

def write_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        for user_id, (name, lastname, city, balance) in data.items():
            f.write(f"{user_id}|{name}|{lastname}|{city}|{balance}\n")

def get_user(user_id):
    data = read_db()
    if user_id in data:
        return data[user_id]
    return None

def create_user(user_id, name="", lastname="", city="Сургут", balance=0):
    data = read_db()
    if user_id not in data:
        data[user_id] = [name, lastname, city, balance]
        write_db(data)
    return data[user_id]

def update_user(user_id, name=None, lastname=None, city=None, balance=None):
    data = read_db()
    if user_id in data:
        if name is not None:
            data[user_id][0] = name
        if lastname is not None:
            data[user_id][1] = lastname
        if city is not None:
            data[user_id][2] = city
        if balance is not None:
            data[user_id][3] = balance
        write_db(data)