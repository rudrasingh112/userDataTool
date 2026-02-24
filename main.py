import uuid
import logging
from fastapi import FastAPI, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import User, UserRequest
import models

logging.basicConfig(level=logging.INFO,
                    format="%(levelname)s: %(message)s")
logger= logging.getLogger(__name__)

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.post("/user/create", status_code=status.HTTP_201_CREATED) # 201 is better for 'Create'
async def create_user(db: db_dependency, user_info: UserRequest):
    logger.info(f"Attempting to create user: {user_info.first_name}{user_info.last_name}")
    try:
        new_user_id = str(uuid.uuid4())
        
        # We map the Pydantic model directly to the JSONB column
        new_user = User(
            user_id=new_user_id,
            user_data={
                "first_name": user_info.first_name,
                "last_name": user_info.last_name,
                "phone_number": user_info.phone_number,
                "current_plan": user_info.current_plan,
            }
        )

        db.add(new_user)
        db.commit()
        # Return the ID so your Agent can use it later
        logger.info(f"Successfully created user with ID: {new_user_id}")
        return {"user_id": new_user_id, "status": "success"}

    except Exception as e:
        db.rollback() # Important: undo the failed transaction
        logger.error(f"Failed to create user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection failed: {str(e)}"
        )

@app.get("/user/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_details(user_id: str, db: db_dependency):
    # No try/except needed for the query itself; SQLAlchemy handles empty results with None
    user_model = db.query(User).filter(User.user_id == user_id).first()
    
    if user_model is None:
        logger.warning(f"No user found with user id: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user_model.user_id,
        "created_at": user_model.created_at,
        "profile": user_model.user_data # This returns the JSON exactly as stored
    }