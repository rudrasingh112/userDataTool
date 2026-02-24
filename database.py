import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

INSTANCE_CONNECTION_NAME = "gen-lang-client-0906242882:us-central1:adk-user-db"

DB_USER = "postgres"
DB_PASS = "Qwerty%40123"
DB_NAME = "user_adk_db"

# 3. Constructing the final URL
SQLALCHEMY_DATABASE_URL = (
    f"postgresql+pg8000://{DB_USER}:{DB_PASS}@/{DB_NAME}"
    f"?unix_sock=/cloudsql/{INSTANCE_CONNECTION_NAME}/.s.PGSQL.5432"
)



engine = create_engine(url = SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(bind= engine, autoflush= False)

Base = declarative_base()
