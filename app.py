from pydantic.tools import parse_obj_as
import uvicorn
from collect_data import DataHandler
from fastapi import FastAPI
from pydantic import BaseModel

class User(BaseModel):
    user_id: str


app = FastAPI()

data_handler = DataHandler()

@app.get('/')
def index():
    return {'message': "This is the home page of this API. Go to /docs to see available endpoints"}


@app.get('/api/user/{user_id}')
def sample_request(user_id: str):
    return {'message': f'Hello! @{user_id}'}

@app.get('/api/most_used')
def most_used_techniques():
    most_used_techniques = data_handler.most_used_techniques(as_json=True)
    print(most_used_techniques)
    return most_used_techniques


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=4000, debug=True)