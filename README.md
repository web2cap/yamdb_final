# DRF application in Docker with CI / CD deploy

## Project demo page
https://yambd.w2c.net.eu.org/api/v1/

### Project details:

The **YaMDb** project is designed to collect feedback on products.
Products can be: *"Books"*, *"Movies"*, *"Music"*.

### Project composition:

The project includes:

1. A system for storing and processing information on products, reviews and users.
2. A system for remote access to information, implemented using the REST architecture.

### Project features:

1. The project allows you to store information:
    * about users
    * about products
    * about product reviews and their comments
2. The project allows you to specify additional information about products:
    * genre (fantasy, thriller, etc.)
    * category (movie, book, music, etc.)
3. The project allows you to work with users:
    * register user
    * get information about your user
    * receive authentication parameters for working via the API protocol
4. The project allows you to specify the user's access role:
    * user
    * moderator
    * administrator
5. The project allows you to add reviews to products:
    * the review is given a score (from 1 to 10)
    * products have an automatically calculated rating on
based on ratings in reviews

### Project API features:

1. Users
    * adding a user
    * get authentication parameters
    * user management (delete, change, view)
2. Categories
    * adding categories
    * category management (delete, view)
3. Genres
    * adding genres
    * genre management (delete, view)
4. Products
    * addition product
    * product management (delete, change, view)
5. Product reviews
    * adding reviews
    * reviews management (delete, change, view)
6. Comments on reviews
    * adding comments
    * comment management (delete, change, view)




The application is packaged in 3 containers:
 - DB: PostgreSQL Database
 - Web: Django RF application, Gunicorn
 - Nginx: Web server and static files

Includes two volumes:
 - Static
 - Media


## CI and CD

Include 4 steps: 
 - Tests: Flake 8 check and pytest tests from tests/
 - Build: build and push to docker hub
 - Deploy: deploy on server with docker and docker compose
 - Inform: Send massage to Telegram

![example workflow](https://github.com/web2cap/yamdb_final/actions/workflows/master_yamdb_workflow.yml/badge.svg)


### Files structure
```
yamdb_final
├── README.md
├── api_yamdb
│   ├── Dockerfile
│   ├── api
│   │   ├── apps.py
│   │   ├── filters.py
│   │   ├── messages.py
│   │   ├── migrations
│   │   ├── mixins.py
│   │   ├── permissions.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── api_yamdb
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── fixtures
│   │   └── fixtures.json
│   ├── forstatic
│   │   └── redoc.yaml
│   ├── manage.py
│   ├── requirements.txt
│   ├── reviews
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations
│   │   ├── models.py
│   │   └── validators.py
│   ├── sent_emails
│   ├── static
│   │   └── redoc.yaml
│   ├── templates
│   │   └── redoc.html
│   └── users
│       ├── admin.py
│       ├── apps.py
│       ├── migrations
│       └── models.py
├── infra
│   ├── docker-compose.yaml
│   └── nginx
│       └── default.conf
├── pytest.ini
├── run.sh
├── setup.cfg
├── tests
│   ├── common.py
│   ├── conftest.py
│   ├── fixtures
│   │   └── fixture_user.py
│   ├── test_00_user_registration.py
│   ├── test_01_users.py
│   ├── test_02_category.py
│   ├── test_03_genre.py
│   ├── test_04_title.py
│   ├── test_05_review.py
│   ├── test_06_comment.py
│   ├── test_07_files.py
│   ├── test_10_readme.py
│   ├── test_11_docker_compose.py
│   ├── test_12_requirements.py
│   ├── test_13_settings.py
│   └── test_14_yamdb_yml.py

```

### Dependencies

```
requests==2.26.0
django==2.2.16
djangorestframework==3.12.4
djangorestframework-simplejwt==5.1.0
PyJWT==2.1.0
pytest==6.2.4
pytest-django==4.4.0
pytest-pythonpath==0.7.3
django-filter==21.1
gunicorn==20.0.4
psycopg2-binary==2.9.2
```

## Launch the project:

#### Set-up server:

## Prepare github repo

Fork this repository
Add a repository secrets:

HOST # Server hostname or IP for deploy
USER # Server Username
SSH_KEY # The public key that is present on the server


DB_ENGINE = django.db.backends.postgresql_psycopg2
DB_HOST = db # DB contaiter name
DB_NAME # Database name
DB_PORT = 5432
DB_USER # Database username
DB_PASSWORD # Database user password
ST_SECRET_KEY # Django secret key 

DOCKER_PASSWORD # Password for dockerhub
DOCKER_USERNAME # Username for dockerhub

TELEGRAM_TO # Your telegram ID. Help: @username_to_id_bot
TELEGRAM_TOKEN # Your telegram bot token. Help: @BotFather

When you make `git push` workflow started


You can create Django super-user:

```
sudo docker compose exec web python manage.py createsuperuser
```


### API description

A description of the project methods API is available at: https://yambd.w2c.net.eu.org/redoc/
* Documentation in Russian from the API customer

### Author:

The development team of the 32 Yandex.Practicum categories:
* Pavel Koshelev (Teamlead)
* Kirillov Evgeny
* Sudoplatova Marina


### About the development process:

The project was developed in a team, using the agile methodology. We used Trello as a task tracker. I was a team leader, responsible for the development process, team morale, developed the authorization section and the Users application. All project developers conducted code reviews.
