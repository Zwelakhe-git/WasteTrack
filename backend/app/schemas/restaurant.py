from pydantic import BaseModel, ConfigDict

class RestaurantBase(BaseModel):
    name: str
    number: str
    address: str | None = None

class RestaurantCreate(RestaurantBase):
    pass

class RestaurantRead(RestaurantBase):
    id: int
    model_config = ConfigDict(from_attributes=True)