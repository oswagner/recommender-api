from collect_data import DataHandler
from fastapi.responses import JSONResponse
from typing import List
from models import Technique, ErroMessage, model_mapper
from fastapi import APIRouter, status, Query
from database_reader.database_reader_mongo import DatabaseReaderMongo
from specialized_recommender import non_personalized
from specialized_recommender.non_personalized import NonPesonalizedRecommender
from specialized_recommender.personalized import PesonalizedRecommender


router = APIRouter()
mongoReader = DatabaseReaderMongo()

personalized = PesonalizedRecommender(mongoReader)
non_personalized = NonPesonalizedRecommender(mongoReader)


## MARk: - Personalized by similar users
@router.get('/rated_by_similar_users/',
            response_model=List[Technique], 
            responses={status.HTTP_404_NOT_FOUND: {"model": ErroMessage}}, 
            tags=["Personalized by similar users"],
            description="Todas técnicas usadas por usuários similares e Técnicas bem avaliadas por usuários similares, ao passar a query string `n_techniques`")
async def rated_by_similar_users(user_id: str, n_techniques: int = None):
    try:
        recommendations_json_str = personalized.get_rated_by_similar_users(user_id, n_techniques)
        model_response = model_mapper(recommendations_json_str)
        return model_response
    except ValueError as e:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={'message': str(e)})

@router.get('/same_objective_by_similar_users/',
            response_model=List[Technique], 
            responses={status.HTTP_404_NOT_FOUND: {"model": ErroMessage}}, 
            tags=["Personalized by similar users"],
            description="Todas técnicas usadas por usuários similares para um objetivo")
async def same_objective_by_similar_users(user_id: str, objective: str):
    try:
        recommendations_json_str = personalized.get_used_by_similars_to_same_objective(user_id, objective)
        model_response = model_mapper(recommendations_json_str)
        return model_response
    except ValueError as e:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={'message': str(e)})

@router.get('/already_used_by_user/',
            response_model=List[Technique], 
            tags=["Personalized by similar users"],
            description="Técnicas já usadas")
async def already_used_by_user(user_id: str):
        used_techniques_str = personalized.get_already_used_by_user(user_id)
        model_response = model_mapper(used_techniques_str)
        return model_response

@router.get('/top_rated_already_used_by_user/',
            response_model=List[Technique], 
            tags=["Personalized by similar users"],
            description="Técnicas já usadas e bem avaliadas")
async def top_rated_already_used_by_user(user_id: str):
        top_rated_used_techniques_str = personalized.get_top_rated_and_used_by_user(user_id)
        model_response = model_mapper(top_rated_used_techniques_str)
        return model_response

@router.get('/top_rated_by_user_for_same_objective/',
            response_model=List[Technique], 
            tags=["Personalized by similar users"],
            description="Técnicas por objetivo bem avaliadas pelo usuário")
async def top_rated_by_user_for_same_objective(user_id: str, objective: str):
        get_top_rated_by_user_for_same_objective_str = personalized.get_top_rated_by_user_for_same_objective(user_id, objective)
        model_response = model_mapper(get_top_rated_by_user_for_same_objective_str)
        return model_response


## MARk: - Non-Personalized 
@router.get('/most_used/', 
            response_model=List[Technique],
            tags=["Non-personalized"],
            description="Técnicas mais usadas")
async def most_used():
    most_used_techniques_str = non_personalized.most_used_techniques()
    model_response = model_mapper(most_used_techniques_str)
    return model_response

@router.get('/top_rated/', 
            response_model=List[Technique],
            tags=["Non-personalized"],
            description="Técnicas melhor avaliadas")
async def top_rated():
    top_rated_techniques_str = non_personalized.top_rated_techniques()
    model_response = model_mapper(top_rated_techniques_str)
    return model_response

@router.get('/all/', 
            response_model=List[Technique],
            tags=["Non-personalized"],
            description="Todas as técnicas")
async def all():
    all_techniques_str = non_personalized.all_techniques()
    model_response = model_mapper(all_techniques_str)
    return model_response

@router.get('/top_rated_by_experts/', 
            response_model=List[Technique],
            tags=["Non-personalized"],
            description="Técnicas bem avaliadas por experts em DT")
async def top_rated_by_experts():
    top_rated_by_experts_str = non_personalized.get_top_rated_and_used_by_experts()
    model_response = model_mapper(top_rated_by_experts_str)
    return model_response

@router.get('/average_rated_by_experts/', 
            response_model=List[Technique],
            tags=["Non-personalized"],
            description="Técnicas com avaliação média")
async def average_rated_by_experts():
    average_rated_by_experts_str = non_personalized.get_average_rated_by_experts()
    model_response = model_mapper(average_rated_by_experts_str)
    return model_response

@router.get('/low_cost/', 
            response_model=List[Technique],
            tags=["Non-personalized"],
            description="Técnicas de baixo custo")
async def low_cost():
    low_cost_str = non_personalized.get_low_cost()
    model_response = model_mapper(low_cost_str)
    return model_response

@router.get('/best_cost_benefit/', 
            response_model=List[Technique],
            tags=["Non-personalized"],
            description="Técnicas com alta razão custo-benefício")
async def best_cost_benefit():
    best_cost_benefit_str = non_personalized.get_best_cost_benefit()
    model_response = model_mapper(best_cost_benefit_str)
    return model_response

@router.get('/top_rated_by_experts_for_same_objective/', 
            response_model=List[Technique],
            tags=["Non-personalized"],
            description="Técnicas por objetivo")
async def top_rated_by_experts_for_same_objective(objective: str):
    top_rated_by_experts_str = non_personalized.get_top_rated_and_used_by_experts_to_same_objective(objective)
    model_response = model_mapper(top_rated_by_experts_str)
    return model_response


@router.get('/top_rated_for_same_objective/', 
            response_model=List[Technique],
            tags=["Non-personalized"],
            description="Técnicas bem avaliadas para o mesmo objetivo")
async def top_rated_for_same_objective(objective: str):
    top_rated_to_same_objective_str = non_personalized.get_top_rated_to_same_objective(objective)
    model_response = model_mapper(top_rated_to_same_objective_str)
    return model_response

@router.get('/workingspace/',
            description="Técnicas por espaço de trabalho [MUST USE ENGLISH VALUES]",
            response_model=List[Technique],
            tags=["Non-personalized"])
async def same_workingspace(workingspace: List[str] = Query(..., example=['Inspiration', 'Ideation', 'Implementation', 'Problem space', 'Solution space'])):
    same_workspace_str = non_personalized.get_top_rated_for_same_workspace(workingspace)
    model_response = model_mapper(same_workspace_str)
    return model_response
