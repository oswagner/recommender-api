from collect_data import DataHandler
from fastapi.responses import JSONResponse
from typing import List
from models import Technique, ErroMessage, model_mapper
from fastapi import APIRouter, status, Query
from collect_data import DataHandler


router = APIRouter()
data_handler = DataHandler()


@router.get('/rated_by_similar_users/',
            response_model=List[Technique], 
            responses={status.HTTP_404_NOT_FOUND: {"model": ErroMessage}}, 
            tags=["Personalized by similar users"])
async def rated_by_similar_users(user_id: str, n_techiques: int = None):
    techniques = data_handler.get_techniques()
    all_ratings = data_handler.get_ratings_from_techniques(techniques)
    ratings_df = data_handler.build_ratings_data_frame(all_ratings)
    algo = data_handler.fit_knn(ratings_df)
    try:
        neighbors_user_id = data_handler.find_similar_users(algo, user_id)
        recommendations_json_str = data_handler.techinque_recommendations(ratings_df, neighbors_user_id, numer_of_recommendations=n_techiques)
        model_response = model_mapper(recommendations_json_str)
        return model_response
    except ValueError as e:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={'message': str(e)})

@router.get('/same_objective_by_similar_users/',
            response_model=List[Technique], 
            responses={status.HTTP_404_NOT_FOUND: {"model": ErroMessage}}, 
            tags=["Personalized by similar users"])
async def same_objective_by_similar_users(user_id: str, objective: str):
    try:
        recommendations_json_str = data_handler.get_used_by_similars_to_same_objective(user_id, objective)
        model_response = model_mapper(recommendations_json_str)
        return model_response
    except ValueError as e:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={'message': str(e)})

@router.get('/already_used_by_user/',
            response_model=List[Technique], 
            tags=["Personalized by similar users"])
async def already_used_by_user(user_id: str):
        used_techniques_str = data_handler.get_already_used_by_user(user_id)
        model_response = model_mapper(used_techniques_str)
        return model_response

@router.get('/top_rated_already_used_by_user/',
            response_model=List[Technique], 
            tags=["Personalized by similar users"])
async def top_rated_already_used_by_user(user_id: str):
        top_rated_used_techniques_str = data_handler.get_top_rated_and_used_by_user(user_id)
        model_response = model_mapper(top_rated_used_techniques_str)
        return model_response


@router.get('/most_used/', 
            response_model=List[Technique],
            tags=["Non-personalized"])
async def most_used():
    most_used_techniques_str = data_handler.most_used_techniques()
    model_response = model_mapper(most_used_techniques_str)
    return model_response

@router.get('/top_rated/', 
            response_model=List[Technique],
            tags=["Non-personalized"])
async def top_rated():
    top_rated_techniques_str = data_handler.top_rated_techniques()
    model_response = model_mapper(top_rated_techniques_str)
    return model_response

@router.get('/all/', 
            response_model=List[Technique],
            tags=["Non-personalized"])
async def all():
    all_techniques_str = data_handler.all_techniques()
    model_response = model_mapper(all_techniques_str)
    return model_response

@router.get('/top_rated_by_experts/', 
            response_model=List[Technique],
            tags=["Non-personalized"])
async def top_rated_by_experts():
    top_rated_by_experts_str = data_handler.get_top_rated_and_used_by_experts()
    model_response = model_mapper(top_rated_by_experts_str)
    return model_response

@router.get('/top_rated_by_experts_for_same_objective/', 
            response_model=List[Technique],
            tags=["Non-personalized"])
async def top_rated_by_experts_for_same_objective(objective: str):
    top_rated_by_experts_str = data_handler.get_top_rated_and_used_by_experts_to_same_objective(objective)
    model_response = model_mapper(top_rated_by_experts_str)
    return model_response


@router.get('/top_rated_for_same_objective/', 
            response_model=List[Technique],
            tags=["Non-personalized"])
async def top_rated_for_same_objective(objective: str):
    top_rated_to_same_objective_str = data_handler.get_top_rated_to_same_objective(objective)
    model_response = model_mapper(top_rated_to_same_objective_str)
    return model_response

@router.get('/workspace/',
            description="MUST USE ENGLISH VALUES",
            response_model=List[Technique],
            tags=["Non-personalized"], )
async def same_workspace(workspace: List[str] = Query(..., example=['Inspiration', 'Ideation', 'Implementation', 'Problem space', 'Solution space'])):
    same_workspace_str = data_handler.get_top_rated_for_same_workspace(workspace)
    model_response = model_mapper(same_workspace_str)
    return model_response
