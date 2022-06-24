import json
from typing import List, Optional, Dict, Any

import jsonpickle
import databases
import sqlalchemy
from asyncpg import Record
from fastapi import FastAPI, status, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Json
from sqlalchemy import Integer, or_, and_
from sqlalchemy.dialects.postgresql import JSONB
import os
import urllib

#DATABASE_URL = "sqlite:///./test.db"

# host_server = os.environ.get('host_server', 'localhost')
# db_server_port = urllib.parse.quote_plus(str(os.environ.get('db_server_port', '5432')))
# database_name = os.environ.get('database_name', 'fastapi')
# db_username = urllib.parse.quote_plus(str(os.environ.get('db_username', 'postgres')))
# db_password = urllib.parse.quote_plus(str(os.environ.get('db_password', 'secret')))
# ssl_mode = urllib.parse.quote_plus(str(os.environ.get('ssl_mode','require')))
# DATABASE_URL = 'postgresql://{}:{}@{}:{}/{}?sslmode={}'.format(db_username, db_password, host_server, db_server_port, database_name, ssl_mode)
DATABASE_URL = "postgresql://tyhogopgeybpov:b1bfaf71b3aaa3c7db86ce5eb4630b6393ee82a39f25f22fdd23baa2a4cd1225@ec2-34-200-35-222.compute-1.amazonaws.com:5432/dfac6s87cm7bgo"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("first_name", sqlalchemy.String),
    sqlalchemy.Column("last_name", sqlalchemy.String),
    # PHONE NUMBER IS SUPPOSED TO BE A STRING!!
    sqlalchemy.Column("phone_number", sqlalchemy.String, unique=True),
    sqlalchemy.Column("email_address", sqlalchemy.String),
    # sqlalchemy.Column("linkedin_url", sqlalchemy.String),
    sqlalchemy.Column("location", sqlalchemy.String),
    sqlalchemy.Column("instagram_handle", sqlalchemy.String),
    sqlalchemy.Column("professional_parameters", sqlalchemy.dialects.postgresql.JSON),
    sqlalchemy.Column("personal_parameters", sqlalchemy.dialects.postgresql.JSON),
    sqlalchemy.Column("group_id", sqlalchemy.String),
    # sqlalchemy.Column("professional_years", sqlalchemy.Integer),
)

relationships = sqlalchemy.Table(
    "relationships",
    metadata,
    sqlalchemy.Column("relationship_id", sqlalchemy.Integer, primary_key=True, unique=True),
    sqlalchemy.Column("initiator_id", sqlalchemy.String),
    sqlalchemy.Column("receiver_id", sqlalchemy.String),
    # PHONE NUMBER IS SUPPOSED TO BE A STRING!!
    sqlalchemy.Column("isPersonal", sqlalchemy.Boolean)
)

# groups = sqlalchemy.Table(
#     "groups",
#     metadata,
#     sqlalchemy.Column("group_id", sqlalchemy.Integer, primary_key=True, unique=True),
#     sqlalchemy.Column("member1", sqlalchemy.String),
#     sqlalchemy.Column("member2", sqlalchemy.String),
#     # PHONE NUMBER IS SUPPOSED TO BE A STRING!!
#     sqlalchemy.Column("member3", sqlalchemy.String),
#     sqlalchemy.Column("member4", sqlalchemy.String),
#     sqlalchemy.Column("member5", sqlalchemy.String)
# )

# LOCAL version
engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
metadata.create_all(engine)


# PostgreSQL version
# engine = sqlalchemy.create_engine(
#     DATABASE_URL
# )
# metadata.create_all(engine)


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
    # fashion: Optional[bool]
    gamer: Optional[bool]
    pets: Optional[bool]


# # Model of JSON payload for Create and Update user endpoints
class UserCreate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    email_address: Optional[str]
    location: Optional[str]
    instagram_handle: Optional[str]
    personal_parameters: PersonalParameters | None = None
    professional_parameters: ProfessionalParameters | None = None


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
    professional_parameters: ProfessionalParameters | None = None


# # Model of JSON response for Update users collection
class UserComplete(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    email_address: Optional[str]
    location: Optional[str]
    instagram_handle: Optional[str]
    personal_parameters: PersonalParameters | None = None
    professional_parameters: ProfessionalParameters | None = None


# Model of JSON response for Retrieve personal information of contact
class UserPersonal(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    email_address: Optional[str]
    location: Optional[str]
    instagram_handle: Optional[str]
    personal_parameters: PersonalParameters | None = None
    # personal_parameters: PersonalParameters | None


# Model of JSON response for Retrieve professional information of contact
class UserProfessional(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    email_address: Optional[str]
    location: Optional[str]
    instagram_handle: Optional[str]
    # personal_parameters: PersonalParameters | None = None
    personal_parameters: PersonalParameters | None

class UserSimple(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    email_address: Optional[str]
    location: Optional[str]
    instagram_handle: Optional[str]

# class Group(BaseModel):
#     id: int
#     contact_ids: List[int]

# class Group(BaseModel):
#     # group_id: Optional[str]
#     group_id: int
#     member1: Optional[str]
#     member2: Optional[str]
#     member3: Optional[str]
#     member4: Optional[str]
#     member5: Optional[str]


class Relationship(BaseModel):
    # relationship_id: Optional[str]
    relationship_id: int
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


@app.post("/users/", response_model=UserCreate, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    query = users.insert().values(
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number,
        email_address=user.email_address,
        location=user.location,
        # linkedin_url=user.linkedin_url,
        instagram_handle=user.instagram_handle,
        # professional_parameters=user.professional_parameters,
        # personal_parameters=user.personal_parameters,
        # professional_parameters=json.dumps(jsonable_encoder(user.professional_parameters)),
        # personal_parameters=json.dumps(jsonable_encoder(user.personal_parameters)),
        professional_parameters=jsonpickle.encode(user.professional_parameters),
        personal_parameters=jsonpickle.encode(user.personal_parameters),
        # professional_years=user.professional_years,
    )
    print(query)
    try:
        last_record_id = await database.execute(query)
    except:
        raise HTTPException(status_code=422, detail="User already in database")
    return {**user.dict(), "id": last_record_id}


# @app.get("/fetch/personal/{user_id}", response_model=List[UserPersonal], status_code=status.HTTP_200_OK)
# async def fetch_personal_contacts


@app.get("/testing/users/{contact_phone_number}/personal", response_model=UserPersonal, status_code=status.HTTP_200_OK)
async def test_fetch_personal_contact(contact_phone_number: str):
    query = users.select().where(users.c.phone_number == contact_phone_number)
    query_result = await database.fetch_one(query)
    decodedPersonalParameters = jsonpickle.decode(
        query_result.personal_parameters) if query_result is not None else None
    if query_result is None:
        raise HTTPException(status_code=305, detail="User is not in our database")
    # query_result.personal_parameters = decodedPersonalParameters
    return {
        "first_name": query_result.first_name,
        "last_name": query_result.last_name,
        "phone_number": query_result.phone_number,
        "email_address": query_result.email_address,
        "location": query_result.location,
        "instagram_handle": query_result.instagram_handle,
        "personal_parameters": decodedPersonalParameters,
    }


@app.get("/testing/users/{contact_phone_number}/professional", response_model=UserProfessional,
         status_code=status.HTTP_200_OK)
async def test_fetch_professional_contact(contact_phone_number: str):
    query = users.select().where(users.c.phone_number == contact_phone_number)
    query_result = await database.fetch_one(query)
    decodedProfessionalParameters = jsonpickle.decode(
        query_result.professional_parameters) if query_result is not None else None
    if query_result is None:
        raise HTTPException(status_code=305, detail="User is not in our database")
    # query_result.personal_parameters = decodedPersonalParameters
    return {
        "first_name": query_result.first_name,
        "last_name": query_result.last_name,
        "phone_number": query_result.phone_number,
        "email_address": query_result.email_address,
        "location": query_result.location,
        "instagram_handle": query_result.instagram_handle,
        "professional_parameters": decodedProfessionalParameters,
    }

@app.get("/testing/{user_id}/relationships/personal/", response_model=List[Relationship], status_code=status.HTTP_200_OK)
async def test_fetch_personal_relationships(user_id:str):
    query = relationships.select().where(
        and_(or_(relationships.c.initiator_id == user_id, relationships.c.receiver_id == user_id),
             (relationships.c.isPersonal == True)))
    query_result = await database.fetch_all(query)
    if query_result:
        return query_result
    else:
        raise HTTPException(status_code=404, detail="No personal relationships exist")

@app.get("/testing/{user_id}/relationships/personal/ids", response_model=List[str], status_code=status.HTTP_200_OK)
async def test_fetch_personal_relationships_ids(user_id:str):
    query = relationships.select().where(
        and_(or_(relationships.c.initiator_id == user_id, relationships.c.receiver_id == user_id),
             (relationships.c.isPersonal == True)))
    query_result = await database.fetch_all(query)
    if query_result:
        return query_result
    else:
        raise HTTPException(status_code=404, detail="No personal relationships exist")

@app.get("/testing/{user_id}/relationships/professional/", response_model=List[Relationship], status_code=status.HTTP_200_OK)
async def test_fetch_professional_relationships(user_id:str):
    query = relationships.select().where(
        and_(or_(relationships.c.initiator_id == user_id, relationships.c.receiver_id == user_id),
             (relationships.c.isPersonal == False)))
    query_result = await database.fetch_all(query)
    if query_result:
        return query_result
    else:
        raise HTTPException(status_code=404, detail="No professional relationships exist")

@app.get("/fetch/{user_id}", response_model=List[User], status_code=status.HTTP_200_OK)
async def fetch_contacts(user_id: str):
    personal_related_relationships_query = relationships.select().where(
        and_(or_(relationships.c.initiator_id == user_id, relationships.c.receiver_id == user_id),
             (relationships.c.isPersonal == True)))
    personal_related_relationships = await database.fetch_all(personal_related_relationships_query)
    print("Personal Related Relationships Query")
    print(personal_related_relationships_query)
    # professional_related_relationships_query = relationships.select().where(
    #     and_(or_(relationships.c.initiator_id == user_id, relationships.c.receiver_id == user_id),
    #          (relationships.c.isPersonal == False)))
    # professional_related_relationships = await database.fetch_all(professional_related_relationships_query)
    # print(professional_related_relationships_query)
    contacts = List[User]
    for personal_relationship in personal_related_relationships:
        personal_contact_details_query = users.select().where(users.c.phone_number == personal_relationship[3])
        print("Personal Contact Details Query")
        print(personal_contact_details_query)
        personal_contact_details = await database.fetch_one(personal_contact_details_query)
        if personal_contact_details is not None:
            contacts.append(personal_contact_details)
    # for professional_relationship in professional_related_relationships:
    #     professional_contact_details_query = users.select().where(users.c.phone_number == professional_relationship[3])
    #     print(professional_contact_details_query)
    #     professional_contact_details = await database.fetch_one(professional_contact_details_query)
    #     if professional_contact_details is not None:
    #     contacts.append(professional_contact_details)
    return contacts


# CREATE PERSONAL RELATIONSHIPS
@app.post("/relationships/{user_id}/personal/{contact_phone_number}", response_model=Relationship,
          status_code=status.HTTP_200_OK)
async def create_personal_relationships(user_id: str, contact_phone_number: str):
    query = relationships.insert().values(
        # TODO: CHANGE THE RELATIONSHIP ID - prithvi; don't think we need it - marcus
        # relationship_id="",
        initiator_id=user_id,
        receiver_id=contact_phone_number,
        isPersonal=True
    )
    print(query)
    last_record_id = await database.execute(query)
    # TODO: Check the return statement; not necessary, returning ID should be sufficient
    # return {**initiator_id.dict(), "id": last_record_id}
    return {"relationship_id": last_record_id, "initiator_id": user_id, "receiver_id": contact_phone_number,
            "isPersonal": True}


# CREATE PROFESSIONAL RELATIONSHIPS
@app.post("/relationships/{user_id}/professional/{contact_phone_number}", response_model=Relationship,
          status_code=status.HTTP_200_OK)
async def create_professional_relationships(user_id: str, contact_phone_number: str):
    query = relationships.insert().values(
        # TODO: CHANGE THE RELATIONSHIP ID - prithvi; don't think we need it - marcus
        # relationship_id="",
        initiator_id=user_id,
        receiver_id=contact_phone_number,
        isPersonal=False
    )
    print(query)
    last_record_id = await database.execute(query)
    # TODO: Check the return statement; not necessary, returning ID should be sufficient
    # return {**initiator_id.dict(), "id": last_record_id}
    return {"relationship_id": last_record_id, "initiator_id": user_id, "receiver_id": contact_phone_number,
            "isPersonal": False}


# CREATE GROUP
@app.post("/groups/{user_id}/create/{group_id}", status_code=status.HTTP_200_OK)
async def create_group(user_id: str, group_id: str):
    # query = relationships.insert().values(
    #     # TODO: CHANGE THE GROUP ID - prithvi; don't think we need it - Marcus
    #     # group_id=group_id,
    #     member1=member1,
    #     member2=member2,
    #     member3=member3,
    #     member4=member4,
    #     member5=member5
    # )
    query = users.update().where(users.c.id == user_id).values(group_id=group_id)
    print(query)
    last_record_id = await database.execute(query)
    # TODO: Check the return statement; probably not necesary either
    # return {**group_id.dict(), "id": last_record_id}
    return {"group_id": group_id, "user_id": user_id}


@app.get("/users/{user_id}/read-group/{group_id}", response_model=List[UserComplete], status_code=status.HTTP_200_OK)
async def fetch_group(user_id: int, group_id: int):
    query = users.select().where(users.c.group_id == group_id)
    query_result = await database.fetch_all(query)
    if not query_result:
        raise HTTPException(status_code=305, detail="The group does not exist")
    # return query_result
    responses = []
    for query_resultant in query_result:
        decodedProfessionalParameters = jsonpickle.decode(query_resultant.professional_parameters)
        decodedPersonalParameters = jsonpickle.decode(query_resultant.personal_parameters)
        newResponse = {
            "first_name": query_resultant.first_name,
            "last_name": query_resultant.last_name,
            "phone_number": query_resultant.phone_number,
            "email_address": query_resultant.email_address,
            "location": query_resultant.location,
            "instagram_handle": query_resultant.instagram_handle,
            "professional_parameters": decodedProfessionalParameters,
            "personal_parameters": decodedPersonalParameters,
        }
        responses.append(newResponse)
    return responses


@app.delete("/users/{user_id}/delete", status_code=status.HTTP_200_OK)
async def remove_user(user_id: int):
    query = users.delete().where(users.c.phone_number == user_id)
    await database.execute(query)
    return {"message": "User with id: {} deleted successfully!".format(user_id)}

# @app.put("/users/{user_id}/", response_model=User, status_code=status.HTTP_200_OK)
# async def update_user(user_id: int, payload: User):
#     query = users.update().where(users.c.id == user_id).values(
#         first_name=payload.first_name,
#         last_name=payload.last_name,
#         phone_number=payload.phone_number,
#         email_address=payload.email_address,
#         # linkedin_url=payload.linkedin_url,
#         instagram_handle=payload.instagram_handle,
#         professional_parameters=payload.professional_parameters,
#         # professional_years=payload.professional_years,
#     )
#     await database.execute(query)
#     return {**payload.dict(), "id": user_id}


# @app.get("/users/{contact_phone_number}/personal", response_model=UserPersonal, status_code=status.HTTP_200_OK)
# async def read_personal_user(contact_phone_number: str):
#     query = users.select().where(users.c.phone_number == contact_phone_number)
#     return await database.fetch_one(query)
#
#
# @app.get("/users/{contact_phone_number}/professional", response_model=UserProfessional, status_code=status.HTTP_200_OK)
# async def read_professional_user(contact_phone_number: str):
#     query = users.select().where(users.c.phone_number == contact_phone_number)
#     query_result = await database.fetch_one(query)
#     return query_result
#
#
# @app.get("/users/{contact_phone_number}/professional-parameters", response_model=ProfessionalParameters,
#          status_code=status.HTTP_200_OK)
# async def read_professional_parameters(contact_phone_number: str):
#     query = users.select().where(users.c.phone_number == contact_phone_number)
#     query_result = await database.fetch_one(query)
#     return jsonpickle.decode(query_result.professional_parameters) if query_result is not None else None
#
#
# @app.get("/users/{contact_phone_number}/personal-parameters", response_model=PersonalParameters,
#          status_code=status.HTTP_200_OK)
# async def read_personal_parameters(contact_phone_number: str):
#     query = users.select().where(users.c.phone_number == contact_phone_number)
#     query_result = await database.fetch_one(query)
#     return jsonpickle.decode(query_result.personal_parameters) if query_result is not None else None
#
#
# @app.post("/users/{user_id}/add-group/{group_id}", status_code=status.HTTP_200_OK)
# async def add_user_to_group(user_id: int, group_id: int):
#     # query = groups.insert().values(group_id=group_id, users_id=)
#     # last_record_id = await database.execute(query)
#     # return {**groups.dict(), "id": last_record_id}
#     # groups.update().where(groups.c.group_id==group_id).values(groups.c.users_id=text(f'array_append({groups.c.users_id.name},{user_id}'))
#     return 200
#
#

#
#
# @app.get("/users/", response_model=List[User], status_code=status.HTTP_200_OK)
# async def read_users(skip: int = 0, take: int = 20):
#     query = users.select().offset(skip).limit(take)
#     return await database.fetch_all(query)
#
#

#
#


# @app.get("/users/{contact_phone_number}/professional-parameters", response_model=ProfessionalParameters,
#          status_code=status.HTTP_200_OK)
# async def read_professional_parameters(contact_phone_number: str):
#     query = users.select().where(users.c.phone_number == contact_phone_number)
#     query_result = await database.fetch_one(query)
#     return jsonpickle.decode(query_result.professional_parameters) if query_result is not None else None
#
#
# @app.get("/users/{contact_phone_number}/personal-parameters", response_model=PersonalParameters,
#          status_code=status.HTTP_200_OK)
# async def read_personal_parameters(contact_phone_number: str):
#     query = users.select().where(users.c.phone_number == contact_phone_number)
#     query_result = await database.fetch_one(query)
#     return jsonpickle.decode(query_result.personal_parameters) if query_result is not None else None
