import sqlite3


def initiate_db(title, description, price, photo):
    connection = sqlite3.connect('base_products.db')
    cursor = connection.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Products(
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    price INTEGER NOT NULL,
    photo TEXT
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users(
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    age INTEGER NOT NULL,
    balance TEXT NOT NULL
    );
    ''')

    cursor.execute("INSERT INTO Products(title, description, price, photo) VALUES(?, ?, ?, ?)",
                   (title, description, price, photo))

    connection.commit()
    connection.close()


def add_user(username, email, age):
    connection = sqlite3.connect('base_products.db')
    cursor = connection.cursor()
    cursor.execute("INSERT INTO Users(username, email, age, balance) VALUES(?, ?, ?, ?)",
                   (username, email, age, 1000))
    connection.commit()
    connection.close()


def is_included(username):
    connection = sqlite3.connect('base_products.db')
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM Users WHERE username=?", (username,))
    incl = cursor.fetchone()
    connection.commit()
    connection.close()
    return not (incl == None)


def get_all_products():
    connection = sqlite3.connect('base_products.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Products")
    all_products = cursor.fetchall()
    connection.commit()
    connection.close()
    return all_products


if __name__ == '__main__':
    initiate_db('Напиток арбузный', 'Объем 300 мл., калорийность 50 ккал. ', 100, '1.jpg')
    initiate_db('Напиток грушевый', 'Объем 300 мл., калорийность 60 ккал. ', 110, '2.jpg')
    initiate_db('Напиток земляничный', 'Объем 300 мл., калорийность 70 ккал. ', 120, '3.jpg')
    initiate_db('Напиток яблочный', 'Объем 300 мл., калорийность 80 ккал. ', 130, '4.jpg')
