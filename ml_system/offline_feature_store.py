from simulation.service import Service

class OfflineFeatureStore(Service):

    def __init__(self):
        super().__init__()

        self.name = "OfflineFeatureStore"

        self.user_features = {}
        self.item_features = {}

    def write_user_features(self, user_id, features):

        self.user_features[user_id] = features


    def write_item_features(self, movie_id, features):

        self.item_features[movie_id] = features


    def get_user_features(self, user_id):

        return self.user_features.get(
            user_id
        )


    def get_item_features(self, movie_id):

        return self.item_features.get(
            movie_id
        )