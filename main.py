import uuid
from fastapi import FastAPI, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import User, UserRequest
import models

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
        return {"user_id": new_user_id, "status": "success"}

    except Exception as e:
        db.rollback() # Important: undo the failed transaction
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection failed: {str(e)}"
        )

@app.get("/user/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_details(user_id: str, db: db_dependency):
    # No try/except needed for the query itself; SQLAlchemy handles empty results with None
    user_model = db.query(User).filter(User.user_id == user_id).first()
    
    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user_model.user_id,
        "created_at": user_model.created_at,
        "profile": user_model.user_data # This returns the JSON exactly as stored
    }