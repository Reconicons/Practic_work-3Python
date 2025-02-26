import getpass
import json
from hashlib import sha256
from datetime import datetime

class DataManager:
    @staticmethod
    def save_data(filename, data):
        with open(filename, "w") as f:
            json.dump(data, f)

    @staticmethod
    def load_data(filename):
        try:
            with open(filename, "r") as f:
                content = f.read()
                if not content:  
                    return []
                return json.loads(content)
        except FileNotFoundError:
            with open(filename, "w") as f:
                json.dump([], f)
            return []
        except json.JSONDecodeError:
            print(f"Ошибка в формате файла {filename}! Файл будет сброшен.")
            with open(filename, "w") as f:
                json.dump([], f)
            return []

class User:
    def __init__(self, username, password_hash, role, history=None, created_at=None):
        self._username = username
        self._password_hash = password_hash
        self._role = role
        self._history = history if history is not None else []
        self._created_at = created_at if created_at is not None else datetime.now().isoformat()

    @staticmethod
    def hash_password(password):
        return sha256(password.encode()).hexdigest()

    def verify_password(self, password):
        return self._password_hash == sha256(password.encode()).hexdigest()

    def update_password(self, new_password):
        self._password_hash = sha256(new_password.encode()).hexdigest()
        DataManager.save_data("users.json", UserManager.users_data())

    def add_to_history(self, product_name):
        self._history.append(product_name)
        DataManager.save_data("users.json", UserManager.users_data())

    def view_history(self):
        print("\n--- Ваша история покупок ---")
        for item in self._history:
            print(item)

class Admin(User):
    def menu(self):
        while True:
            print("\n--- Административное меню ---")
            print("1. Добавить товар")
            print("2. Удалить товар")
            print("3. Изменить товар")
            print("4. Просмотреть статистику")
            print("5. Выйти")

            choice = input("Выберите действие: ")

            if choice == '1':
                ProductManager.add_product()
            elif choice == '2':
                ProductManager.remove_product()
            elif choice == '3':
                ProductManager.edit_product()
            elif choice == '4':
                ProductManager.view_statistics()
            elif choice == '5':
                break
            else:
                print("Неверный выбор.")

class RegularUser(User):
    def menu(self):
        while True:
            print("\n--- Пользовательское меню ---")
            print("1. Просмотреть товары")
            print("2. Купить товар")
            print("3. История покупок")
            print("4. Обновить пароль")
            print("5. Выйти")

            choice = input("Выберите действие: ")

            if choice == '1':
                ProductManager.view_products()
            elif choice == '2':
                self.purchase_product()
            elif choice == '3':
                self.view_history()
            elif choice == '4':
                self.update_password_flow()
            elif choice == '5':
                break
            else:
                print("Неверный выбор.")

    def purchase_product(self):
        product_name = input("Введите название товара: ")
        product = ProductManager.get_product(product_name)
        if product and product.update_quantity(-1):
            self.add_to_history(product_name)
            print("Покупка совершена!")
        else:
            print("Товар недоступен.")

    def update_password_flow(self):
        new_password = getpass.getpass("Новый пароль: ")
        self.update_password(new_password)
        print("Пароль обновлен.")

class Product:
    def __init__(self, name, quantity, price):
        self._name = name
        self._quantity = quantity
        self._price = price

    def update_quantity(self, delta):
        if self._quantity + delta >= 0:
            self._quantity += delta
            ProductManager.save_products()
            return True
        return False

    def update_price(self, new_price):
        self._price = new_price
        ProductManager.save_products()

class ProductManager:
    products = []

    @classmethod
    def load_products(cls):
        cls.products = [
            Product(**p) for p in DataManager.load_data("products.json")
        ]
        
    @classmethod
    def save_products(cls):
        data = [{"name": p._name, "quantity": p._quantity, "price": p._price}
                for p in cls.products]
        DataManager.save_data("products.json", data)
    @classmethod
    def add_product(cls):
        name = input("Название товара: ")
        quantity = int(input("Количество: "))
        price = float(input("Цена: "))
        cls.products.append(Product(name, quantity, price))
        cls.save_products()

    @classmethod
    def remove_product(cls):
        name = input("Введите название товара для удаления: ")
        product = cls.get_product(name)
        if product:
            cls.products.remove(product)
            cls.save_products()
            print("Товар удален.")
        else:
            print("Товар не найден.")

    @classmethod
    def edit_product(cls):
        name = input("Введите название товара для изменения: ")
        product = cls.get_product(name)
        if product:
            new_name = input("Новое название (оставьте пустым, чтобы не изменять): ")
            new_quantity = input("Новое количество (оставьте пустым, чтобы не изменять): ")
            new_price = input("Новая цена (оставьте пустым, чтобы не изменять): ")

            if new_name:
                product._name = new_name
            if new_quantity:
                product._quantity = int(new_quantity)
            if new_price:
                product._price = float(new_price)

            cls.save_products()
            print("Товар изменен.")
        else:
            print("Товар не найден.")

    @classmethod
    def view_statistics(cls):
        print("\n--- Статистика ---")
        for p in cls.products:
            print(f"{p._name}: {p._quantity} шт. по {p._price} руб.")

    @classmethod
    def get_product(cls, name):
        for p in cls.products:
            if p._name.lower() == name.lower():
                return p
        return None

    @classmethod
    def view_products(cls):
        print("\n--- Товары ---")
        for p in cls.products:
            print(f"{p._name}: {p._quantity} шт. по {p._price} руб.")

class UserManager:
    users = []

    @classmethod
    def load_users(cls):
        cls.users = []
        for u in DataManager.load_data("users.json"):
            role_class = Admin if u['role'] == 'admin' else RegularUser
            cls.users.append(role_class(
                u['username'],
                u['password_hash'],
                u['role'],
                u['history'],
                u['created_at']
            ))

    @classmethod
    def users_data(cls):
        return [{
            "username": u._username,
            "password_hash": u._password_hash,
            "role": u._role,
            "history": u._history,
            "created_at": u._created_at
        } for u in cls.users]

def authorize():
    username = input("Логин: ")
    password = getpass.getpass("Пароль: ")
    for user in UserManager.users:
        if user._username == username and user.verify_password(password):
            return user
    print("Ошибка авторизации!")
    return None

def main():
    UserManager.load_users()
    ProductManager.load_products()

    print("Добро пожаловать!")
    user = authorize()
    if user:
        user.menu()
        DataManager.save_data("users.json", UserManager.users_data())
        DataManager.save_data("products.json", [
            {"name": p._name, "quantity": p._quantity, "price": p._price}
            for p in ProductManager.products
        ])

if __name__ == "__main__":
    main()