import random

from simulation.events import (
    RecommendationShownEvent,
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
        self.shown_recommendations = {}
        self.negative_samples = negative_samples


    def add_event(self, event, event_order):

        if isinstance(event, RecommendationShownEvent):

            self.shown_recommendations[
                event.recommendation_id
            ] = event

        elif isinstance(event, RecommendationClickedEvent):

            self.interactions.append({
                "user_id": event.user_id,
                "movie_id": event.movie_id,
                "label": 1,
                "timestamp": event.timestamp,
                "event_order": event_order
            })

            shown = self.shown_recommendations.get(
                event.recommendation_id
            )

            if shown is not None:

                candidates = [
                    movie_id
                    for movie_id in shown.movie_ids
                    if movie_id != event.movie_id
                ]

                sampled_negatives = random.sample(
                    candidates,
                    min(
                        self.negative_samples,
                        len(candidates)
                    )
                )

                for movie_id in sampled_negatives:

                    self.interactions.append({
                        "user_id": event.user_id,
                        "movie_id": movie_id,
                        "label": 0,
                        "timestamp": event.timestamp,
                        "event_order": event_order
                    })

        elif isinstance(event, WatchEvent):

            self.interactions.append({
                "user_id": event.user_id,
                "movie_id": event.movie_id,
                "label": 1,
                "timestamp": event.timestamp,
                "event_order": event_order
            })


    def build(self):

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
        self.shown_recommendations = {}

        return dataset
