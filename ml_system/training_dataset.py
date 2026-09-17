import random

from simulation.events import (
    RecommendationClickedEvent,
    WatchEvent,
)


class TrainingDatasetGenerator:

    def __init__(
        self,
        feature_store,
        negative_samples=5
    ):
        self.feature_store = feature_store
        self.interactions = []
        self.user_movies = {}
        self.negative_samples = negative_samples


    def add_event(self, event, event_order):

        if isinstance(event, RecommendationClickedEvent):

            self.interactions.append({
                "user_id": event.user_id,
                "movie_id": event.movie_id,
                "label": 1,
                "timestamp": event.timestamp,
                "event_order": event_order
            })

            self.user_movies.setdefault(
                event.user_id,
                set()
            ).add(event.movie_id)


        elif isinstance(event, WatchEvent):

            self.interactions.append({
                "user_id": event.user_id,
                "movie_id": event.movie_id,
                "label": 1,
                "timestamp": event.timestamp,
                "event_order": event_order
            })

            self.user_movies.setdefault(
                event.user_id,
                set()
            ).add(event.movie_id)


    def add_negative_samples(self):

        all_movies = list(
            self.feature_store.item_features.keys()
        )

        negatives = []

        for interaction in self.interactions:

            user_id = interaction["user_id"]

            seen_movies = self.user_movies.get(
                user_id,
                set()
            )

            candidates = [
                movie_id
                for movie_id in all_movies
                if movie_id not in seen_movies
            ]

            for _ in range(self.negative_samples):

                if candidates:

                    negative_movie = random.choice(
                        candidates
                    )

                    negatives.append({
                        "user_id": user_id,
                        "movie_id": negative_movie,
                        "label": 0,
                        "timestamp": interaction["timestamp"],
                        "event_order": interaction["event_order"]
                    })

        self.interactions.extend(
            negatives
        )


    def build(self):

        self.add_negative_samples()

        random.shuffle(self.interactions)

        dataset = []

        for interaction in self.interactions:

            user_features = (
                self.feature_store.get_user_features_as_of(
                    interaction["user_id"],
                    interaction["timestamp"],
                    interaction["event_order"]
                )
            )

            item_features = (
                self.feature_store.get_item_features_as_of(
                    interaction["movie_id"],
                    interaction["timestamp"],
                    interaction["event_order"]
                )
            )

            dataset.append({
                "user_features": user_features,
                "item_features": item_features,
                "label": interaction["label"]
            })

        self.interactions = []
        self.user_movies = {}

        return dataset
