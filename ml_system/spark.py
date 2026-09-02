from simulation.service import Service


class Spark(Service):
    def __init__(self):
        super().__init__()

    def run_offline_feature_job(self, events, feature_pipeline):
        feature_pipeline.process(events)
