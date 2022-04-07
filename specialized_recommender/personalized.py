from surprise import KNNBaseline
from surprise import Dataset
from surprise import Reader
from database_reader.database_reader_mongo import DatabaseInterface

class PesonalizedRecommender:

  def __init__(self, db_reader: DatabaseInterface):
      self.db = db_reader

  def __fit_knn(self, ratings_df):
      reader = Reader(rating_scale=(1.0, 5.0))
      data = Dataset.load_from_df(ratings_df[['user_id', 'tech_name', 'rating']], reader)
      trainset = data.build_full_trainset()
      algo = KNNBaseline(k=5, sim_options={'name': 'pearson', 'user_based': True})
      algo.fit(trainset)
      return algo

  def __find_similar_users(self, algo, raw_user_id):
        if algo.trainset.knows_user(raw_user_id):
            raise ValueError(f"User {raw_user_id} is unknown")
        user_inner_id = algo.trainset.to_inner_uid(raw_user_id)
        neighbors = algo.get_neighbors(user_inner_id, k=5)
        neighbors_user_id = [algo.trainset.to_raw_uid(inner_id) for inner_id in neighbors]
        return neighbors_user_id


  def get_similar_users(self, user_id):
      print(f'User that wants a recommendation id = [{user_id}]')
      ratings_df = self.db.get_df_ratings()
      algo = self.__fit_knn(ratings_df)
      neighbors_user_id = self.__find_similar_users(algo, user_id)

      print(f"Similar Users id = [{neighbors_user_id}]")
      
      df_users = self.db.get_df_users().astype({'_id': 'str'})
      
      df_users = df_users.loc[df_users['_id'].isin(neighbors_user_id)]
      json_value = df_users.to_json(orient="records", default_handler = str)
      return json_value
  

  def get_rated_by_similar_users(self, user_id, numer_of_recommendations = None):
        print(f'User that wants a recommendation id = [{user_id}]')
        ratings_df = self.db.get_df_ratings()
        algo = self.__fit_knn(ratings_df)
        neighbors_user_id = self.__find_similar_users(algo, user_id)

        recommendations = []
        for user_id in neighbors_user_id:
            print(f"Similar Users id = [{user_id}]")
            ratings = ratings_df.loc[ratings_df['user_id'] == user_id]
            if numer_of_recommendations is None:
                list_tech_names = list(ratings['tech_name'])
                recommendations.extend(list_tech_names)
            else:
                top_n = ratings.sort_values('rating', ascending=False).head(numer_of_recommendations)
                list_tech_names = list(top_n['tech_name'])
                recommendations.extend(list_tech_names)

        recommendations = list(set(recommendations))
        print(f"Techniques used by similar users = [{recommendations}]")
        df_tech = self.db.get_df_techniques()
        df_tech = df_tech.loc[df_tech['name'].isin(recommendations)]
        print(f"Techniques recommended = [{list(df_tech['name'])}]")
        json_value = df_tech.to_json(orient="records", default_handler = str)
        return json_value

  def get_used_by_similars_to_same_objective(self, user_id, objective):
    df_users = self.db.get_df_users().astype({'_id': 'str'})
    df_tech = self.db.get_df_techniques()
    df_ratings = self.db.get_df_ratings()
    algo = self.__fit_knn(df_ratings)
    
    # get similar users
    neighbors_user_id = self.__find_similar_users(algo, user_id)

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

  def get_already_used_by_user(self, user_id):
    # unsure id is a string
    df_users = self.db.get_df_users().astype({'_id': 'str'})
    df_tech = self.db.get_df_techniques()
    # get user
    user = df_users[df_users['_id'] == str(user_id)]
    # get list of techs used by user
    tech_names = [tech['technique'] for tech in user['useTechniques'].tolist()[0]]
    # build response
    df_tech = df_tech.loc[df_tech['name'].isin(tech_names)]
    json_value = df_tech.to_json(orient="records", default_handler = str)
    return json_value

  def get_top_rated_and_used_by_user(self, user_id):
    df_users = self.db.get_df_users().astype({'_id': 'str'})
    df_tech = self.db.get_df_techniques()
    df_ratings = self.db.get_df_ratings()
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

  def get_top_rated_by_user_for_same_objective(self, user_id, objective):
    # unsure id is a string
    df_users = self.db.get_df_users().astype({'_id': 'str'})
    df_tech = self.db.get_df_techniques()
    df_ratings = self.db.get_df_ratings()

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