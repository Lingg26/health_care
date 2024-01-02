import json
from typing import Generic, List, Optional, Type, TypeVar

from fastapi import HTTPException, status
from pydantic import BaseModel, Field, validator
from pydantic.generics import GenericModel


class Paginate(BaseModel):
    page_size: int = Field(example=20)
    page: int = Field(example=1)
    page_count: int = Field(example=10)
    total_count: int = Field(example=680)


class BaseRequestListSchema(BaseModel):
    page_size: int = Field(example=20, default=20, description='number of records')
    page: int = Field(example=1, default=1)
    sort_by: Optional[str] = Field(default={"created_at": "asc"})

    @property
    def limit(self):
        return self.page_size

    @property
    def offset(self):
        return (self.page - 1) * self.page_size

    @validator('sort_by')
    def must_be_dictionary(cls, v):
        try:
            val = json.loads(v)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='must be a dictionary'
            )
        return val


class BaseListResponse(BaseModel):
    paginate: Paginate

    class Config:
        orm_mode = True


# Define a type variable T which will be used to type-hint our generic class
T = TypeVar('T', bound=BaseModel)


# Create a generic class that can accept any type of ResponseItem
class GenericListResponse(GenericModel, Generic[T]):
    """
    A generic list response class to handle various types of items in a list response.

    Type Parameter:
    - T: The type of item in the list response.
    """

    data: List[T]
