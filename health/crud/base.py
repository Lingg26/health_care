from math import floor
from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Query, Session

from health.schemas.base import BaseRequestListSchema, Paginate
from health.shared.database import Base


class CrudBase:
    model: Base = None
    sort_fields = '*'

    def __init__(self) -> None:
        assert self.model is not None, "No model class found"

    def response_pagination(self, total: int, page: int, page_size: int):
        page_count = (
            floor(total / page_size) + 1 if (total % page_size) else floor(total / page_size)
        )
        return {
            'page': page,
            'page_size': page_size,
            'total_count': total,
            'page_count': page_count,
        }

    def all(
        self,
        db: Session,
        query_param: Optional[BaseRequestListSchema] = None,
        filter_by: Dict[str, Any] = {},
    ) -> tuple[list[model], Optional[int], Optional[int], Optional[int]]:
        query = self.get_query_all(db, filter_by, query_param)
        if query_param:
            query = query.filter(*self.get_filter_list(query_param))
            print(query)

            total = query.count()

            query = (
                query.order_by(*self.get_sort_list(query_param.sort_by))
                .limit(query_param.limit)
                .offset(query_param.offset)
            )
            return (
                query.all(),
                Paginate(
                    page_size=query_param.page_size,
                    page=query_param.page,
                    total_count=total,
                    page_count=((total - total % query_param.page_size) / query_param.page_size)
                    + 1,
                ),
            )
        else:
            return (query.all(), None)

    def get(
        self,
        db: Session,
        filter_by: Dict[str, Any],
        raise_exception: Optional[bool] = False,
        error_status: Optional[int] = status.HTTP_404_NOT_FOUND,
        exception_detail: Optional[str] = None,
    ) -> Optional[model]:
        obj = db.query(self.model).filter_by(**filter_by).first()
        if not obj and raise_exception:
            raise HTTPException(
                status_code=error_status,
                detail=exception_detail,
            )
        return obj

    def get_by_id(
        self,
        db: Session,
        id: int,
        raise_exception: Optional[bool] = False,
        exception_detail: Optional[str] = None,
    ):
        return self.get(
            db,
            filter_by={'id': id},
            raise_exception=raise_exception,
            exception_detail=exception_detail,
        )

    def create(
        self,
        db: Session,
        data: Optional[BaseModel] = None,
        default_data: Dict[str, Any] = {},
    ) -> Optional[model]:
        try:
            data = data.copy(update=default_data).dict(exclude_unset=True) if data else default_data
            obj = self.model(**data)
            db.add(obj)
            db.commit()
            db.refresh(obj)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        return obj

    def update(
        self,
        db: Session,
        filter_by: Optional[Dict[str, Any]] = {},
        data: Optional[BaseModel] = None,
        default_data: Optional[Dict[str, Any]] = {},
        instance: Optional[model] = None,
    ) -> Optional[model]:
        obj = self.get(db, filter_by=filter_by, raise_exception=True) if not instance else instance
        try:
            data = data.copy(update=default_data).dict(exclude_unset=True) if data else default_data
            for key, value in data.items():
                setattr(obj, key, value)
            db.add(obj)
            db.commit()
            db.refresh(obj)
            return obj

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def bulk_update(self, db: Session, list_updated_instance: list[model]) -> list[model]:
        db.add_all(list_updated_instance)
        db.commit()
        return list_updated_instance

    def delete(
        self,
        db: Session,
        filter_by: Dict[str, Any],
        instance: Optional[model] = None,
    ) -> Optional[model]:
        obj = self.get(db, filter_by=filter_by, raise_exception=True) if not instance else instance
        try:
            db.delete(obj)
            db.commit()
            return obj
        except Exception as e:
            raise HTTPException(status_code=400)

    def get_sort_list(self, sort_by: Dict[str, Any]) -> list:
        sort_list = []
        for field, sort_type in sort_by.items():
            try:
                if (
                    isinstance(self.sort_fields, (tuple, list))
                    and field in self.sort_fields
                    or self.sort_fields == '*'
                ):
                    sort_item = getattr(self.model, field)
                    sort_item = getattr(sort_item, sort_type)
                    sort_list.append(sort_item())
            except:
                continue
        return sort_list

    def get_filter_list(self, query_param: BaseModel) -> list:
        return []

    def get_query_all(
        self,
        db: Session,
        filter_by: Dict[str, Any] = {},
        query_param: Optional[BaseModel] = None,
    ) -> Query:
        return db.query(self.model).filter_by(**filter_by)
