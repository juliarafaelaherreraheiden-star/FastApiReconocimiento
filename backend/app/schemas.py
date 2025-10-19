from typing import List, Optional
from pydantic import BaseModel

class Recipe(BaseModel):
    id: int
    title: str
    ingredients: List[str]
    categories: List[str]
    calories: Optional[int]
    protein: Optional[int]
    fat: Optional[int]
    sodium: Optional[int]
    rating: Optional[float]
    date: Optional[str] 
    desc: Optional[str]  
    directions: List[str]
    

class SearchResponse(BaseModel):
    total: int
    recipes: List[Recipe]
