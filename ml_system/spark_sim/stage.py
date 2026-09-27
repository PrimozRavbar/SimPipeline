from enum import Enum


class StageState(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class SparkStage:

    def __init__(
        self,
        stage_id,
        name,
        tasks=None,
        dependencies=None
    ):
        self.stage_id = stage_id
        self.name = name

        self.state = StageState.PENDING

        self.tasks = tasks or []
        self.dependencies = dependencies or []

        self.start_time = None
        self.end_time = None

        self.metrics = {
            "tasks_submitted": 0,
            "tasks_succeeded": 0,
            "tasks_failed": 0,
        }

        self.logs = []

    def add_task(self, task):

        self.tasks.append(task)

        self.metrics["tasks_submitted"] += 1

        self.log(
            f"Task {task.task_id} added to stage {self.stage_id}"
        )

    def start(self, clock):

        if self.state != StageState.PENDING:
            raise RuntimeError(
                f"Cannot start stage in state {self.state.value}"
            )

        self.state = StageState.RUNNING
        self.start_time = clock.now

        self.log(
            f"Stage {self.stage_id} started at tick {clock.now}"
        )

    def complete(self, clock):

        self.state = StageState.SUCCEEDED
        self.end_time = clock.now

        self.log(
            f"Stage {self.stage_id} completed at tick {clock.now}"
        )

    def fail(self, clock, error):

        self.state = StageState.FAILED
        self.end_time = clock.now

        self.log(
            f"Stage {self.stage_id} failed: {error}"
        )

    def log(self, message):

        self.logs.append(message)
