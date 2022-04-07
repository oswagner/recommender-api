import json
from pydantic import BaseModel, Field
from typing import List, Optional


class Model(BaseModel):    
    name: List[str]
    etapas: List[str]
    label: List[str]
class Characteristics(BaseModel):    
    materials: List[str]
    duration: List[str]
    location: List[str]
    participants: List[str]
    classification: List[str]
    reference: List[str]
    
class Evaluate(BaseModel):
    user: str = None
    rate: float = None
    cost: float = None
    howWas: str = None
    howManyPeople: List[str] = None
    project: str = None
    techniques: List[str] = None
    recommend: bool = None
    date: str = None
    countTechnique: float = None
    
class Technique(BaseModel):
    id: str = Field(..., alias='_id')
    name: str = None
    nameT: List[str] = None
    count: Optional[int] = None
    rating: Optional[float] = None
    description: List[str] = None
    howToUse: List[str] = None
    whenToUse: List[str] = None
    rating: float = None
    image: str = None
    projects: List[str] = None
    evaluate: List[Evaluate] = None
    count: float = None
    characteristics: Characteristics = None
    objective: List[str] = None
    models: List[Model] = None
    
    class Config:
        schema_extra = {
            "example": {
                "_id": "6128fcd36337a400164e99b3",
                "name": "A day in the life",
                "nameT": [
                "A day in the life",
                "Um dia na vida"
                ],
                "count": 3,
                "rating": 4,
                "description": [
                "A day in the life can be defined as a simulation carried out by the researcher of the life of the respondent, considering the activities performed and the situations experienced.\nIt is an ethnographic method in which the researcher follows the user's activities during a typical working day. The technique serves to create empathy between researchers and the reality of the researched person. This allows for a deep understanding of the reality surrounding the problem that needs to be solved.\nThe technique allows you to gain an in-depth understanding of the user, seek a human-centric view and capture expert opinion.",
                "Um dia na vida pode ser definida como uma simulação realizada pelo pesquisador da vida do pesquisado, considerando as atividades realizadas e as situações vividas.\nTrata-se de um método de etnografia em que o pesquisador acompanha as atividades do usuário durante um típico dia de trabalho. A técnica serve para a criação de empatia dos pesquisadores com a realidade do pesquisado. Isso permite um entendimento profundo da realidade em torno do problema que precisa ser resolvido.\nA técnica permite obter um entendimento do usuário em profundidade, buscar uma visão centrada no humano e capturar opinião de experts."
                ],
                "howToUse": [
                "The technique is useful when seeking to understand the user's reality, needs and desires. It is a technique that should serve as a generator of insights for later stages.",
                "A técnica é útil para quando se busca o entendimento da realidade do usuário, das suas necessidades e desejos. É uma técnica que deve servir como geradora de insights para as fases posteriores. "
                ],
                "whenToUse": [
                "The project team members assume the role of the user and stay for a certain period of time, which varies according to what is intended to be understood. This role as a user will allow a different point of view not only of the problem, but also of the opportunities for solutions by having contact with the context and people with which he would be confronted on a daily basis.\nIt is important that professionals carry out assessments and studies of the context of the user to whom they will perform the technique, in order to learn about such behaviors, attitudes, limitations, and users' realities and experiences.",
                "Os membros da equipe de projeto assumem o papel do usuário e permanecem por um determinado período de tempo, o qual é variável de acordo com o que se pretende entender. Esta atuação como usuário permitirá um diferente ponto de vista não só do problema, mas das oportunidades de solução ao ter contato com o contexto e  as pessoas com os quais se estaria confrontado no dia a dia.\nÉ importante que os profissionais façam avaliações e estudos do contexto do usuário ao qual farão a técnica, para poder aprender sobre tais comportamentos, atitudes, limitações, e realidades e experiências dos usuários. "
                ],
                "image": "https://heliustool.github.io/helius-web/img/A_day_in_the_life_Helius.png",
                "projects": [
                "614de931b6e9380016773555",
                "614dead9b6e9380016773567",
                "61845f424476e3001671f962"
                ],
                "evaluate": [
                {
                    "user": "61250453ab505d0016d519ab",
                    "rate": 3,
                    "howWas": "Foi ok",
                    "howManyPeople": [
                    "Designer",
                    "Dev"
                    ],
                    "project": "614de931b6e9380016773555",
                    "techniques": [
                    "A day in the life",
                    "world_cafe"
                    ],
                    "recommend": True,
                    "date": "9/24/2021",
                    "countTechnique": 2
                },
                {
                    "user": "61250453ab505d0016d519ab",
                    "rate": 5,
                    "howWas": "ok",
                    "howManyPeople": [
                    "dev"
                    ],
                    "project": "614dead9b6e9380016773567",
                    "techniques": [
                    "A day in the life",
                    "brainstorming"
                    ],
                    "recommend": True,
                    "date": "9/24/2021",
                    "countTechnique": 3
                },
                {
                    "user": "6115a3db3397360015fb9fd8",
                    "rate": 4,
                    "howWas": "Teste",
                    "howManyPeople": [
                    "Lucas"
                    ],
                    "project": "61845f424476e3001671f962",
                    "techniques": [
                    "A day in the life"
                    ],
                    "recommend": True,
                    "date": "11/4/2021",
                    "countTechnique": 1
                }
                ]
            }
        }
class ErroMessage(BaseModel):
    message: str


class User(BaseModel):
    id: str = Field(..., alias='_id')
    # onBoard: str = None
    name: str = None
    email: str = None
    # password: str = None
    # function: str = None
    # startDT: str = None
    # formation: str = None
    # photo: str = None

def model_mapper(json_str):
    tech_dict = json.loads(json_str)
    # print(f"[model_mapper - tech_dict]: {tech_dict} \n")
    tech_list = [ Technique(**tech) for tech in tech_dict ]
    # print(f"[model_mapper - tech_list]: {tech_dict} \n")
    return tech_list















