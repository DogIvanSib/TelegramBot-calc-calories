import sqlite3
from datetime import datetime, timedelta


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
            cursor.close()
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
            cursor.close()
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
            cursor.close()
            conn.close()

    def get_user_top_products_this_week(self, user_id) -> list[dict]:
        """Получить топ-5 самых часто повторяющихся блюд за неделю для конкретного пользователя"""

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Определяем начало недели
            today = datetime.now().date()
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)

            start_date_str = start_of_week.strftime("%d-%m-%Y")
            end_date_str = end_of_week.strftime("%d-%m-%Y")

            # Создаем список всех дат недели
            week_dates = []
            current_date = start_of_week
            while current_date <= end_of_week:
                week_dates.append(current_date.strftime("%d-%m-%Y"))
                current_date += timedelta(days=1)

            # SQL запрос для суммирования калорий по дням (используем IN)
            placeholders = ",".join(["?" for _ in week_dates])
            cursor.execute(
                f"""
                    SELECT product_name, COUNT(*) as frequency
                    FROM products 
                    WHERE user_id = ? AND date IN ({placeholders})
                    GROUP BY product_name
                    HAVING COUNT(*) > 1
                    ORDER BY frequency DESC
                    LIMIT 5
                    """,
                [user_id] + week_dates,
            )
            user_info = f" для пользователя {user_id}"

            top_products = cursor.fetchall()

            print(
                f"Топ {len(top_products)} самых частых блюд за неделю{user_info} ({start_date_str} - {end_date_str}):"
            )

            if top_products:
                for i, (product_name, frequency) in enumerate(
                    top_products, 1
                ):
                    print(f"{i}. {product_name} - {frequency} раз(а)")
            else:
                print("Нет часто повторяющихся блюд за эту неделю")
                top_products = []

            return top_products

        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def get_weekly_calories(self, user_id) -> list[dict]:
        """Получить количество килокалорий по дням в течение недели для пользователя"""

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Определяем начало и конец недели
            today = datetime.now().date()
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)

            # Форматируем даты для SQL запроса
            start_date_str = start_of_week.strftime("%d-%m-%Y")
            end_date_str = end_of_week.strftime("%d-%m-%Y")

            # Создаем список всех дат недели
            week_dates = []
            current_date = start_of_week
            while current_date <= end_of_week:
                week_dates.append(current_date.strftime("%d-%m-%Y"))
                current_date += timedelta(days=1)

            # SQL запрос для суммирования калорий по дням (используем IN)
            placeholders = ",".join(["?" for _ in week_dates])
            cursor.execute(
                f"""
                SELECT date, SUM(calories) as total_calories
                FROM products 
                WHERE user_id = ? AND date IN ({placeholders})
                GROUP BY date
                ORDER BY date
                """,
                [user_id] + week_dates,
            )

            daily_calories = cursor.fetchall()

            # Создаем полный список всех дней недели с калориями
            full_week = []
            current_date = start_of_week

            while current_date <= end_of_week:
                date_str = current_date.strftime("%d-%m-%Y")

                # Ищем калории для этой даты в результатах запроса
                calories = 0
                for date, cal in daily_calories:
                    if date == date_str:
                        calories = cal
                        break

                # Добавляем день недели для удобства чтения
                day_names = [
                    "Понедельник",
                    "Вторник",
                    "Среда",
                    "Четверг",
                    "Пятница",
                    "Суббота",
                    "Воскресенье",
                ]
                day_name = day_names[current_date.weekday()]

                full_week.append(
                    {"date": date_str, "day_name": day_name, "calories": calories}
                )

                current_date += timedelta(days=1)

            # Выводим результаты
            print(
                f"Потребление калорий пользователем {user_id} за неделю ({start_date_str} - {end_date_str}):"
            )
            print("-" * 50)

            total_weekly_calories = 0
            for day in full_week:
                print(f"{day['day_name']} ({day['date']}): {day['calories']:.0f} ккал")
                total_weekly_calories += day["calories"]

            print("-" * 50)
            print(f"Итого за неделю: {total_weekly_calories:.0f} ккал")
            print(f"В среднем в день: {total_weekly_calories/7:.0f} ккал")

            return full_week, total_weekly_calories

        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
