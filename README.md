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

## Render.com server hosting:
```
I used render.com mainly because its FREE to create several web services to deploy the API using github, you get a "custom" url and its pretty easy to setup.
```
## Database and redis on render.com
```

Since i used DRF for the api, i`ve seen that postgresql is one of the recommended databases to pair with render.com, it offers a free postgresql database, the only bad thing is that the database gets deleted after 3 months unless you pay for an upgraded instance.
The redis server is great, i used it to setup django channels and it works great so far.

Overall render.com is great to create projects and deploy. We have to keep in mind that im using the free version for development and testing. The specs of the servers are pretty low so in a real stage it would be necessary to upgrade or lookup for any other more affordable or that brings better cards to the table. 
```
# Database info
## Class Diagram
[Class Diagrama lucid chart link](https://lucid.app/lucidchart/312df9b3-ee00-47b2-adf6-d349ac8c9b9b/edit?viewport_loc=-152%2C33%2C2674%2C1336%2C0_0&invitationId=inv_171d3cc6-46ce-40d5-b74a-ef61c904353a)

![image](https://github.com/VictorDuartCalamot/ease_backend/assets/115024032/ce7c5341-b446-48f3-894c-2cd0363eab81)


## ER Diagram
[ER Diagram lucid chart link](https://lucid.app/lucidchart/c99734df-2ad2-4e88-abec-458289e6d9c6/edit?viewport_loc=-45%2C3%2C2164%2C1081%2C0_0&invitationId=inv_457726de-bf5b-4beb-9ab1-a806997d89c8)

![image](https://github.com/VictorDuartCalamot/ease_backend/assets/115024032/9fa76905-809d-43de-83c6-3eab6013566e)


# Api information
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
  *POST
    Required fields:
      - username
      - password
users/register/
  *POST
    Required fields:
      -first_name
      -last_name
      -email
      -password

users/logout/
  *GET
    Required header:
      -Authorization: Token <token>
      -Content-Type: application/json

users/changepwd/
  *PUT
    Required fields:
      -current_password
      -new_password
    Required header:
      -Authorization: Token <token>
      -Content-Type: application/json
users/loginLog/
  *GET
    Optional Params:
      -start_date
      -end_date
      -start_time
      -end_time
    Required Header:
      -Authorization: Token <token>
      -Content-Type: application/json
  *POST
      #Cant't be used directly, its used automatically on login  
  Required Header:
    -Authorization: Token <token>
    -Content-Type: application/json  

users/loginLog/<uuid:pk>/
  *GET
    Required data in the url:
      -<UUID>
    Required Header:
    -Authorization: Token <token>
    -Content-Type: application/json
  *PUT
    Required data in the url:
      -<UUID>
    Required Fields:
      -creation_date
      -creation_time
      -platform_OS
      -successful
      -description
    Required Header:
      -Authorization: Token <token>
      -Content-Type: application/json
  *DELETE
    Required data in the url:
      -<UUID>
    Required Header:
      -Authorization: Token <token>
      -Content-Type: application/json    

 _____________
| Management: |
 -------------
management/expense/
  *GET
    Optional Params
      -start_date
      -end_date
      -start_time
      -end_time
    Required Header:
      -Authorization: Token <token>
      -Content-Type: application/json
  *POST
    Required Fields:
      -title
      -description
      -amount
      -creation_date
      -creation_time
      -category
      -subcategory
    Required Header:
      -Authorization: Token <token>
      -Content-Type: application/json
  
management/expense/<uuid:pk>/
  *GET
    Required data in the url:
      -<UUID>
    Required Header:
      -Authorization: Token <token>
      -Content-Type: application/json
  *PUT
    Required data in the url:
      -<UUID>
    Optional Fields:
      -title
      -description
      -amount
      -creation_date
      -creation_time
      -category
      -subcategory
    Required Header:
      -Authorization: Token <token>
      -Content-Type: application/json
  *DELETE
    Required data in the url:
      -<UUID>
    Required Header:
      -Authorization: Token <token>
      -Content-Type: application/json
      
management/income/
  *GET
    Optional Params
      -start_date
      -end_date
      -start_time
      -end_time
    Required Header:
      -Authorization: Token <token>
      -Content-Type: application/json
  *POST
    Required Fields:
      -title
      -description
      -amount
      -creation_date
      -creation_time
      -category
      -subcategory
    Required Header:
      -Authorization: Token <token>
      -Content-Type: application/json

management/income/<uuid:pk>/
  *GET
    Required data in the url:
      -<UUID>
    Required Header:
      -Authorization: Token <token>
      -Content-Type: application/json
  *PUT
    Required data in the url:
      -<UUID>
    Optional Fields:
      -title
      -description
      -amount
      -creation_date
      -creation_time
      -category
      -subcategory
    Required Header:
      -Authorization: Token <token>
      -Content-Type: application/json
   *DELETE
      Required data in the url:
        -<UUID>
      Required Header:
        -Authorization: Token <token>
        -Content-Type: application/json

management/category/
  *GET    
    Required Header:
      -Authorization: Token <token>
      -Content-Type: application/json
  *POST
    Required Fields:
      -name
      -description
      -type
      -hexColor
    Required Header:
      -Authorization: Token <token>
      -Content-Type: application/json

management/category/<uuid:pk>/
  *GET
    Required data in the url:
      -<UUID>
    Required Header:
      -Authorization: Token <token>
      -Content-Type: application/json
  *PUT
    Required data in the url:
      -<UUID>
    Optional Fields:
      -name
      -description
      -type
      -hexColor
    Required Header:
      -Authorization: Token <token>
      -Content-Type: application/json
  *Delete
    Required data in the url:
      -<UUID>
    Required Header:
      -Authorization: Token <token>
      -Content-Type: application/json

management/subcategory/
  *GET    
    Required Header:
      -Authorization: Token <token>
      -Content-Type: application/json
  *POST
    Required Fields:
      -name
      -description
      -type
      -hexColor
      -category
    Required Header:
      -Authorization: Token <token>
      -Content-Type: application/json

management/subcategory/<uuid:pk>/
  *GET
    Required data in the url:
      -<UUID>
    Required Header:
      -Authorization: Token <token>
      -Content-Type: application/json
  *PUT
    Required data in the url:
      -<UUID>
    Optional Fields:
      -name
      -description
      -type
      -hexColor
      -category
    Required Header:
      -Authorization: Token <token>
      -Content-Type: application/json
  *Delete
    Required data in the url:
      -<UUID>
    Required Header:
      -Authorization: Token <token>
      -Content-Type: application/json
 ________
| Chats: |
 --------
chats/get-or-create/
  *POST
    Required Header
      -Authorization: Token <token>
      -Content-Type: application/json

chats/<int:pk>/close/
  *POST
    Required data in the url:
      -<INT>
    Required Header
      -Authorization: Token <token>
      -Content-Type: application/json

chats/chat/
  *GET
    Required Header
      -Authorization: Token <token>
      -Content-Type: application/json

 ___________________
| Admin/SuperAdmin: |
 -------------------
superadmin/user/
  *GET
    Optional Params:
      -start_date
      -end_date
      -is_active
      -is_staff
      -is_superuser
    Required Header
      -Authorization: Token <token>
      -Content-Type: application/json
  *POST
    Required Fields
      -email
      -first_name
      -last_name
      -password
    Optional Fields
      -is_staff
      -is_superuser
      -is_active
    Required Header
      -Authorization: Token <token>
      -Content-Type: application/json
  
superadmin/user/<int:pk>/
  *GET
    Required data in the url:
      -<INT>    
    Required Header
      -Authorization: Token <token>
      -Content-Type: application/json
  *PUT
    Required data in the url:
      -<INT> 
    Optional Fields:
      -first_name
      -last_name
      -email
      -is_staff
      -is_superuser
      -is_active
    Required Header
      -Authorization: Token <token>
      -Content-Type: application/json
  *DELETE
    Required data in the url:
      -<INT>
    Required Header
      -Authorization: Token <token>
      -Content-Type: application/json 
    
superadmin/user/block/<int:pk>/
  *PUT
    Required data in the url:
      -<INT>       
    Optional Field:
      -is_active
    Required Header
      -Authorization: Token <token>
      -Content-Type: application/json
```
## WebSocket Endpoint:
```
wss://BASEURL/ws/support/chat/<chatid>/?token=<user token>
```
