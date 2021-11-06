import uvicorn
from fastapi import FastAPI
from routes import api  

app = FastAPI()


app.include_router(api.router, prefix="/api")

@app.get('/')
def index():
    return {'message': "This is the home page of this API. Go to /docs or /redoc to see available endpoints"}


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=4000, debug=True)