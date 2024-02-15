#Create virtual enviroment
python -m venv venv

#Get in venv
.\venv\Scripts\activate

#Install required packages (inside venv)
pip install django dj-database-url djangorestframework-simplejwt psycopg2-binary whitenoise[brotli] gunicorn

#Copy packages to requirements.txt
pip freeze > requirements.txt


#Api root url
https://easeapi.onrender.com/