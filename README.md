# Проект "Перевод средств"

Это простое веб-приложение на Django, которое позволяет пользователям переводить средства между счетами.

## Особенности

- Аутентификация пользователей с использованием пользовательской модели CustomUser, содержащей ИНН и баланс.
- Форма для перевода средств между пользователями с проверкой корректности данных.
- Обработка перевода средств с использованием транзакций в базе данных для обеспечения консистентности данных.
- Управление пользователями через административную панель Django.

## Установка и настройка

### Требования

- Python 3.7 или выше
- Django 3.2 или выше

### Установка

1. Клонируйте репозиторий:

```
git clone https://github.com/harrior/MoneyDistrib-test-task.git
```

2. Перейдите в директорию проекта:

```
cd MoneyDistrib
```

3. Создайте и активируйте виртуальное окружение:

```
python3 -m venv venv
source venv/bin/activate
```

4. Установите зависимости:

```
pip install -r requirements.txt
```

5. Примените миграции:

```
python manage.py migrate
```

6. Создайте суперпользователя для доступа к административной панели:

```
python manage.py createsuperuser
```

### Запуск сервера

Запустите сервер с помощью следующей команды:

```
python manage.py runserver
```

Теперь вы можете открыть веб-приложение в браузере по адресу http://127.0.0.1:8000/.

Для доступа к административной панели перейдите по адресу http://127.0.0.1:8000/admin/ и войдите с использованием
учетных данных суперпользователя, созданных на этапе установки.

## Тестирование

Для запуска тестов выполните следующую команду:

``` 
python manage.py test
```

## Добавление пользователей

Пользователи могут быть добавлены через административную панель Django. Для этого перейдите по
адресу http://127.0.0.1:8000/admin/ и войдите с использованием учетных данных суперпользователя. Затем выберите "Users"
и нажмите "Add User" для добавления нового пользователя.

## Автор

Сизов Сергей ([@harrior](https://github.com/harrior/))
