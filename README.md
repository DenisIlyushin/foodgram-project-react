# foodgram

Проект помогает хранить и обмениваться рецептами, а также формировать список 
покупок для них.

#### Учебный проект Я.Практикума.
##### Когорта Python.7+

---

![example workflow](https://github.com/DenisIlyushin/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

---

## [Тестовый сервер](http://denisilyushin.ddns.net)

**логин** review@mail.fake \
**пароль** letsreviewthis

---

## Технологии
- Python `v3.7`
- Django `v2.2.19`
- DRF (Django REST framework) `v3.13.1`
- Djoser `v.2.0.5`
- Gunicorn `v.20.0.4`
- Docker `v.20.10.14`
- nginx `v.1.21.3`
- PostgreSQL `v.13.0`

## Описание проекта

Cайт Foodgram, «Продуктовый помощник» - онлайн-сервис и API для него. 
На этом сервисе пользователи смогут публиковать рецепты, подписываться 
на публикации других пользователей, добавлять понравившиеся рецепты 
в список «Избранное», а перед походом в магазин скачивать сводный список 
продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Установка и запуск backend-проекта на локальном компьютере

1. Клонируйте директорий и перейдите в корневую папку проекта:
```bash
git clone https://github.com/DenisIlyushin/foodgram-project-react.git
cd foodgram-project-react
```
2. Создайте и активируйте виртуальное окружение:
- Для Win10:
```bash
python -m venv env
source ./venv/bin/activate
```
- Для Ubuntu
```bash
python -m venv env
source venv/bin/activate
```
3. Обновите pip и установите зависимости в виртуальное окружение:
```bash
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
```

4. Выполните миграции:
```bash
python manage.py migrate
```

5. (опционально) Наполните базу данных стартовыми данными:
```bash
python manage.py imprint_initial_data
```

6. (опционально) Создайте суперпользователя Django:
```bash
python manage.py createsuperuser
```

7. Застите проект:
```bash
python manage.py runserver
```

## Модель пользователей проекта
- **Аноним** — может просматривать и фильтровать по ярлыкам все рецепты 
и рецепты отдельных пользователей.
- **Аутентифицированный пользователь (`user`)** — может читать всё, как и Аноним, 
может публиковать новые рецепты, редактировать свои рецепты, подписываться
на обновления рецептов других пользователей, добавлять рецепты в избранное и 
формировать список покупок.
- **Администратор (`admin`)** — полные права на управление всем контентом проекта. 
Может создавать и удалять рецепты, теги и ингредиенты, управлять пользователями.
Весь функционал доступен в стандартной админ-панели Django.
- **Суперпользователь Django** должен всегда обладать правами администратора, 
пользователя с правами admin. Даже если изменить пользовательскую роль 
суперпользователя — это не лишит его прав администратора. 
Суперпользователь — всегда администратор, но администратор — не обязательно 
суперпользователь.

## Ресурсы проекта
- Ресурс **auth**: аутентификация - получение и отзыв токена.
- Ресурс **users**: пользователи и подписки.
- Ресурс **tags**: ярлыки ('тэги'), создаются администраторами (или при наполнении проекта
стартовыми данными, см. п.5 выше).
- Ресурс **recepies**: рецепты, в том числе добавление в списки
избранных и списки покупок.
- Ресурс **ingredients**: ингридиенты.

Каждый ресурс описан в документации: указаны эндпоинты (адреса, по которым можно 
сделать запрос), разрешённые типы запросов, права доступа и дополнительные параметры, 
если это необходимо.

Для доступа к документации проекта запустите проект согласно инструкции ниже
и пройдите [по ссылке](http://localhost/api/docs/redoc.html).

## Запуск проекта в Docker
Для автоматизации запуска приложения установите на вашем компьютере или сервере Docker.

### Шаблон наполнения .env
Файл `.env` следует разместить в директории `./backend/`. 
Пример наполнения с комментариями приведет в файле `./backend/.env.example`

### Dockerfile для приложения Django
В файле конфигурации запуска многоконтейнерных приложений `./infra/docker-compose.yaml` 
все уже сделано за вас, однако при желании сделать самостоятельную сборку приложения 
**foodgram**, используя файл-конфигурации `./backend/Dockerfile`.
Находясь в директории `./backend/` для сборки контейнера используйте команду:
```bash
docker build -t foodgram .
```

### Последовательность запуска приложения
1. **Сборка контейнера**.
Находясь в папке `.\infra\` выполните следующую команду для сборки и запуска контейнера
```bash
docker-compose up -d --build
```
2. **Запуск приложения foodgram**.
После успешной сбоки контейнеров выполните следующие команды в терминале:
```bash
# Выполнить миграции
docker-compose exec backend python manage.py migrate
# Создаем суперппользователя
docker-compose exec backend python manage.py createsuperuser
# Собираем статику со всего проекта
docker-compose exec backend python manage.py collectstatic --no-input
# (опц.) Для резервного копирования данных из БД
docker-compose exec backend python manage.py dumpdata > dump.json
# (опц.) Для занесения в БД демонстрационных данных
docker-compose exec backend python manage.py imprint_initial_data
```
3. **Остановка и повторный запуск приложения foodgram**.
```bash
# Для остановки контейнеров
docker-compose down
# Для повторного запуска контейнеров
docker-compose up -d
```

## Запуск проекта на удаленном сервере

1. Скопируйте в корень домашней папки на удаленном сервере следующие файлы и директории
- `./docs/*`
- `./frontend/*`
- `./infra/docker-compose-deploy.yml`
- `./infra/nginx-deploy.config`
- `./infra/.env.example`

2. Создайте файл .env в корне домашней папки на удаленном сервере, заполните по образцу
из файла .env.example

3. В файле docker-compose-deploy.yml в строке 8 замените `/home/denisilyushin/` на путь 
до вашей домашней директории на удаленном сервере.

4. Переименуйте файлы на удаленном сервере:
- `~/docker-compose-deploy.yml` -> `~/docker-compose.yml`
- `~/nginx-deploy.config` -> `~/nginx.config`

5. Установите docker согласно руководству на официальном сайте

6. Запустите проект командой 
```bash
docker-compose up -d --build
```

#### Особенености сборки
- Файлы базы данных будут сохранены в `~/.dbdata`
- CI/CD не подразумевает частую замену файлов `.evn`, `nginx.config`, `docker-compose.yml`

## Github-actions
Для CI/CD c использованием Github Actions можно использовать предложенный 
в папке `/infra` конфигурационный файл `foodgram_workflow.yml`.

Workflow состоит из четырёх шагов:
1. Проведение матричного теста на соотвествие PEP для интерпретаторов 
Python 3.7, 3.8 и 3.9.
2. Сборка и публикация образа backend-сервера на вашем [DockerHub](https://hub.docker.com/).
3. Автоматический деплой на сервере Я.Облака.
4. Отправка уведомления вашим телеграм-ботом.

#### Настройка сервера для CI/CD
1. Выполнить действия из раздела _Запуск проекта на удаленном сервере_ (см. выше).
2. Подготовка ssh-ключа для Github Actions:
```bash
cd ~/.ssh
# генерируем ключ для Github Actions
# ssh-ключ предлагается назвать github-actions
# passphase не устанавливать
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```
![image](https://zellwk.com/images/2021/github-actions-deploy/name-ssh-key-file.png) \
![image](https://zellwk.com/images/2021/github-actions-deploy/passphrase-empty.png)
```bash
# добавляем публичный ключ в список разрешенных ключей
cat github-actions.pub >> authorized_keys
# (опц.) для удобства дальнейшей работы можно скопировать содержимое ключа в файл
cat github-actions >> ~/github-key.txt
```
3. Для работы с workflow добавьте переменные окружения Github Actions.
```bash
DOCKER_USERNAME = 'Логин от DockerHub'
DOCKER_PASSWORD = 'Пароль от DockerHub'

SSH_KEY = 'содержимое приватного ключа github-actions (см. п.2)'
HOST_SERVER = 'IP-адрес сервера на Я.Облаке'
HOST_USERNAME = 'Учетная запись администратора с правами суперпользователя'

DJANGO_ADMIN_USERNAME = 'Пседоним учетной записи суперпользователя Djano'
DJANGO_ADMIN_EMAIL = 'Адрес электронной почты учетной записи суперпользователя Djano'
DJANGO_ADMIN_PASSWORD = 'Пароль учетной записи суперпользователя Djano'

TELEGRAM_TO = 'id вашей учетной записи в telegram'
TELEGRAM_TOKEN = 'token вашего бота в telegram'
```

### Восстановление данных из резервной копии
```bash
docker-compose exec backend bash
python manage.py flush
python3 manage.py shell
```
```python
from django.contrib.contenttypes.models import ContentType
ContentType.objects.all().delete()
quit()
```
```bash
python manage.py loaddata dump.json
```

---

### Автор проекта
**Денис Илюшин** ([DenisIlyushin](https://github.com/DenisIlyushin/))