import uvicorn
import json
from collect_data import DataHandler
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
data_handler = DataHandler()

@app.get('/')
def index():
    return {'message': "This is the home page of this API. Go to /docs or /redoc to see available endpoints"}

@app.get('/api/user/{user_name}')
def sample_request(user_name: str):
    return {'message': f'Hello! @{user_name}'}

@app.get('/api/most_used')
def most_used_techniques():
    most_used_techniques_str = data_handler.most_used_techniques(as_json=True)
    json_data = json.loads(most_used_techniques_str)
    return json_data

@app.get('/api/top_rated')
def top_rated_techniques():
    most_used_techniques_str = data_handler.top_rated_techniques(as_json=True)
    json_data = json.loads(most_used_techniques_str)
    return json_data


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=4000, debug=True)