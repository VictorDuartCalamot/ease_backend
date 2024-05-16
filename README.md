### Setup API in your machine using windows.
```
#Create virtual enviroment
python -m venv venv

#Get in venv
.\venv\Scripts\activate

#Install required packages (inside venv)
pip install django dj-database-url djangorestframework-simplejwt psycopg2-binary whitenoise[brotli] gunicorn django-guardian channels channels_redis
pip install daphne "twisted[tls]" --no-deps 

#Copy packages to requirements.txt
pip freeze > requirements.txt
```

# Render.com server hosting:
```
I used render.com mainly because its FREE to create several web services to deploy the API using github, you get a "custom" url and its pretty easy to setup.
```
## Database and redis on render.com
```

Since i used DRF for the api, i`ve seen that postgresql is one of the recommended databases to pair with render.com, it offers a free postgresql database, the only bad thing is that the database gets deleted after 3 months unless you pay for an upgraded instance.
The redis server is great, i used it to setup django channels and it works great so far.

Overall render.com is great to create projects and deploy. We have to keep in mind that im using the free version for development and testing. The specs of the servers are pretty low so in a real stage it would be necessary to upgrade or lookup for any other more affordable or that brings better cards to the table. 
```
# Api root url
### Testing server:
  https://easeapi.onrender.com/
### Production server:
  https://ease-backend-xsi2.onrender.com/

### Enviromental variables:
```
ALLOWED_HOSTS
DATABASE_URL
DEBUG
OPENAI_KEY
PYTHON_VERSION
REDIS_URL
SECRET_KEY
```
### Possible actions using the API:
```
User:
  -Login
  -Register
  -Logout
  -Change own password
  -Fetch own expenses/income
  -Create expenses/income
  -Update own expenses/income
  -Delete own expenses/income
  -Create Technical support chat (send messages/get messages)
Admin (Same actions as user plus the following ones)
  -Fetch users
  -Create users with same or lower role permission level
  -Update users
  -Delete users
  -Fetch chats where they belong
  -Delete chats where they belong
SuperAdmin (Same actions as user plus admin plus the following ones)
  -Create users with any role permission leveL
  -Update users with any role permission level
  -Delete users with any role permission level  
```

### Created/Modified files:
```
____________________________________________

Djangocrud
--------------------------------------------
djangocrud/settings.py
djangocrud/urls.py
djangocrud/asgi.py

Backend
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
____________________________________________
```
## HTTP/HTTPS Endpoints:
```
BASEURL: 
  https://easeapi.onrender.com/api/
  https://ease-backend-xsi2.onrender.com/api/
 _______
| User: |
 -------
users/login/
users/register/
users/logout/
users/loginLog/
users/loginLog/<uuid:pk>/
users/changepwd/
 _____________
| Management: |
 -------------
management/expense/
management/expense/<uuid:pk>/

management/income/
management/income/<uuid:pk>/

management/category/
management/category/<uuid:pk>/

management/subcategory/
management/subcategory/<uuid:pk>/
 ________
| Chats: |
 --------
chats/chat/
chats/get-or-create/
chats/<int:pk>/close/
 ___________________
| Admin/SuperAdmin: |
 -------------------
superadmin/user/
superadmin/user/<int:pk>/
superadmin/user/block/<int:pk>/
```
## WebSocket Endpoint:
```
wss://BASEURL/ws/support/chat/<chatid>/?token=<user token>
```
