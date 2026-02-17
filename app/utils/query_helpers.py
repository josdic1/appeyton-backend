# app/utils/query_helpers.py
from fastapi import HTTPException

def apply_permission_filter(query, model, scope, user_id):
    """
    Injects a .filter() if the scope is 'own'.
    """
    if scope == "all":
        return query
    
    if scope == "own":
        # Assumes your models have a 'user_id' field
        if hasattr(model, 'user_id'):
            return query.filter(model.user_id == user_id)
        raise HTTPException(status_code=500, detail="Ownership check requested on model without user_id")
    
    return query