from typing import Annotated

from sqlalchemy import create_engine
from fastapi import Depends
from core.dependencies import get_settings
from sqlmodel import Session

settings = get_settings()

# PostgreSQL connection using environment variables
postgres_url = f"postgresql://{settings.db_username}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

engine = create_engine(postgres_url)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]