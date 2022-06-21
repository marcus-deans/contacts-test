from typing import List, Optional

import databases
import sqlalchemy
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Json
from sqlalchemy.dialects.postgresql import JSONB
import os
import urllib

DATABASE_URL = "sqlite:///./test.db"

# host_server = os.environ.get('host_server', 'localhost')
# db_server_port = urllib.parse.quote_plus(str(os.environ.get('db_server_port', '5432')))
# database_name = os.environ.get('database_name', 'fastapi')
# db_username = urllib.parse.quote_plus(str(os.environ.get('db_username', 'postgres')))
# db_password = urllib.parse.quote_plus(str(os.environ.get('db_password', 'secret')))
# ssl_mode = urllib.parse.quote_plus(str(os.environ.get('ssl_mode','prefer')))
# DATABASE_URL = 'postgresql://{}:{}@{}:{}/{}?sslmode={}'.format(db_username, db_password, host_server, db_server_port, database_name, ssl_mode)

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("first_name", sqlalchemy.String),
    sqlalchemy.Column("last_name", sqlalchemy.String),
    sqlalchemy.Column("phone_number", sqlalchemy.Integer, unique=True),
    sqlalchemy.Column("email_address", sqlalchemy.String),
    sqlalchemy.Column("linkedin_url", sqlalchemy.String),
    sqlalchemy.Column("instagram_url", sqlalchemy.String),
    sqlalchemy.Column("industry_parameters", sqlalchemy.dialects.postgresql.JSON),
    sqlalchemy.Column("personal_parameters", sqlalchemy.dialects.postgresql.JSON),
    sqlalchemy.Column("industry_years",sqlalchemy.Integer),
)

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
metadata.create_all(engine)

# PostgreSQL version
# engine = sqlalchemy.create_engine(
#     DATABASE_URL, pool_size=3, max_overflow=0
# )
# metadata.create_all(engine)

# Industry parameters used in both creation, updates, etc.
class IndustryParameters(BaseModel):
    experience_years: Optional[int]
    company_title: Optional[str]
    company_position: Optional[str]
    industry: Optional[str]
    backend: Optional[bool]
    frontend: Optional[bool]
    cloud: Optional[bool]

# Personal parameter used in creation, updates, etc.
class PersonalParameters(BaseModel):
    soccer: Optional[bool]
    basketball: Optional[bool]
    tennis: Optional[bool]
    musician: Optional[bool]
    music_listener: Optional[bool]
    foodie: Optional[bool]
    fashion: Optional[bool]
    gamer: Optional[bool]
    pets: Optional[bool]

#Model of JSON payload for Create and Update user endpoints
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    phone_number: int
    email_address: str
    linkedin_url: Optional[str] = ''
    instagram_url: Optional[str] = ''
    industry_parameters: IndustryParameters | None = None
    personal_parameters: PersonalParameters | None = None
    industry_years: Optional[int] = -1

#Model of JSON response for Retrieve users collection, or Retrieve single user
class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    phone_number: int
    email_address: str

#Model of JSON response for Update users collection
class UserUpdate(BaseModel):
    id: int
    first_name: Optional[str] 
    last_name: Optional[str]
    phone_number: Optional[int]
    email_address: Optional[str]
    linkedin_url: Optional[str]
    instagram_url: Optional[str]
    industry_parameters: Optional[Json]
    industry_years: Optional[int]

#Model of JSON response for Retrieve personal information of contact
class UserPersonal(User):
    instagram_url: str
    personal_parameters: PersonalParameters

#Model of JSON response for Retrieve professional information of contact
class UserProfessional(User):
    linkedin_url: str
    industry_years: int
    industry_parameters: IndustryParameters


app = FastAPI(title="REST API using FastAPI PostgreSQL Async EndPoints")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
#Specify origins more precisely by substituting with
# allow_origins=['client-facing-example-app.com', 'localhost:5000']

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.post("/users/", response_model=User, status_code = status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    print("is this wokinrg?")
    print(user)
    query = users.insert().values(
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number,
        email_address=user.email_address,
        linkedin_url=user.linkedin_url,
        instagram_url=user.instagram_url,
        industry_parameters=sqlalchemy.JSON(user.industry_parameters),
        industry_years = user.industry_years,
    )
    last_record_id = await database.execute(query)
    return {**user.dict(), "id": last_record_id}

@app.put("/users/{user_id}/", response_model=User, status_code = status.HTTP_200_OK)
async def update_user(user_id: int, payload: UserUpdate):
    query = users.update().where(users.c.id == user_id).values(
        first_name=payload.first_name,
        last_name=payload.last_name,
        phone_number=payload.phone_number,
        email_address=payload.email_address,
        linkedin_url=payload.linkedin_url,
        instagram_url=payload.instagram_url,
        industry_parameters=payload.industry_parameters,
        industry_years = payload.industry_years,
    )
    await database.execute(query)
    return {**payload.dict(), "id": user_id}

@app.get("/users/{contact_phone_number}/personal", response_model=UserPersonal, status_code = status.HTTP_200_OK)
async def read_personal_user(contact_phone_number:int):
    query = users.select().where(users.c.phone_number == contact_phone_number)
    return await database.fetch_one(query)

@app.get("/users/{contact_phone_number}/professional", response_model=UserProfessional, status_code = status.HTTP_200_OK)
async def read_professional_user(contact_phone_number:int):
    query = users.select().where(users.c.phone_number == contact_phone_number)
    return await database.fetch_one(query)

@app.get("/users/", response_model=List[User], status_code = status.HTTP_200_OK)
async def read_users(skip: int = 0, take: int = 20):
    query = users.select().offset(skip).limit(take)
    return await database.fetch_all(query)

@app.get("/users/{user_id}/", response_model=User, status_code = status.HTTP_200_OK)
async def read_users(user_id: int):
    query = users.select().where(users.c.id == user_id)
    return await database.fetch_one(query)

@app.delete("/users/{user_id}/", status_code = status.HTTP_200_OK)
async def remove_user(user_id: int):
    query = users.delete().where(users.c.id == user_id)
    await database.execute(query)
    return {"message": "User with id: {} deleted successfully!".format(user_id)}