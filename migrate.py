import sqlite3


def create_tables():
    """Создание таблиц users и products в базе данных SQLite"""

    # Подключаемся к базе данных (файл создастся автоматически)
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    try:
        # Создание таблицы users
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                age INTEGER,
                weight REAL,
                height REAL,
                gender TEXT,
                calories INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Создание таблицы products
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                date TEXT,
                product_name TEXT,
                calories REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
            )
        """
        )

        # Создание индексов для улучшения производительности
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_products_user_date ON products(user_id, date)"
        )

        # Коммитим изменения
        conn.commit()
        print("Таблицы успешно созданы!")

    except Exception as e:
        print(f"Ошибка при создании таблиц: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    create_tables()
