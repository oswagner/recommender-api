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
    
    
    def __get_df_techniques(self,):
        technique_df = pd.DataFrame(self.get_techniques())
        return technique_df
    
    def get_df_techniques(self):
        technique_df = pd.DataFrame(self.get_techniques())
        return technique_df
    
    def get_df_users(self):
        users_df = pd.DataFrame(self.__get_users())
        return users_df

    def get_df_ratings(self,):
        techniques = self.get_techniques()
        all_ratings = self.get_ratings_from_techniques(techniques)
        ratings_df = self.build_ratings_data_frame(all_ratings)
        return ratings_df

    def get_df_costs(self,):
        techniques = self.get_techniques()
        all_costs = self.get_costs_from_techniques(techniques)
        cost_df = self.build_cost_data_frame(all_costs)
        return cost_df

    def get_df_ratings_and_costs(self):
        df_ratings = self.get_df_ratings()
        df_costs = self.get_df_costs()
        df_costs_ratings = pd.merge(df_costs, df_ratings, on=['user_id', 'tech_name'], how='outer')
        return df_costs_ratings

    def get_low_cost(self):
        df_tech = self.get_df_techniques()
        df_costs_ratigns = self.get_df_ratings_and_costs()

        # get top 10 techs with low cost
        low_cost_sorted = df_costs_ratigns.sort_values('cost', ascending=True).head(10)
        
        tech_names = list(low_cost_sorted['tech_name'])
        # remove duplicates tech_names
        uniq_names = []
        for name in tech_names:
            if name not in uniq_names:
                uniq_names.append(name)

        # change name to category
        df_tech.name = df_tech.name.astype('category')
        df_tech.name.cat.set_categories(uniq_names, inplace=True)

        # get techs sorted by name
        sorted_techs = df_tech.sort_values('name')
        sorted_techs = sorted_techs.loc[sorted_techs['name'].isin(uniq_names)]

        json_value = sorted_techs.to_json(orient="records", default_handler = str)
        return json_value

    def get_best_cost_benefit(self):
        df_costs_ratigns = self.get_df_ratings_and_costs()
        cost = df_costs_ratigns['cost']
        rating = df_costs_ratigns['rating']
        # evaluate cost benefit
        cost_benefit = [(cost[i]/rating[i])  for i in range(len(cost))]
        df_costs_ratigns['cost_benefit'] = cost_benefit

        # sort top 10 by cost benefit
        sorted = df_costs_ratigns.sort_values('cost_benefit', ascending=False).head(10)

        tech_names = list(sorted['tech_name'])
        # remove duplicates tech_names
        uniq_names = []
        for name in tech_names:
            if name not in uniq_names:
                uniq_names.append(name)

        # change name to category
        df_tech.name = df_tech.name.astype('category')
        df_tech.name.cat.set_categories(uniq_names, inplace=True)

        # get techs sorted by name
        sorted_techs = df_tech.sort_values('name')
        sorted_techs = sorted_techs.loc[sorted_techs['name'].isin(uniq_names)]

        json_value = sorted_techs.to_json(orient="records", default_handler = str)
        return json_value

    
    def most_used_techniques(self):
        df_techniques = self.__get_df_techniques()
        most_used_technique = df_techniques.sort_values('count', ascending=False)
        return most_used_technique.to_json(orient="records", default_handler = str)
    
    def top_rated_techniques(self):
        df_techniques = self.__get_df_techniques()
        top_rated_technique = df_techniques.sort_values('rating',  ascending=False)
                
        return top_rated_technique.to_json(orient="records", default_handler = str)


    def all_techniques(self):
        df_techniques = self.__get_df_techniques()
        return df_techniques.to_json(orient="records", default_handler = str)
        

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
    
    def get_costs_from_techniques(self,techniques):
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

    def build_cost_data_frame(self, all_costs):
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
        if algo.trainset.knows_user(raw_user_id):
            raise ValueError(f"User {raw_user_id} is unknown")
        user_inner_id = algo.trainset.to_inner_uid(raw_user_id)
        neighbors = algo.get_neighbors(user_inner_id, k=5)
        neighbors_user_id = [algo.trainset.to_raw_uid(inner_id) for inner_id in neighbors]
        return neighbors_user_id

    def techinque_recommendations(self,ratings_df, neighbors_user_id, numer_of_recommendations=None):
        recommendations = []
        for user_id in neighbors_user_id:
            print(f"User id = [{user_id}]")
            ratings = ratings_df.loc[ratings_df['user_id'] == user_id]
            if numer_of_recommendations is None:
                list_tech_names = list(ratings['tech_name'])
                recommendations.extend(list_tech_names)
            else:
                top_n = ratings.sort_values('rating', ascending=False).head(numer_of_recommendations)
                list_tech_names = list(top_n['tech_name'])
                recommendations.extend(list_tech_names)

        recommendations = list(set(recommendations))
        df_tech = self.get_df_techniques()
        df_tech = df_tech.loc[df_tech['name'].isin(recommendations)]
        json_value = df_tech.to_json(orient="records", default_handler = str)
        return json_value

    def get_top_rated_and_used_by_experts(self,):
        df_ratings = self.get_df_ratings()
        df_users = self.get_df_users().astype({'startDT': 'int'})

        #sort by exeperts
        sorted = df_users.sort_values('startDT', ascending=True).head(10)
        top_users = sorted.to_dict('records')

        top_rated_and_used_by_expert = []
        for user in top_users:
            # list of techs used by user
            tech_names = [tech['technique'] for tech in user['useTechniques']]
            # list of techs rated by user
            rated_by_expert = df_ratings.loc[df_ratings['user_id'] == str(user['_id'])]
            # list of techs rated and used by expert
            rated_and_used_by_expert = rated_by_expert.loc[rated_by_expert['tech_name'].isin(tech_names)]
            # top 5 rated and used by expert
            top_5 = rated_and_used_by_expert.sort_values('rating', ascending=False).head(5)
            top_rated_and_used_by_expert.extend(list(top_5['tech_name']))

        # remove duplicates        
        uniq = list(set(top_rated_and_used_by_expert))
        # build response
        df_tech = self.get_df_techniques()
        df_tech = df_tech.loc[df_tech['name'].isin(uniq)]
        json_value = df_tech.to_json(orient="records", default_handler = str)
        return json_value

    def get_already_used_by_user(self, user_id):
        # unsure id is a string
        df_users = self.get_df_users().astype({'_id': 'str'})
        df_tech = self.get_df_techniques()
        # get user
        user = df_users[df_users['_id'] == str(user_id)]
        # get list of techs used by user
        tech_names = [tech['technique'] for tech in user['useTechniques'].tolist()[0]]
        # build response
        df_tech = df_tech.loc[df_tech['name'].isin(tech_names)]
        json_value = df_tech.to_json(orient="records", default_handler = str)
        return json_value

    def get_top_rated_and_used_by_user(self, user_id):
        df_users = self.get_df_users().astype({'_id': 'str'})
        df_tech = self.get_df_techniques()
        df_ratings = self.get_df_ratings()
        # get user
        user = df_users[df_users['_id'] == str(user_id)].to_dict('records')[0]
        # get list of techs used by user
        tech_names = [tech['technique'] for tech in user['useTechniques']]
        # get list of techs used and rated by user
        techs_used_and_rated = df_ratings.loc[df_ratings['tech_name'].isin(tech_names)]
        techs_used_and_rated_by_user = techs_used_and_rated.loc[techs_used_and_rated['user_id'] == str(user_id)]
        # sort by rating
        tech_names_rated = techs_used_and_rated_by_user.sort_values('rating', ascending=False)['tech_name']
        tech_names_sorted = tech_names_rated.to_list()
        # change name to category
        df_tech.name = df_tech.name.astype('category')
        df_tech.name.cat.set_categories(tech_names_sorted, inplace=True)
        # get techs sorted by name
        sorted_techs = df_tech.sort_values('name')
        sorted_techs = sorted_techs.loc[sorted_techs['name'].isin(tech_names_sorted)]
        
        json_value = sorted_techs.to_json(orient="records", default_handler = str)
        return json_value

    def get_used_by_similars_to_same_objective(self, user_id, objective):
        df_users = self.get_df_users().astype({'_id': 'str'})
        df_tech = self.get_df_techniques()
        df_ratings = self.get_df_ratings()
        algo = self.fit_knn(df_ratings)
        
        # get similar users
        neighbors_user_id = self.find_similar_users(algo, user_id)

        techs_used_by_similars_for_same_objective = []
        for similar_user in neighbors_user_id:
            # similar_user = neighbors_user_id[0]
            user = df_users[df_users['_id'] == str(similar_user)]
            # get list of techs used by similar user
            tech_names = [tech['technique'] for tech in user['useTechniques'].tolist()[0]]
            # get techs used by similar user
            tech_used_by_similar = df_tech.loc[df_tech['name'].isin(tech_names)]
            tech_dict = tech_used_by_similar.to_dict('records')
            # get techs used by similar user for specific objective
            for tech in tech_dict:
                if objective in tech['objective']:
                    techs_used_by_similars_for_same_objective.append(tech['name'])

        # remove duplicates
        techs_used_by_similars_for_same_objective = list(set(techs_used_by_similars_for_same_objective))
        # build response
        selected_techs = df_tech.loc[df_tech['name'].isin(techs_used_by_similars_for_same_objective)]
        json_value = selected_techs.to_json(orient="records", default_handler = str)
        return json_value

    def get_top_rated_and_used_by_experts_to_same_objective(self, objective):
        df_tech = self.get_df_techniques()
        df_ratings = self.get_df_ratings()
        df_users = self.get_df_users().astype({'startDT': 'int'})
        # objective = "Validating ideas"

        #sort users by exeperts
        sorted = df_users.sort_values('startDT', ascending=True).head(10)
        top_users = sorted.to_dict('records')

        tech_top_rated_and_used_by_expert = []
        for user in top_users:
            # list of techs used by top user
            tech_names = [tech['technique'] for tech in user['useTechniques']]
            # list of techs rated by user
            rated_by_expert = df_ratings.loc[df_ratings['user_id'] == str(user['_id'])]
            # list of techs rated and used by expert
            rated_and_used_by_expert = rated_by_expert.loc[rated_by_expert['tech_name'].isin(tech_names)]
            # top 5 rated and used by expert
            top_5 = rated_and_used_by_expert.sort_values('rating', ascending=False).head(5)
            tech_top_rated_and_used_by_expert.extend(list(top_5['tech_name']))

        # remove duplicates        
        uniq = list(set(tech_top_rated_and_used_by_expert))

        # get top rated techs used by experts for specific objective
        selected_top_rated = df_tech.loc[df_tech['name'].isin(uniq)]
        tech_dict = selected_top_rated.to_dict('records')
        techs_used_by_experts_for_same_objective = []
        for tech in tech_dict:
            if objective in tech['objective']:
                techs_used_by_experts_for_same_objective.append(tech['name'])

        # remove duplicates
        uniq = list(set(techs_used_by_experts_for_same_objective))
        
        # build response
        selected_tech_used_by_experts_for_same_objective = df_tech.loc[df_tech['name'].isin(uniq)]
        json_value = selected_tech_used_by_experts_for_same_objective.to_json(orient="records", default_handler = str)
        return json_value

    def get_top_rated_to_same_objective(self, objective):
        df_tech = self.get_df_techniques()
        df_ratings = self.get_df_ratings()
        # objective = "Validating ideas"

        # get top techs by users for specific objective
        tech_dict = df_tech.to_dict('records')
        techs_used_for_same_objective = []
        for tech in tech_dict:
            if objective in tech['objective']:
                techs_used_for_same_objective.append(tech['name'])


        # get top 10 techs by users for specific objective
        selected_techs_for_objective = df_ratings.loc[df_ratings['tech_name'].isin(techs_used_for_same_objective)]
        top_rated = selected_techs_for_objective.sort_values('rating', ascending=False).head(10)

        # get tech_name list
        names = top_rated['tech_name']

        # remove duplicates tech_names
        uniq_names = []
        for name in names:
            if name not in uniq_names:
                uniq_names.append(name)

        # change name to category
        df_tech.name = df_tech.name.astype('category')
        df_tech.name.cat.set_categories(uniq_names, inplace=True)

        # get techs sorted by name
        sorted_techs = df_tech.sort_values('name')
        sorted_techs = sorted_techs.loc[sorted_techs['name'].isin(uniq_names)]

        json_value = sorted_techs.to_json(orient="records", default_handler = str)
        return json_value

    def get_top_rated_for_same_workspace(self, workspace):
        df_tech = self.get_df_techniques()
        df_ratings = self.get_df_ratings()
        # all_workspace = ['Inspiration', 'Ideation', 'Implementation', 'Problem space', 'Solution space']

        techs = df_tech.to_dict('records')
        techs_for_same_workspace = []
        for tech in techs:
            models = tech['models']
            labels = list(np.array([model['label'] for model in models]).flatten())
            if len([w for w in workspace if w in labels])>0:
                techs_for_same_workspace.append(tech['name'])

        # get top 10 techs by workspace
        selected = df_ratings.loc[df_ratings['tech_name'].isin(techs_for_same_workspace)]
        top_10 = selected.sort_values('rating', ascending=False).head(10)

        # remove duplicates tech_names
        names = list(top_10['tech_name'])
        uniq_names = []
        for name in names:
            if name not in uniq_names:
                uniq_names.append(name)

        # change name to category
        df_tech.name = df_tech.name.astype('category')
        df_tech.name.cat.set_categories(uniq_names, inplace=True)

        # get techs sorted by name
        sorted_techs = df_tech.sort_values('name')
        sorted_techs = sorted_techs.loc[sorted_techs['name'].isin(uniq_names)]

        sorted_techs
        json_value = sorted_techs.to_json(orient="records", default_handler = str)
        return json_value

    def get_top_rated_by_user_for_same_objective(self, user_id, objective):
        # unsure id is a string
        df_users = self.get_df_users().astype({'_id': 'str'})
        df_tech = self.get_df_techniques()
        df_ratings = self.get_df_ratings()

        # get user
        user = df_users[df_users['_id'] == str(user_id)]
        # get list of techs used by user
        tech_names = [tech['technique'] for tech in user['useTechniques'].tolist()[0]]
        selected = df_tech.loc[df_tech['name'].isin(tech_names)]
        tech_dict = selected.to_dict('records')

        # get techs by user for specific objective
        techs_used_by_user_for_same_objective = []
        for tech in tech_dict:
            if objective in tech['objective']:
                techs_used_by_user_for_same_objective.append(tech['name'])

        # get list of techs used and rated by user
        techs_used_and_rated = df_ratings.loc[df_ratings['tech_name'].isin(techs_used_by_user_for_same_objective
        )]
        techs_used_and_rated_by_user = techs_used_and_rated.loc[techs_used_and_rated['user_id'] == str(user_id)]
        # sort by rating
        tech_names_rated = techs_used_and_rated_by_user.sort_values('rating', ascending=False)['tech_name']
        tech_names_sorted = tech_names_rated.to_list()
        # change name to category
        df_tech.name = df_tech.name.astype('category')
        df_tech.name.cat.set_categories(tech_names_sorted, inplace=True)
        # get techs sorted by name
        sorted_techs = df_tech.sort_values('name')
        sorted_techs = sorted_techs.loc[sorted_techs['name'].isin(tech_names_sorted)]

        json_value = sorted_techs.to_json(orient="records", default_handler = str)
        return json_value

    def get_average_rated_by_experts(self):
        df_users = self.get_df_users().astype({'startDT': 'int'})
        df_tech = self.get_df_techniques()
        df_ratings = self.get_df_ratings()

        # sort by exeperts
        experts_users = df_users.sort_values('startDT', ascending=True).head(10)
        # get list of experts ids
        experts_id = [str(user['_id']) for user in experts_users.to_dict('records')]
        # get ratings by experts
        experts_rating = df_ratings.loc[df_ratings['user_id'].isin(experts_id)]
        # get ratings equals to 3
        rated_eq3 = experts_rating.loc[np.round(experts_rating['rating'],2) == 3.00]
        # df_ratings
        tech_names = list(rated_eq3['tech_name'])

        techs = df_tech.loc[df_tech['name'].isin(tech_names)]
        json_value = techs.to_json(orient="records", default_handler = str)
        
        return json_value
