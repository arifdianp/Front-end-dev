# Django-docker notes for future reference
venv\Scripts\activate
pip install Django
django-admin startproject core .

#create requirements.txt files
pip freeze > requirements.context_processors

# docker-compose commands
docker-compose build
docker-compose run --rm app django-admin startproject core .
docker-compose up
docker exec -it django_container /bin/bash
