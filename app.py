import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

class User(BaseModel):
    user_id: str


app = FastAPI()

@app.get('/')
def index():
    return {'message': "This is the home page of this API. Go to /docs to see available endpoints"}


@app.get('/api/{user_id}')
def api1(user_id: str):
    return {'message': f'Hello! @{user_id}'}


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=4000, debug=True)