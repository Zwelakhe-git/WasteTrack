from pydantic import BaseModel, ConfigDict
from app.models.user import UserRole

class UserBase(BaseModel):
    login: str
    display_name: str
    role: UserRole = UserRole.MANAGER
    restaurant_id: int | None = None

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    avatar_url: str | None = None
    
    # Позволяет Pydantic читать данные из объектов SQLAlchemy
    model_config = ConfigDict(from_attributes=True)