# %%
import collections
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from pymongo import MongoClient

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
    
    
    connectionStr = "mongodb+srv://{user}:{password}@{cluster}/{db_name}?retryWrites=true&w=majority".format(**__auth_db_info)
    client = MongoClient(connectionStr)
    
    def __init__(self) -> None:
     self.db = self.client[self.__auth_db_info['db_name']]
    
    def __get_users(self):
        users = self.db.users.find()
        return list(users)
        
    def __get_techniques(self):
        techniques = self.db.techniques.find()
        return list(techniques)
    
    def get_tech_user_rate(self):
        
        pipeline = [
            { "$unwind" : "$evaluate" },
            {"$project": {
                "_id":1,
                "name":1, 
                "count":1, 
                "evaluate.user":1,
                "evaluate.rate":1,
            }},
            { "$replaceRoot": { "newRoot": {
                "technique_id": "$_id",
                # "name":"$name",
                # "count":"$count",
                "user_id": "$evaluate.user",
                "rate": "$evaluate.rate"
            }}},
        ]
        
        values = self.db.techniques.aggregate(pipeline)
        return list(values)
    
    def get_df_tech_user_rate(self):
        tech_user_rate_df = pd.DataFrame(self.__get_tech_user_rate())
        return tech_user_rate_df
    
    def __get_df_techniques(self, 
                            columns=
                            ['_id', 'nameT', 'description', 
                             'howToUse', 'whenToUse', 'projects',
                             'name', 'rating', 'count', 'image', 
                             'evaluate', '__v']):
        technique_df = pd.DataFrame(self.__get_techniques())
        selected_colum_data = technique_df.loc[:,columns]
        return selected_colum_data
    
    def get_df_techniques(self):
        technique_df = pd.DataFrame(self.__get_techniques())
        return technique_df
    
    def get_df_users(self):
        users_df = pd.DataFrame(self.__get_users())
        return users_df
     
    
    def most_used_techniques(self, as_json=False):
        df_techniques = self.__get_df_techniques(['_id','name','count'])
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
        df_techniques = self.__get_df_techniques(['_id', 'name', 'rating'])
        top_rated_technique = df_techniques.sort_values('rating',  ascending=False)
        
        if as_json:
          return top_rated_technique.to_json(orient="records", default_handler = str)
        else:
            return top_rated_technique

    def get_df_ratings(self, size=200):
        techniques = self.get_df_techniques()
        tech_id = list(map(lambda x: str(x), techniques['_id']))
        sample = []
        for i in range(size):
            sample.append({
                'user_id':np.random.randint(low=1, high=size),
                'tech_id':tech_id[np.random.randint(0,(len(tech_id)-1))],
                'rating':np.random.uniform(low=1, high=5)
            })
            
        return pd.DataFrame(sample)
     
# %%

# data = DataHandler()

# # df_techniques = data.get_df_techniques()
# df_ratings = data.get_df_ratings(size=1000)

# df_ratings.head()

# df = df_ratings.groupby(['tech_id', 'user_id'], as_index=False).agg({'rating': 'mean'})

# df.head()



# rating_pivot = df.pivot(index='user_id', columns = 'tech_id', values='rating').fillna(0)
# # rating_pivot.shape

# user_tech_ratings_matrix = csr_matrix(rating_pivot.values)

# model_knn = NearestNeighbors(metric='cosine', algorithm='brute')
# model_knn.fit(user_tech_ratings_matrix)


# query_index = np.random.choice(rating_pivot.shape[0]) # random user change by user id

# distances, indices = model_knn.kneighbors(rating_pivot.iloc[query_index, :].values.reshape(1, -1), n_neighbors = 6)

# flatt_distances = distances.flatten()
# flatt_indices = indices.flatten()

# # all technique ratings by the user
# all_rated = collections.defaultdict(dict)
# for i in df_ratings.values.tolist():
#     all_rated[i[0]][i[1]] = i[2]

# neighbours_rated = {}
# for i in range(0, len(flatt_distances)):
#     if i == 0:
#         print('Closest users to user {0} \n'.format(rating_pivot.index[query_index]))
#     else:
#         print('{0}: {1} - distance: {2}'.format(i, rating_pivot.index[flatt_indices[i]], flatt_distances[i]))

#     neighbours_rated[rating_pivot.index[flatt_indices[i]]] = all_rated[rating_pivot.index[flatt_indices[i]]].copy()

#     for user_id, rating in neighbours_rated[rating_pivot.index[flatt_indices[i]]].items():
#         neighbours_rated[rating_pivot.index[flatt_indices[i]]][user_id] = [1 - flatt_distances[i], rating]

# print('\n')
# # {user_id: {tech_id: [distance, rating]}}
# neighbours_rated