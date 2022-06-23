import json
from typing import List, Optional, Dict, Any

import jsonpickle
import databases
import sqlalchemy
from asyncpg import Record
from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Json
from sqlalchemy import Integer
from sqlalchemy.dialects.postgresql import JSONB
import os
import urllib

# DATABASE_URL = "sqlite:///./test.db"

# host_server = os.environ.get('host_server', 'localhost')
# db_server_port = urllib.parse.quote_plus(str(os.environ.get('db_server_port', '5432')))
# database_name = os.environ.get('database_name', 'fastapi')
# db_username = urllib.parse.quote_plus(str(os.environ.get('db_username', 'postgres')))
# db_password = urllib.parse.quote_plus(str(os.environ.get('db_password', 'secret')))
# ssl_mode = urllib.parse.quote_plus(str(os.environ.get('ssl_mode','require')))
# DATABASE_URL = 'postgresql://{}:{}@{}:{}/{}?sslmode={}'.format(db_username, db_password, host_server, db_server_port, database_name, ssl_mode)
DATABASE_URL = "postgresql://bntliqohchcrzk:ee8f7b47350fa6d25f66d75be5c186636edd9a5fa0d4ee32d43aaff13b75ed59@ec2-52-22-136-117.compute-1.amazonaws.com:5432/d2e1q9sqmd67oj"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("first_name", sqlalchemy.String),
    sqlalchemy.Column("last_name", sqlalchemy.String),
    #PHONE NUMBER IS SUPPOSED TO BE A STRING!!
    sqlalchemy.Column("phone_number", sqlalchemy.String, unique=True),
    sqlalchemy.Column("email_address", sqlalchemy.String),
    #sqlalchemy.Column("linkedin_url", sqlalchemy.String),
    sqlalchemy.Column("instagram_handle", sqlalchemy.String),
    sqlalchemy.Column("professional_parameters", sqlalchemy.dialects.postgresql.JSON),
    sqlalchemy.Column("personal_parameters", sqlalchemy.dialects.postgresql.JSON),
    #sqlalchemy.Column("professional_years", sqlalchemy.Integer),
)

relationships = sqlalchemy.Table(
    "relationships",
    metadata,
    sqlalchemy.Column("relationship_id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("initiator_id", sqlalchemy.Integer),
    sqlalchemy.Column("receiver_id", sqlalchemy.Integer),
    #PHONE NUMBER IS SUPPOSED TO BE A STRING!!
    sqlalchemy.Column("isPersonal", sqlalchemy.Boolean)
)

groups = sqlalchemy.Table(
    "groups",
    metadata,
    sqlalchemy.Column("group_id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("member1", sqlalchemy.Integer),
    sqlalchemy.Column("member2", sqlalchemy.Integer),
    #PHONE NUMBER IS SUPPOSED TO BE A STRING!!
    sqlalchemy.Column("member3", sqlalchemy.Integer),
    sqlalchemy.Column("member4", sqlalchemy.Integer),
    sqlalchemy.Column("member5", sqlalchemy.Integer)
)


# groups = sqlalchemy.Table(
#     "groups",
#     metadata,
#     sqlalchemy.Column("group_id", sqlalchemy.Integer, primary_key=True),
#     #TODO: explore one to many mapping
#     sqlalchemy.Column("users_id", sqlalchemy.types.ARRAY(Integer)),
# )

# engine = sqlalchemy.create_engine(
#     DATABASE_URL, connect_args={"check_same_thread": False}
# )
# metadata.create_all(engine)


# PostgreSQL version
engine = sqlalchemy.create_engine(
    DATABASE_URL
)
metadata.create_all(engine)

# Professional parameters used in both creation, updates, etc.
class ProfessionalParameters(BaseModel):
    machine_learning: Optional[bool]
    has_mba: Optional[bool]
    has_cs: Optional[bool]
    has_engineering: Optional[bool]
    finance: Optional[bool]
    marketing: Optional[bool]
    consulting: Optional[bool]
    startup: Optional[bool]

# Personal parameter used in creation, updates, etc.
class PersonalParameters(BaseModel):
    soccer: Optional[bool]
    basketball: Optional[bool]
    tennis: Optional[bool]
    musician: Optional[bool]
    music_listener: Optional[bool]
    foodie: Optional[bool]
    #fashion: Optional[bool]
    gamer: Optional[bool]
    pets: Optional[bool]


# # Model of JSON payload for Create and Update user endpoints
# class UserCreate(BaseModel):
#     first_name: str
#     last_name: str
#     phone_number: int
#     email_address: str
#     linkedin_url: Optional[str] = ''
#     instagram_url: Optional[str] = ''
#     professional_parameters: ProfessionalParameters | None = None
#     personal_parameters: PersonalParameters | None = None
#     professional_years: Optional[int] = -1


# Model of JSON response for Retrieve users collection, or Retrieve single user
class User(BaseModel):
    id: int
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    email_address: Optional[str]
    location: Optional[str]
    instagram_handle: Optional[str]
    personal_parameters: PersonalParameters | None = None
    professional_parameters: ProfessionalParameters |  None = None


# # Model of JSON response for Update users collection
# class UserUpdate(BaseModel):
#     id: int
#     first_name: Optional[str]
#     last_name: Optional[str]
#     phone_number: Optional[int]
#     email_address: Optional[str]
#     linkedin_url: Optional[str]
#     instagram_url: Optional[str]
#     professional_parameters: Optional[Json]
#     professional_years: Optional[int]


# Model of JSON response for Retrieve personal information of contact
class UserPersonal(User):
    instagram_handle: str
    # personal_parameters: PersonalParameters | None


# Model of JSON response for Retrieve professional information of contact
class UserProfessional(User):
    linkedin_url: str
    #professional_years: int
    #professional_parameters: ProfessionalParameters | None

# class Group(BaseModel):
#     id: int
#     contact_ids: List[int]

class Group(BaseModel):
    group_id: Optional[str]
    member1: Optional[str]
    member2: Optional[str]
    member3: Optional[str]
    member4: Optional[str]
    member5: Optional[str]

class Relationship(BaseModel):
    relationship_id: Optional[str]
    initiator_id: Optional[str]
    receiver_id: Optional[str]
    isPersonal: Optional[bool]


app = FastAPI(title="Enhanced Contacts API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Specify origins more precisely by substituting with
# allow_origins=['client-facing-example-app.com', 'localhost:5000']

@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.post("/users/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: User):
    query = users.insert().values(
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number,
        email_address=user.email_address,
        #linkedin_url=user.linkedin_url,
        instagram_handle=user.instagram_handle,
        professional_parameters=jsonpickle.encode(user.professional_parameters),
        personal_parameters=jsonpickle.encode(user.personal_parameters),
        #professional_years=user.professional_years,
    )
    print(query)
    last_record_id = await database.execute(query)
    return {**user.dict(), "id": last_record_id}


@app.put("/users/{user_id}/", response_model=User, status_code=status.HTTP_200_OK)
async def update_user(user_id: int, payload: User):
    query = users.update().where(users.c.id == user_id).values(
        first_name=payload.first_name,
        last_name=payload.last_name,
        phone_number=payload.phone_number,
        email_address=payload.email_address,
        #linkedin_url=payload.linkedin_url,
        instagram_handle=payload.instagram_handle,
        professional_parameters=payload.professional_parameters,
        #professional_years=payload.professional_years,
    )
    await database.execute(query)
    return {**payload.dict(), "id": user_id}


@app.get("/users/{contact_phone_number}/personal", response_model=UserPersonal, status_code=status.HTTP_200_OK)
async def read_personal_user(contact_phone_number: str):
    query = users.select().where(users.c.phone_number == contact_phone_number)
    return await database.fetch_one(query)


@app.get("/users/{contact_phone_number}/professional", response_model=UserProfessional, status_code=status.HTTP_200_OK)
async def read_professional_user(contact_phone_number: str):
    query = users.select().where(users.c.phone_number == contact_phone_number)
    query_result = await database.fetch_one(query)
    return query_result

@app.get("/users/{contact_phone_number}/professional-parameters", response_model = ProfessionalParameters, status_code=status.HTTP_200_OK)
async def read_professional_parameters(contact_phone_number:str):
    query = users.select().where(users.c.phone_number == contact_phone_number)
    query_result = await database.fetch_one(query)
    return jsonpickle.decode(query_result.professional_parameters) if query_result is not None else None

@app.get("/users/{contact_phone_number}/personal-parameters", response_model = PersonalParameters, status_code=status.HTTP_200_OK)
async def read_personal_parameters(contact_phone_number:str):
    query = users.select().where(users.c.phone_number == contact_phone_number)
    query_result = await database.fetch_one(query)
    return jsonpickle.decode(query_result.personal_parameters) if query_result is not None else None

@app.post("/users/{user_id}/add-group/{group_id}", status_code=status.HTTP_200_OK)
async def add_user_to_group(user_id:int, group_id:int):
    # query = groups.insert().values(group_id=group_id, users_id=)
    # last_record_id = await database.execute(query)
    # return {**groups.dict(), "id": last_record_id}
    # groups.update().where(groups.c.group_id==group_id).values(groups.c.users_id=text(f'array_append({groups.c.users_id.name},{user_id}'))
    return 200

@app.get("/users/{user_id}/read-group/{group_id}", status_code=status.HTTP_102_PROCESSING)
async def read_contacts_from_group(user_id:int, group_id:int):
    return 202


@app.get("/users/", response_model=List[User], status_code=status.HTTP_200_OK)
async def read_users(skip: int = 0, take: int = 20):
    query = users.select().offset(skip).limit(take)
    return await database.fetch_all(query)


@app.get("/users/{user_id}/", response_model=User, status_code=status.HTTP_200_OK)
async def read_users(user_id: int):
    query = users.select().where(users.c.id == user_id)
    return await database.fetch_one(query)


@app.delete("/users/{user_id}/", status_code=status.HTTP_200_OK)
async def remove_user(user_id: int):
    query = users.delete().where(users.c.id == user_id)
    await database.execute(query)
    return {"message": "User with id: {} deleted successfully!".format(user_id)}

#CREATE PERSONAL RELATIONSHIPS
@app.post("/relationships/{user_id}/personal/{contact_phone_number}", response_model=Relationship, status_code=status.HTTP_200_OK)
async def create_personal_relationships(initiator_id: str, receiver_id: str):
    query = relationships.insert().values(
        #CHANGE THE RELATIONSHIP ID
        relationship_id="",
        initiator_id=initiator_id,
        receiver_id=receiver_id,
        isPersonal=True
    )
    print(query)
    last_record_id = await database.execute(query)
    #Check the return statement
    return {**initiator_id.dict(), "id": last_record_id}

#CREATE PROFESSIONAL RELATIONSHIPS
@app.post("/relationships/{user_id}/professional/{contact_phone_number}", response_model=Relationship, status_code=status.HTTP_200_OK)
async def create_professional_relationships(initiator_id: str, receiver_id: str):
    query = relationships.insert().values(
        #CHANGE THE RELATIONSHIP ID
        relationship_id="",
        initiator_id=initiator_id,
        receiver_id=receiver_id,
        isPersonal=False
    )
    print(query)
    last_record_id = await database.execute(query)
    #Check the return statement
    return {**initiator_id.dict(), "id": last_record_id}

#CREATE GROUP
@app.post("/groups/{user_id}/create/{group_id}", response_model=Group, status_code=status.HTTP_200_OK)
async def create_professional_relationships(group_id: str, member1: str,  member2: str,  member3: str,  member4: str,  member5: str):
    query = relationships.insert().values(
        #CHANGE THE GROUP ID
        group_id = group_id,
        member1=member1,
        member2=member2,
        member3=member3,
        member4=member4,
        member5=member5
    )
    print(query)
    last_record_id = await database.execute(query)
    #Check the return statement
    return {**group_id.dict(), "id": last_record_id}
