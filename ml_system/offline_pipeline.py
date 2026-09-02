from simulation.events import (
    RatingEvent,
    WatchEvent,
    RecommendationClickedEvent,
)

from ml_system.features import (
    RatingFeatureComputer,
    ItemRatingFeatureComputer,
)


class OfflinePipeline:

    def __init__(
        self,
        feature_pipeline,
        dataset_generator,
        trainer,
        embedding_generator
    ):
        self.feature_pipeline = feature_pipeline
        self.dataset_generator = dataset_generator
        self.trainer = trainer
        self.embedding_generator = embedding_generator

    def run(self, events):

        self.feature_pipeline.process(events)

        for event in events:
            self.dataset_generator.add_event(event)

        training_data = (
            self.dataset_generator.build()
        )

        user_tower, item_tower = self.trainer.train(
            training_data
        )

        item_embeddings = (
            self.embedding_generator.generate(
                item_tower
            )
        )

        return {
            "user_tower": user_tower,
            "item_tower": item_tower,
            "item_embeddings": item_embeddings
        }


class OfflineFeaturePipeline:

    def __init__(self, movie_objects, feature_store):
        self.movie_objects = movie_objects
        self.feature_store = feature_store

        self.rating_features = RatingFeatureComputer()
        self.item_rating_features = ItemRatingFeatureComputer()


    def process(self, events):

        user_features = {}
        item_features = {}

        for event in events:

            if event.user_id not in user_features:
                user_features[event.user_id] = {
                    "genre_preferences": {},
                    "average_rating": 0,
                    "activity_level": 0,
                    "interactions": 0,
                    "watch_count": 0,
                    "user_click_counts": 0
                }

            user = user_features[event.user_id]


            if isinstance(event, RatingEvent):

                average_rating = self.rating_features.update(
                    event.user_id,
                    event.rating
                )

                user["average_rating"] = average_rating


            if hasattr(event, "movie_id"):

                movie = self.movie_objects[event.movie_id]

                if event.movie_id not in item_features:

                    item_features[event.movie_id] = {
                        "movie_id": event.movie_id,
                        "genres": movie.genres,
                        "average_rating": 0,
                        "popularity": 0,
                        "interactions": 0
                    }


                item = item_features[event.movie_id]

                item["interactions"] += 1

                user["interactions"] += 1
                user["activity_level"] = user["interactions"]


                if isinstance(event, WatchEvent):

                    user["watch_count"] += 1

                    item["popularity"] += 1


                    for genre in movie.genres:
                        user["genre_preferences"][genre] = (
                            user["genre_preferences"].get(genre, 0) + 1
                        )


                if isinstance(event, RecommendationClickedEvent):

                    user["user_click_counts"] += 1


                if isinstance(event, RatingEvent):

                    item_average_rating = (
                        self.item_rating_features.update(
                            event.movie_id,
                            event.rating
                        )
                    )

                    item["average_rating"] = item_average_rating


        for user_id, features in user_features.items():

            total = sum(
                features["genre_preferences"].values()
            )

            if total > 0:

                features["genre_preferences"] = {
                    genre: count / total
                    for genre, count in features["genre_preferences"].items()
                }


            self.feature_store.write_user_features(
                user_id,
                features
            )


        for movie_id, features in item_features.items():

            self.feature_store.write_item_features(
                movie_id,
                features
            )
