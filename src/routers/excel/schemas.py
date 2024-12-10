from typing import Optional
from pydantic import BaseModel, field_validator


class CarsCreate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    modif: Optional[str] = None
    sk_brand: Optional[str] = None
    sk_model: Optional[str] = None
    type: Optional[str] = None

    @field_validator('brand', 'model', 'modif', 'sk_brand', 'sk_model', 'type')
    def blank_string(value, field):
        if value == "":
            return None
        return value
