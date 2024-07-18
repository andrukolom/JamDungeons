## Запуск тг бота
0. Установите зависимости `pip install -r requirements.txt`
1. Создайте супер пользователя `python3 manage.py createsuperuser`
2. Зарегистрируйтесь под аккаунтом telegram на сайте
3. Зайдите в панель админа -> пользователи -> выберите пользователя telegram -> статус персонала 
4. Создайте .env в папке telegram в таком формате:
    ```
    BOT_TOKEN="ваш токен"
    API_USERNAME="telegram"
    API_PASSWORD="пароль"
    ```
5. Запустите сайт `python3 manage.py runserver`
6. Запустите telegram/bot.py