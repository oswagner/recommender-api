import uvicorn
from fastapi import FastAPI
from routes import api
from fastapi.middleware.cors import CORSMiddleware

tags_metadata = [
    {
        "name": "Personalized by similar users",
        "description": "Técnicas recomendadas que levam em consideração o usuário solicitante, e/ou usuários similares",
    },
    {
        "name": "Non-personalized",
        "description": "Técnicas recomendadas que não levam em consideração o usuário solicitante, e/ou usuários similares",
    },
]

app = FastAPI(
    title="HeliusRecommenderAPI",
    description="Helius Recommender Module API helps you to improve design thinking techniques selection",
    version="1.0",
    contact={
        "name": "Wagner Oliveira dos Santos",
        "email": "w.santos@edu.pucrs.br",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    openapi_tags=tags_metadata)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.router, prefix="/api")

@app.get('/')
def index():
    return {'message': "This is the home page of this API. Go to /docs or /redoc to see available endpoints"}


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=4000, debug=True)