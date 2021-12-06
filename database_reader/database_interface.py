from abc import ABC, abstractmethod

class DatabaseInterface(ABC):
    
    @abstractmethod
    def get_df_techniques(self):
        pass
    @abstractmethod
    def get_df_users(self):
        pass
    @abstractmethod
    def get_df_ratings(self,):
        pass
    @abstractmethod
    def get_df_costs(self,):
        pass
    @abstractmethod
    def get_df_ratings_and_costs(self):
        pass