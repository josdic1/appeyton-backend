# app/utils/query_helpers.py
from typing import Any, Type
from fastapi import HTTPException, status
from sqlalchemy import false  # Use the SQLAlchemy construct for 'False'
from sqlalchemy.orm import Query

def apply_permission_filter(
    query: Query, 
    model: Type[Any], 
    scope: str, 
    user_id: int,
    alt_field: str | None = None
) -> Query:
    """
    Infers the correct column to filter by based on the model structure.
    """
    if scope == "all":
        return query
    
    if scope == "own":
        # 1. Use the override field if provided
        if alt_field and hasattr(model, alt_field):
            return query.filter(getattr(model, alt_field) == user_id)
        
        # 2. Check for standard 'user_id'
        if hasattr(model, 'user_id'):
            return query.filter(getattr(model, 'user_id') == user_id)
        
        # 3. Check for 'created_by_user_id'
        if hasattr(model, 'created_by_user_id'):
            return query.filter(getattr(model, 'created_by_user_id') == user_id)
            
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Model '{model.__name__}' does not support ownership filtering."
        )
    
    # If scope is 'none', we want a SQL-rendered FALSE (usually 1=0)
    # This satisfies Pylance's requirement for a _ColumnExpressionArgument
    return query.filter(false())