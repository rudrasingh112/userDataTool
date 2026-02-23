from pydantic import BaseModel, Field
from sqlalchemy import String, Column, Boolean, Integer, DateTime
from sqlalchemy.dialects.postgresql import JSONB  # Import this for JSONB
from database import Base
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users" # lowercase is standard in Postgres

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Store all user details in this one flexible column
    user_data = Column(JSONB, default={})

# The Pydantic model stays the same—it still validates the input
class UserRequest(BaseModel):
    first_name: str
    last_name: str
    phone_number: int
    current_plan: str