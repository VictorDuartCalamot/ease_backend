#Create virtual enviroment
python -m venv venv

#Get in venv
.\venv\Scripts\activate

#Install required packages (inside venv)
pip install django dj-database-url djangorestframework-simplejwt psycopg2-binary whitenoise[brotli] gunicorn django-guardian

#Copy packages to requirements.txt
pip freeze > requirements.txt


#Api root url
https://easeapi.onrender.com/

Archivos creados/modificados:

#djangocrud
djangocrud/settings.py
djangocrud/urls.py

#backend
backend/utils.py
backend/serializers.py
backend/permissions.py
backend/models.py
backend/views/management_views.py
backend/views/user_views.py
backend/urls/admin_urls.py
backend/urls/management_urls.py
backend/urls/user_urls.py
