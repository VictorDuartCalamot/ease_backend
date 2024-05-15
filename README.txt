#Create virtual enviroment
python -m venv venv

#Get in venv
.\venv\Scripts\activate

#Install required packages (inside venv)
pip install django dj-database-url djangorestframework-simplejwt psycopg2-binary whitenoise[brotli] gunicorn django-guardian channels channels_redis
pip install daphne "twisted[tls]" --no-deps 

#Copy packages to requirements.txt
pip freeze > requirements.txt


#Api root url
Testing server:
  https://easeapi.onrender.com/
Production server:
  https://ease-backend-xsi2.onrender.com/

Created/Modified files:

#Djangocrud
--------------------------------------------
djangocrud/settings.py
djangocrud/urls.py
djangocrud/asgi.py

#Backend
--------------------------------------------
backend/utils.py
backend/serializers.py
backend/permissions.py
backend/models.py
backend/websocket_auth.py
backend/routing.py
backend/consumers.py
backend/middleware.py
--------------------------------------------
backend/views/management_views.py
backend/views/user_views.py
backend/views/chat_views.py
--------------------------------------------
backend/urls/admin_urls.py
backend/urls/management_urls.py
backend/urls/user_urls.py
backend/urls/chat_urls.py
________________________________________________________

HTTP/HTTPS Endpoints:
BASEURL: 
  https://easeapi.onrender.com/api/
  https://ease-backend-xsi2.onrender.com/api/

User:
--------------------------------------------
users/login/
users/register/
users/logout/
users/loginLog/
users/loginLog/<uuid:pk>/
users/changepwd/

Management:
--------------------------------------------
management/expense/
management/expense/<uuid:pk>/
-
management/income/
management/income/<uuid:pk>/
-
management/category/
management/category/<uuid:pk>/
-
management/subcategory/
management/subcategory/<uuid:pk>/

Chats:
--------------------------------------------
chats/chat/
chats/get-or-create/
chats/<int:pk>/close/

Admin/SuperAdmin:
--------------------------------------------
superadmin/user/
superadmin/user/<int:pk>/
superadmin/user/block/<int:pk>/

WebSocket Endpoint:
wss://easeapi.onrender.com/ws/support/chat/<chatid>/?token=<user token>
