import numpy as np
from database_reader.database_reader_mongo import DatabaseInterface


class NonPesonalizedRecommender:

  def __init__(self, db_reader: DatabaseInterface):
    self.db = db_reader

  def get_all_techniques(self):
    df_techniques = self.db.get_df_techniques()
    return df_techniques.to_json(orient="records", default_handler = str)

  def get_most_used_techniques(self):
    df_techniques = self.db.get_df_techniques()
    most_used_technique = df_techniques.sort_values('count', ascending=False)
    return most_used_technique.to_json(orient="records", default_handler = str)

  def get_top_rated_techniques(self):
    df_techniques = self.db.get_df_techniques()
    top_rated_technique = df_techniques.sort_values('rating',  ascending=False)
    return top_rated_technique.to_json(orient="records", default_handler = str)

  def get_top_rated_and_used_by_experts(self):
    df_ratings = self.db.get_df_ratings()
    df_users = self.db.get_df_users().astype({'startDT': 'int'})

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
    df_tech = self.db.get_df_techniques()
    df_tech = df_tech.loc[df_tech['name'].isin(uniq)]
    json_value = df_tech.to_json(orient="records", default_handler = str)
    return json_value

  def get_average_rated_by_experts(self):
    df_users = self.db.get_df_users().astype({'startDT': 'int'})
    df_tech = self.db.get_df_techniques()
    df_ratings = self.db.get_df_ratings()

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

  def get_low_cost(self):
    df_tech = self.db.get_df_techniques()
    df_costs_ratigns = self.db.get_df_ratings_and_costs()

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
    df_tech = self.db.get_df_techniques()
    df_costs_ratigns = self.db.get_df_ratings_and_costs()
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

  def get_top_rated_and_used_by_experts_to_same_objective(self, objective):
    df_tech = self.db.get_df_techniques()
    df_ratings = self.db.get_df_ratings()
    df_users = self.db.get_df_users().astype({'startDT': 'int'})
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
    df_tech = self.db.get_df_techniques()
    df_ratings = self.db.get_df_ratings()
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
    df_tech = self.db.get_df_techniques()
    df_ratings = self.db.get_df_ratings()
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