from enum import Enum


class JobState(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class SparkJob:

    def __init__(
        self,
        job_id,
        name,
        stages=None
    ):
        self.job_id = job_id
        self.name = name

        self.state = JobState.PENDING

        self.stages = stages or []

        self.current_stage = None

        self.start_time = None
        self.end_time = None

        self.metrics = {
            "stages_submitted": 0,
            "stages_succeeded": 0,
            "stages_failed": 0,
        }

        self.logs = []

    def add_stage(self, stage):

        self.stages.append(stage)

        self.metrics["stages_submitted"] += 1

        self.log(
            f"Stage {stage.stage_id} added to job {self.job_id}"
        )

    def start(self, clock):

        if self.state != JobState.PENDING:
            raise RuntimeError(
                f"Cannot start job in state {self.state.value}"
            )

        self.state = JobState.RUNNING
        self.start_time = clock.now

        self.log(
            f"Job {self.job_id} started at tick {clock.now}"
        )

    def complete(self, clock):

        self.state = JobState.SUCCEEDED
        self.end_time = clock.now

        self.log(
            f"Job {self.job_id} completed at tick {clock.now}"
        )

    def fail(self, clock, error):

        self.state = JobState.FAILED
        self.end_time = clock.now

        self.log(
            f"Job {self.job_id} failed: {error}"
        )

    def log(self, message):

        self.logs.append(message)
