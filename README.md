### Setup API in your machine using windows.
```
#Create virtual enviroment
python -m venv venv

#Get in venv
.\venv\Scripts\activate

#Install required packages (inside venv)
pip install django dj-database-url djangorestframework-simplejwt psycopg2-binary whitenoise[brotli] gunicorn django-guardian channels channels_redis django-cors-headers requests django-redis
pip install daphne "twisted[tls]" --no-deps 

#Copy packages to requirements.txt
pip freeze > requirements.txt

#Exit venv
exit
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

![image](https://github.com/VictorDuartCalamot/ease_backend/assets/115024032/f07e787f-cb1f-4eb4-80b6-b4b54f28e6c1)



## ER Diagram
[ER Diagram lucid chart link](https://lucid.app/lucidchart/c99734df-2ad2-4e88-abec-458289e6d9c6/edit?viewport_loc=-45%2C3%2C2164%2C1081%2C0_0&invitationId=inv_457726de-bf5b-4beb-9ab1-a806997d89c8)

![image](https://github.com/VictorDuartCalamot/ease_backend/assets/115024032/0c518a78-f276-4c52-8dc4-b9864ead309a)
### Tables
#### Users
```
  //This table stores users

  Columns:
    id: int //Its the identifier of the user
    password: varcharr(128) //Password of the user
    username: varchar (150) // Its not a used field because gets overwritten by email 
    email: varchar(254) //Its the email of the user which acts as the unique field yet it isn't but in the logic of       the code its been updated to make it unique.
    first_name: varchar(150) // First name of the user
    last_name: varchar(150) // Last name of the user
    last_login: timestampz // Last successful login of the user
    date_joined: timestampz // Datetime creation of the useraccount
    is_active: bool //Its used to block the account from login disabling the account.
    is_staff: bool //Used to check if the user is an Admin
    is_superuser: bool //Used to check if the user is a super admin

  Table relations:
    User 1---N:1---N User Logs
    User 1---1:1---1 Chat
    User 1---N:1---N Chat messages
    User 1---N:1---N Income
    User 1---N:1---N Expense

  Constraints:
    id: PK
    Username: UNIQUE
```
#### User Logs
```
  //This table stores login logs of users

  Columns:
    id: uuid //Identifier of the log
    creation_date: date //Creation date of the log
    creation_time: time //Creation time of the log
    platform_OS: varchar(50) //Its ment to be fullfilled with the platform the user is trying to log-in (Example:         Web, Phone, Tablet, Desktop, Laptop)
    successful: bool // Shows if the login was successful or failed
    description: varchar(30) //Explains the reason of the failed login
    useri_id: int //Its the foreign key to the user

Table relations:
User logs N---N:1---1 User

Constraints:
  id: PK

Foreign keys:
  user_id -- User
```
#### Chat
```
  //This table stores chats

  Columns:
    id: uuid //Its the identificator of the chat session
    is_active: bool //Shows if the chat is currently active or not
    created_at: timestampz // Shows when the chat got created
    admin_id: int //Shows the admin thats responsible to answer in that chat
    customer_id: int //The customer that opened the chat

  Table Relations:
  Chat 1---1:1---1 User
  Chat 1---N:1---N Chat messages

  Constraints:
    id: PK

  Foreign keys:
    admin_id -- User
    customer_id -- User
```
#### Chat messages
```
  //This table stores messsages of the chat

  Columns:
    id: uuid //Identificator of the message
    message: varchar(250) //Message
    timestamp: timestampz //Creation of the message
    user_id: int //User that sent the message
    chat_session: uuid //Chat session where the message belongs to

Table relations:
  Chat messages N---N:1---1 Chat
  Chat messages N---N:1---1 User

Constraints
  id: PK

Foreign keys;
  user_id -- User
  chat_session -- Chat
```
#### Blacklisted Token
```
  //This table stores the tokens that got blacklisted 

  Columns:
    id: int //Identificator of the blacklisted token
    token: varchar(255) //Token of the user that got blacklisted
    created_at: timestampz //Creation of the blaclisted token

Constraints:
id: PK
```
#### Income
```
  //This table stores income records created by users

  Columns:
    id: uuid //Identificator of the income record
    title: varchar(100) //Title of the income
    description: varchar(100) //Description of the income
    amount: numeric(10,2) // Amount of the income
    category_id: uuid //Category of the income
    user_id: int //User that owns the income record
    creation_date: date //Creation date of the income
    creation_time: time //Cration time of the income 

Table relations:
  Income N---N:1---1 User
  Income N---N:1---1 Category  

Constraints:
  id: PK

Foreign keys:
  category_id -- Category
  user_id -- User
```
#### Expense
```
  //This table stores expense records created by users

  Columns:
    id: uuid //Identificator of the expense record
    title: varchar(100) //Title of the expense
    description: varchar(100) //Description of the expense
    amount: numeric(10,2) //Amount of the expense
    category_id: uuid //Category of the expense
    subcategory_id: uuid //Subcategory of the expense
    user_id: int //User that owns the expense record
    creation_date: date //Creation date of the expense
    creation_time: time //Creation time of the expense

Table relations:
  Expense N---N:1---1 User
  Expense N---N:1---1 Category
  Expense N---N:1---1 Subcategory

Constraints:
  id: PK

Foreign keys:
  category_id -- Category
  subcategory_id -- Subcategory
  user_id -- User
```
#### Category
```
  //This table stores the categories

  Columns:
    id: uuid //Identificator of the category
    name: varchar(100) //Name of the category
    description: varchar(100) //Description of the category
    type: varchar(100) //Type of the category (income/expense)
    hexColor: varchar(7) //HTML color of the category

Table relations:
  Category 1---N:1---N Income
  Category 1---N:1---N Expense
  Category 1---N:1---N Subcategory

Constraints:
  id: PK
```
#### Subcategory
```
  //This table stores the subcategories

  Columns:
    id: uuid //Identificator of the subcategory
    name: varchar(100) //Name of the subcategory
    description: varchar(100) //Name of the subcategory
    hexColor: varchar(7) //HTML color of the subcategory
    category_id: uuid //Main category

  Table relations;
    Subcategory 1--N:1--N Expense    
    Subcategory N--N:1--1 Category

  Constraints:
    id: PK

  Foreign keys:
    category_id -- Category
```

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
    Optional fields:
      - Type (income/expense)
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
wss://BASEURL/ws/support/chat/<chatuuid>/?token=<user token>
```
