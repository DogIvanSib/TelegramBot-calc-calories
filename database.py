import sqlite3


class Database:
    def __init__(self, db_path="database.db"):
        self.db_path = db_path

    def get_connection(self):
        """Получение соединения с базой данных"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Для доступа к колонкам по имени
        return conn

    def add_user(self, user_id, age, weight, height, gender, calories):
        """Добавление или обновление пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT OR REPLACE INTO users 
                (user_id, age, weight, height, gender, calories)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (user_id, age, weight, height, gender, calories),
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении пользователя: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def add_product(self, user_id, date, product_name, calories):
        """Добавление продукта для пользователя на определенную дату"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO products 
                (user_id, date, product_name, calories)
                VALUES (?, ?, ?, ?)
            """,
                (user_id, date, product_name, calories),
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении продукта: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def get_user_products_by_date(self, user_id, date):
        """Получение всех продуктов пользователя за определенную дату"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT product_name, calories 
                FROM products 
                WHERE user_id = ? AND date = ?
            """,
                (user_id, date),
            )
            return cursor.fetchall()
        finally:
            conn.close()

    def get_total_calories_by_date(self, user_id, date):
        """Получение суммы calories по user_id и date"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT SUM(calories) as total_calories
                FROM products 
                WHERE user_id = ? AND date = ?
                """,
                (user_id, date),
            )
            result = cursor.fetchone()
            return (
                int(result["total_calories"])
                if result["total_calories"] is not None
                else 0
            )
        finally:
            conn.close()

    def get_user_info(self, user_id):
        """Получение информации о пользователе"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT age, weight, height, gender, calories FROM users WHERE user_id = ?",
                (user_id,),
            )
            return cursor.fetchone()
        finally:
            conn.close()
