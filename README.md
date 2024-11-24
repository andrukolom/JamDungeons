# О проекте

Этот сайт создан для увлекательного создания и прохождения текстовых квестов. Проект был разработан в рамках учебной работы в МШП и представляет собой интересное сочетание технологий и творчества.

На стороне сервера используется фреймворк Django в связке с базой данных SQLite, что обеспечивает надежную и эффективную работу приложения. Дизайн был тщательно проработан с помощью инструментов Figma и Bootstrap, что позволяет создать интуитивно понятный и привлекательный интерфейс.

Кроме того, наш проект предлагает уникальную возможность прохождения квестов через Telegram, что делает его доступным и удобным для пользователей. Присоединяйтесь к нам и погружайтесь в мир захватывающих приключений.

## Установка из репозитория

### 1. Установка необходимых инструментов

Перед тем, как начать, убедитесь, что у вас установлены следующие инструменты:

- [Python](https://www.python.org/downloads/) (рекомендуемая версия 3.6 или выше)
- [pip](https://pip.pypa.io/en/stable/installation/) (менеджер пакетов для Python)
- [Git](https://git-scm.com/downloads) (для клонирования репозитория)

### 2. Клонирование репозитория

Откройте терминал и выполните следующую команду, чтобы клонировать репозиторий:

```bash
git clone https://github.com/andrukolom/JamDungeons.git
```

Перейдите в директорию проекта:

```bash
cd JamDungeons
```

### 3. Создание виртуального окружения

Рекомендуется использовать виртуальное окружение для изоляции зависимостей проекта. Создайте виртуальное окружение с помощью следующей команды:

```bash
python -m venv venv
```

Активируйте виртуальное окружение:

- Для Windows:

```bash
venv\Scripts\activate
```

- Для macOS/Linux:

```bash
source venv/bin/activate
```

### 4. Установка зависимостей

Установите необходимые зависимости, указанные в файле `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 5. Настройка базы данных

В проекте может использоваться база данных. Выполните миграции, чтобы создать необходимые таблицы:

```bash
python manage.py migrate
```

### 6. Запуск сервера

Теперь вы можете запустить сервер разработки Django:

```bash
python manage.py runserver
```

### 7. Доступ к сайту

После запуска сервера откройте веб-браузер и перейдите по следующему адресу:

```
http://127.0.0.1:8000/
```


# Установка сайта из Docker Image
### 1. Установка Docker

Если у вас еще не установлен Docker, вы можете установить его, следуя инструкциям на официальном сайте [Docker](https://docs.docker.com/get-docker/).

### 2. Загрузка Docker Image

Откройте терминал и выполните следующую команду, чтобы загрузить нужный Docker image:

```bash
docker pull abbadob/jamdungeons:v1.0
```

### 3. Запуск контейнера

После загрузки образа, запустите контейнер с помощью следующей команды:

```bash
docker run -d -p 8080:80 --name jamdungeons abbadob/jamdungeons:v1.0
```

- `-d` — запустит контейнер в фоновом режиме.
- `-p 8080:80` — пробросит порт 80 контейнера на порт 8080 вашей машины.
- `--name jamdungeons` — задает имя контейнера для удобства.

### 4. Доступ к сайту

Теперь вы можете получить доступ к сайту, открыв веб-браузер и перейдя по следующему адресу:

```
http://localhost:8080
```

### 5. Остановка и удаление контейнера

Если вам нужно остановить контейнер, выполните команду:

```bash
docker stop jamdungeons
```

Чтобы удалить контейнер, выполните команду:

```bash
docker rm jamdungeons
```

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

# Запуск бота из Doker
### 1. Создание суперпользователя
```
Создайте суперпользователя для доступа к административной панели:

```bash
docker-compose exec web python3 manage.py createsuperuser
```

### 2. Регистрация в Telegram

Зарегистрируйтесь под аккаунтом Telegram на [официальном сайте](https://my.telegram.org/).

### 3. Настройка пользователя в панели администратора

1. Зайдите в панель админа -> пользователи -> выберите пользователя telegram -> статус персонала

### 4. Создание .env файла

Создайте файл `.env` в папке `telegram` с необходимыми переменными окружения:

```bash
# Создайте файл .env
touch telegram/.env
```

Заполните файл `.env` следующим образом:

```
BOT_TOKEN="ваш токен"
API_USERNAME="telegram"
API_PASSWORD="пароль"
```

### 5. Перезапуск контейнера

После добавления файла `.env`, перезапустите контейнер для применения изменений:

```bash
docker-compose down
docker-compose up -d
```
