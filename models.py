import json
from pydantic import BaseModel, Field
from typing import List, Optional

class Technique(BaseModel):
    id: str = Field(..., alias='_id')
    name: str = None
    nameT: List[str] = None
    count: Optional[int] = None
    rating: Optional[float] = None
    
    class Config:
        schema_extra = {
            "example": {
                '_id':'617f1b4ef0a90c7c757926ba',
                "name": "A day in the life",
                "nameT": [
                    "A day in the life",
                    "Um dia na vida"
                ],
                "count": 1,
                "rating": 2.5,
            }
        }
class ErroMessage(BaseModel):
    message: str

def model_mapper(json_str):
    tech_dict = json.loads(json_str)
    # print(f"[model_mapper - tech_dict]: {tech_dict} \n")
    tech_list = [ Technique(**tech) for tech in tech_dict ]
    # print(f"[model_mapper - tech_list]: {tech_dict} \n")
    return tech_list