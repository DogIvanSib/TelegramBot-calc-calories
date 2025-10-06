
# Описание

+ Записывать потребленные калории
+ Подсчитывать калории за сутки
+ Давать рекомендацию по потреблению следующему дню

# Запуск

+ Установить Python3.12 и выше
+ Перейти в папку где будет развертываться проект
+ Создать venv окружение `python -m venv venv`
+ Установить зависимости  
`venv\Scripts\python.exe -m pip install -r requirements.txt`
+ Cкопировать secret_example.py. Переименовать его в secret.py. Заполнить своей приватной информацией.  
TOKEN поможет выдать @BotFather  
GIGA_AI_CREDENTIALS поможет https://developers.sber.ru/docs/ru/gigachat/individuals-quickstart   
+ запустить миграции, если еще не делали. Делается один раз для инициализации БД SQLLite  
`venv\Scripts\python.exe migrate.py`
+ Запустить  
`venv\Scripts\python.exe main.py`
