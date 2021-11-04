# %%
import pandas as pd
import numpy as np
from pymongo import MongoClient
from surprise import KNNBaseline
from surprise import Dataset
from surprise import Reader

class DataHandler:
    
    # helius mock DB
    # __auth_db_info = dict(user="wagner",
    #                       password="1a2b3c", 
    #                       db_name="<dbname>",
    #                       cluster="cluster0.h7dwe.gcp.mongodb.net")
    
    # helius Oficial DB
    __auth_db_info = dict(user="wagner", 
                          password="ODDtF8nsrOQOSVS8", 
                          db_name="helius", 
                          cluster="cluster0.kooo9.mongodb.net")
    
    # local db
    # connectionStr = "mongodb://127.0.0.1:27017/?readPreference=primary&serverSelectionTimeoutMS=2000&directConnection=true&ssl=false"
    
    connectionStr = "mongodb+srv://{user}:{password}@{cluster}/{db_name}?retryWrites=true&w=majority".format(**__auth_db_info)
    
    client = MongoClient(connectionStr)
    
    def __init__(self) -> None:
     self.db = self.client[self.__auth_db_info['db_name']]
    
    def __get_users(self):
        users = self.db.users.find()
        return list(users)
        
    def get_techniques(self):
        techniques = self.db.techniques.find()
        return list(techniques)
    
    
    def __get_df_techniques(self, 
                            columns=
                            ['_id', 'nameT', 'description', 
                             'howToUse', 'whenToUse', 'projects',
                             'name', 'rating', 'count', 'image', 
                             'evaluate', '__v']):
        technique_df = pd.DataFrame(self.get_techniques())
        selected_colum_data = technique_df.loc[:,columns]
        return selected_colum_data
    
    def get_df_techniques(self):
        technique_df = pd.DataFrame(self.get_techniques())
        return technique_df
    
    def get_df_users(self):
        users_df = pd.DataFrame(self.__get_users())
        return users_df
     
    
    def most_used_techniques(self, as_json=False):
        df_techniques = self.__get_df_techniques(['_id','name', 'nameT','count'])
        most_used_technique = df_techniques.sort_values('count', ascending=False)
        # generate data csv
        # most_used_technique.to_csv("most_used_technique.csv", sep=',', encoding='utf-8')

        # generate data html 
        # most_used_technique.to_html("sample.html")

        # generate data json
        # most_used_technique.to_json("sample.json", orient="records", default_handler = str)
        
        if as_json:
            return most_used_technique.to_json(orient="records", default_handler = str)
        else:
            return most_used_technique
    
    def top_rated_techniques(self, as_json=False):
        df_techniques = self.__get_df_techniques(['_id', 'name', 'nameT', 'rating'])
        top_rated_technique = df_techniques.sort_values('rating',  ascending=False)
        
        if as_json:
          return top_rated_technique.to_json(orient="records", default_handler = str)
        else:
            return top_rated_technique

    def get_ratings_from_techniques(self,techniques):
        all_ratings = []
        for tech in techniques:
            # print(f"Tech name = [{tech['name']}]")
            unique_rate_per_user = {}
            ratings = tech['evaluate']
            for i in range(len(ratings)):
                left_user_id = ratings[i]['user']
                if left_user_id not in unique_rate_per_user:
                    unique_rate_per_user[left_user_id] = [ratings[i]['rate']]
                    for j in range(i+1, len(ratings)):
                        right_user_id = ratings[j]['user']
                        if left_user_id == right_user_id:
                            unique_rate_per_user[left_user_id].append(ratings[j]['rate'])

            unique_rate_per_user = {k: np.mean(v) for k, v in unique_rate_per_user.items()}

            all_ratings.append({'tech_name':tech['name'],'rates':unique_rate_per_user})
        return all_ratings

    def build_ratings_data_frame(self, all_ratings):
        all_users = []
        all_rates = []
        all_techs = []
        for rating in all_ratings:
            users = [k for k in rating['rates']]
            values = [v for v in rating['rates'].values()]
            tech_names = [ ]
            for _ in range(len(users)):
                tech_names.append(rating['tech_name'])
            all_users.extend(users)
            all_rates.extend(values)
            all_techs.extend(tech_names)
        
        data_frame_structure = {'user_id': all_users, 'tech_name': all_techs, 'rating': all_rates}
        ratings_df = pd.DataFrame(data_frame_structure)
        return ratings_df

    def fit_knn(self, ratings_df):
        reader = Reader(rating_scale=(1.0, 5.0))
        data = Dataset.load_from_df(ratings_df[['user_id', 'tech_name', 'rating']], reader)
        trainset = data.build_full_trainset()
        algo = KNNBaseline(k=5, sim_options={'name': 'pearson', 'user_based': True})
        algo.fit(trainset)
        return algo
    
    def find_similar_users(self, algo, raw_user_id):
        # if algo.trainset.knows_user(raw_user_id):
        #     raise ValueError(f"User {raw_user_id} is unknown")
        user_inner_id = algo.trainset.to_inner_uid(raw_user_id)
        neighbors = algo.get_neighbors(user_inner_id, k=5)
        neighbors_user_id = [algo.trainset.to_raw_uid(inner_id) for inner_id in neighbors]
        return neighbors_user_id

    def techinque_recommendations(self,ratings_df, neighbors_user_id):
        recommendations = []
        for user_id in neighbors_user_id:
            print(f"User id = [{user_id}]")
            ratings = ratings_df.loc[ratings_df['user_id'] == user_id]
            top_five = ratings.sort_values('rating', ascending=False).head(5)
            list_tech_names = list(top_five['tech_name'])
            recommendations.extend(list_tech_names)

        recommendations = list(set(recommendations))
        df_tech = self.get_df_techniques()
        df_tech = df_tech.loc[df_tech['name'].isin(recommendations)]
        json_value = df_tech[['_id','name', 'nameT']].to_json(orient="records", default_handler = str)
        return json_value
# %%

# data_handler = DataHandler()
# techniques = data_handler.get_techniques()
# all_ratings = data_handler.get_ratings_from_techniques(techniques)
# ratings_df = data_handler.build_ratings_data_frame(all_ratings)
# algo = data_handler.fit_knn(ratings_df)
# raw_user_id = '617f1b4ef0a90c7c757926ba'
# # raw_user_id = '617f1b4ef0a90c7c7579269e'
# neighbors_user_id = data_handler.find_similar_users(algo, raw_user_id)
# recommendations = data_handler.techinque_recommendations(ratings_df, neighbors_user_id)
# recommendations