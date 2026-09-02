def test_online_offline_feature_parity(system):
    offline_pipeline = system["offline_pipeline"]

    flink = system["sim"].get_service("Flink")
    redis = system["redis"]
    feature_store = offline_pipeline.feature_pipeline.feature_store

    # USER average_rating
    user_id = next(iter(flink.rating_features.rating_sum))
    assert (
        redis.get("average_rating", user_id)
        == feature_store.user_features[user_id]["average_rating"]
    )

    # USER genre_preferences
    user_id = next(iter(flink.state["genre_counts"]))
    assert (
        redis.get("genre_preferences", user_id)
        == feature_store.user_features[user_id]["genre_preferences"]
    )

    # USER activity_level
    user_id = next(iter(flink.state["activity_level"]))
    assert (
        redis.get("activity_level", user_id)
        == feature_store.user_features[user_id]["activity_level"]
    )

    # ITEM average_rating
    movie_id = next(iter(flink.item_rating_features.rating_count))
    assert (
        redis.get("item_average_rating", movie_id)
        == feature_store.item_features[movie_id]["average_rating"]
    )

    # ITEM popularity
    movie_id = next(iter(flink.state["item_popularity"]))
    assert (
        redis.get("item_popularity", movie_id)
        == feature_store.item_features[movie_id]["popularity"]
    )

    # USER watch_count
    user_id = next(iter(flink.state["watch_count"]))
    assert (
        redis.get("watch_count", user_id)
        == feature_store.user_features[user_id]["watch_count"]
    )

    # USER click_count
    user_id = next(iter(flink.state["user_click_counts"]))
    assert (
        redis.get("user_click_counts", user_id)
        == feature_store.user_features[user_id]["user_click_counts"]
    )
