import torch
import torch.nn as nn
import torch.nn.functional as F


class TwoTowerTrainer:

    def __init__(
        self,
        user_tower,
        item_tower,
        learning_rate=0.001,
        epochs=5,
        temperature=0.1
    ):

        self.user_tower = user_tower
        self.item_tower = item_tower

        self.epochs = epochs
        self.temperature = temperature

        self.optimizer = torch.optim.Adam(
            list(self.user_tower.parameters()) +
            list(self.item_tower.parameters()),
            lr=learning_rate
        )


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

                positive_embedding = (
                    self.item_tower.encode(
                        example["positive_item_features"]
                    )
                )

                negative_embeddings = [
                    self.item_tower.encode(features)
                    for features in example["negative_item_features"]
                ]

                positive_score = torch.dot(
                    user_embedding,
                    positive_embedding
                )

                negative_scores = torch.stack([
                    torch.dot(
                        user_embedding,
                        negative_embedding
                    )
                    for negative_embedding in negative_embeddings
                ])

                scores = torch.cat([
                    positive_score.unsqueeze(0),
                    negative_scores
                ])

                logits = scores / self.temperature

                target = torch.tensor(
                    0,
                    dtype=torch.long
                )

                loss = F.cross_entropy(
                    logits.unsqueeze(0),
                    target.unsqueeze(0)
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
