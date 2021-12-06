import pandas as pd
import numpy as np
from pymongo import MongoClient
from database_reader.database_interface import DatabaseInterface

class DatabaseReaderMongo(DatabaseInterface):
    # helius Oficial DB
    __auth_db_info = dict(user="wagner", 
                          password="ODDtF8nsrOQOSVS8", 
                          db_name="helius", 
                          cluster="cluster0.kooo9.mongodb.net")
    
    # local db
    # connectionStr = "mongodb://127.0.0.1:27017/?readPreference=primary&serverSelectionTimeoutMS=2000&directConnection=true&ssl=false"
    
    connectionStr = "mongodb+srv://{user}:{password}@{cluster}/{db_name}?retryWrites=true&w=majority".format(**__auth_db_info)
    
    client = MongoClient(connectionStr)
    
    def __init__(self):
        self.db = self.client[self.__auth_db_info['db_name']]

    def __get_users(self):
        users = self.db.users.find()
        return list(users)

    def __get_techniques(self):
        techniques = self.db.techniques.find()
        return list(techniques)
    
    def get_df_techniques(self):
        technique_df = pd.DataFrame(self.__get_techniques())
        return technique_df
    
    def get_df_users(self):
        users_df = pd.DataFrame(self.__get_users())
        return users_df
    
    def get_df_ratings(self):
        techniques = self.__get_techniques()
        all_ratings = self.__get_ratings_from_techniques(techniques)
        ratings_df = self.__build_ratings_data_frame(all_ratings)
        return ratings_df
    
    def get_df_costs(self):
        techniques = self.__get_techniques()
        all_costs = self.__get_costs_from_techniques(techniques)
        cost_df = self.__build_cost_data_frame(all_costs)
        return cost_df
    
    def get_df_ratings_and_costs(self):
        df_ratings = self.get_df_ratings()
        df_costs = self.get_df_costs()
        df_costs_ratings = pd.merge(df_costs, df_ratings, on=['user_id', 'tech_name'], how='outer')
        return df_costs_ratings

    def __get_ratings_from_techniques(self,techniques):
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

    def __build_ratings_data_frame(self, all_ratings):
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

    def __get_costs_from_techniques(self,techniques):
        all_costs = []
        for tech in techniques:
            # print(f"Tech name = [{tech['name']}]")
            unique_cost_per_user = {}
            evaluate = tech['evaluate']
            for i in range(len(evaluate)):
                left_user_id = evaluate[i]['user']
                if left_user_id not in unique_cost_per_user:
                    unique_cost_per_user[left_user_id] = [evaluate[i]['cost']]
                    for j in range(i+1, len(evaluate)):
                        right_user_id = evaluate[j]['user']
                        if left_user_id == right_user_id:
                            unique_cost_per_user[left_user_id].append(evaluate[j]['cost'])

            unique_cost_per_user = {k: np.mean(v) for k, v in unique_cost_per_user.items()}

            all_costs.append({'tech_name':tech['name'],'cost':unique_cost_per_user})
        return all_costs

    def __build_cost_data_frame(self, all_costs):
        all_users = []
        all_techs = []
        all_cost = []
        for cost in all_costs:
            users = [k for k in cost['cost']]
            values = [v for v in cost['cost'].values()]
            tech_names = [ ]
            for _ in range(len(users)):
                tech_names.append(cost['tech_name'])
            all_users.extend(users)
            all_cost.extend(values)
            all_techs.extend(tech_names)

        data_frame_structure = {'user_id': all_users, 'tech_name': all_techs, 'cost': all_cost}
        cost_df = pd.DataFrame(data_frame_structure)
        return cost_df