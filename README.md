
# DRF application in Docker with CI / CD deploy

## Project demo page
http://web2cap.hopto.org/api/v1/

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

![example workflow](https://github.com/web2cap/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)


### Files structure
```
yamdb_final
├── .git/ 
├── .github/ 
│    └── workflows/
|          └── yamdb_workflow.yml <-- Workflow instruction
├── api_yamdb/
│    ├── api/
│    ├── api_yamdb/
│    │   ├── __init__.py
│    │   ├── settings.py
│    │   ├── urls.py
│    │   └── wsgi.py
│    ├── reviews/
│    ├── static 
│    │   └── redoc.yaml
│    ├── templates
│    │   └── redoc.html
│    ├── manage.py
|    └── requirements.txt 
├── infra/ <-- Deploy files
│    ├── nginx/ 
│    │   └── default.conf
│    ├── .env
|    └── docker-compose.yaml
├── tests/
├── .gitignore
├── Dockerfile 
├── pytest.ini
├── README.md
└── setup.cfg
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

I use on this project Ubuntu 20 with last updates
```
sudo apt-get update 
sudo apt install docker.io 
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

 echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

 sudo apt-get update
 sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

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
POSTGRES_USER # Database username
POSTGRES_PASSWORD # Database user password
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


### This DRF Project Page

https://github.com/web2cap/api_yamdb

### Autor:

* Koshelev Pavel


