import hashlib
import sqlite3
from googletrans import Translator

users_db = sqlite3.connect("users.db")
history_db = sqlite3.connect("history.db")
history_cursor = history_db.cursor()
cursor = users_db.cursor()


class User:
    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.hashed_password = hashlib.sha512(password.encode()).hexdigest()
        self.is_logged_in = False

    def register(self) -> None:
        cursor.execute(""" SELECT * FROM users WHERE username = ? """, (self.username,))
        if cursor.fetchone():
            print("Такой username уже занят")
            return

        cursor.execute(
            """INSERT INTO users (username, password) VALUES (?, ?)""",
            (self.username, self.hashed_password),
        )

        users_db.commit()
        print(f"Пользователь {self.username} зарегистрирован!")

    def login(self) -> None:
        cursor.execute(
            """ SELECT * FROM users WHERE username = ? AND password =?""",
            (self.username, self.hashed_password),
        )
        if cursor.fetchone():
            print("Успех")
            self.is_logged_in = True
        else:
            print("Ошибка в логине или пароле")

    def logout(self) -> None:
        if self.is_logged_in:
            self.is_logged_in = False
            print("Вы успешно вышли")
        else:
            print("Вы еще не вошли")


class Translate:
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        translator = Translator()
        translation = translator.translate(text=text, src=source_lang, dest=target_lang)
        return translation.text


class History:
    def add_entry(
        self, source_lang: str, target_lang: str, source_text: str, translated_text: str
    ):
        history_cursor.execute(
            """
            INSERT INTO history (source_lang, target_lang, source_text, translated_text)
            VALUES ( ?, ?, ?, ?)
            """,
            (source_lang, target_lang, source_text, translated_text),
        )
        history_db.commit()

    def get_history(self):
        history_cursor.execute(
            """
            SELECT * FROM history
            """
        )
        return history_cursor.fetchall()

    def view_history(self):
        items = self.get_history()
        for item in items:
            print(f"\n---\nИсточник: {item[1]}")
            print(f"Цель: {item[2]}")
            print(f"Текст: {item[3]}")
            print(f"Перевод: {item[4]}")


user = None
while True:
    print("\nМеню:")
    print("1. Регистрация")
    print("2. Вход")
    print("3. Выход")
    print("4. Перевод")
    print("5. История переводов")

    choice = input("Введите ваш выбор: ")

    if choice == "1":
        username = input("Введите username: ")
        password = input("Введите пароль: ")
        new_user = User(username, password)
        new_user.register()

    elif choice == "2":
        username = input("Введите username: ")
        password = input("Введите пароль: ")
        user = User(username, password)
        user.login()

    elif choice == "3":
        if user:
            user.logout()
            user = None
        else:
            print("Вы еще не вошли")
        break

    elif choice == "4":
        if user and user.is_logged_in:
            source_lang = input("Введите исходный язык (например, ru): ")
            target_lang = input("Введите целевой язык (например, en): ")
            source_text = input("Введите текст для перевода: ")
            translator = Translate()
            translated_text = translator.translate(
                source_text, source_lang, target_lang
            )
            print("Переведенный текст:", translated_text)
            history = History()
            history.add_entry(source_lang, target_lang, source_text, translated_text)
        else:
            print("Вы не авторизованы. Пожалуйста, войдите или зарегистрируйтесь.")
    elif choice == "5":
        if user:
            history = History()
            history.view_history()
        else:
            print("Вы не авторизованы. Пожалуйста, войдите или зарегистрируйтесь.")
            continue
    else:
        print("Неверный выбор. Пожалуйста, введите номер пункта меню из списка.")
