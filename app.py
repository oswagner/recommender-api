import uvicorn
from collect_data import DataHandler
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from typing import List
from models import Technique, ErroMessage, model_mapper

app = FastAPI()
data_handler = DataHandler()

@app.get('/')
def index():
    return {'message': "This is the home page of this API. Go to /docs or /redoc to see available endpoints"}

@app.get('/api/user/{raw_user_id}', response_model=List[Technique], responses={status.HTTP_404_NOT_FOUND: {"model": ErroMessage}})
def get_recommendations_from_similar_users(raw_user_id: str):
    techniques = data_handler.get_techniques()
    all_ratings = data_handler.get_ratings_from_techniques(techniques)
    ratings_df = data_handler.build_ratings_data_frame(all_ratings)
    algo = data_handler.fit_knn(ratings_df)
    try:
        neighbors_user_id = data_handler.find_similar_users(algo, raw_user_id)
        recommendations_json_str = data_handler.techinque_recommendations(ratings_df, neighbors_user_id)
        model_response = model_mapper(recommendations_json_str)
        return model_response
    except ValueError as e:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={'message': str(e)})

@app.get('/api/most_used', response_model=List[Technique])
def most_used_techniques():
    most_used_techniques_str = data_handler.most_used_techniques(as_json=True)
    model_response = model_mapper(most_used_techniques_str)
    return model_response

@app.get('/api/top_rated', response_model=List[Technique])
def top_rated_techniques():
    top_rated_techniques_str = data_handler.top_rated_techniques(as_json=True)
    model_response = model_mapper(top_rated_techniques_str)
    return model_response


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=4000, debug=True)