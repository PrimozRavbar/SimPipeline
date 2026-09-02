import torch
import torch.nn as nn


class TwoTowerTrainer:

    def __init__(
        self,
        user_tower,
        item_tower,
        learning_rate=0.001,
        epochs=5
    ):

        self.user_tower = user_tower
        self.item_tower = item_tower

        self.epochs = epochs

        self.optimizer = torch.optim.Adam(
            list(self.user_tower.parameters()) +
            list(self.item_tower.parameters()),
            lr=learning_rate
        )

        self.loss_fn = nn.BCEWithLogitsLoss()


    def train(self, training_data):

        self.user_tower.train()
        self.item_tower.train()

        for epoch in range(self.epochs):

            total_loss = 0

            for example in training_data:

                user_embedding = (
                    self.user_tower.encode(
                        example["user_features"]
                    )
                )

                item_embedding = (
                    self.item_tower.encode(
                        example["item_features"]
                    )
                )

                score = torch.dot(
                    user_embedding,
                    item_embedding
                )

                label = torch.tensor(
                    example["label"],
                    dtype=torch.float32
                )

                loss = self.loss_fn(
                    score,
                    label
                )

                self.optimizer.zero_grad()

                loss.backward()

                self.optimizer.step()

                total_loss += loss.item()


            print(
                "epoch:",
                epoch + 1,
                "loss:",
                total_loss / len(training_data)
            )


        return (
            self.user_tower,
            self.item_tower
        )


class EmbeddingGenerator:

    def __init__(self, feature_store):
        self.feature_store = feature_store

    def generate(self, item_tower):

        embeddings = {}

        for movie_id in self.feature_store.item_features:

            features = self.feature_store.get_item_features(
                movie_id
            )

            embeddings[movie_id] = (
                item_tower.embed(features)
            )

        return embeddings
