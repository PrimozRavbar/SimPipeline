from enum import Enum


class TaskSchedulerState(Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"


class TaskScheduler:

    def __init__(self, scheduler_id):

        self.scheduler_id = scheduler_id

        self.state = TaskSchedulerState.IDLE

        self.pending_tasks = []
        self.running_tasks = []
        self.completed_tasks = []
        self.failed_tasks = []

        self.executors = []

        self.metrics = {
            "tasks_submitted": 0,
            "tasks_started": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
        }

        self.logs = []

    def start(self):

        self.state = TaskSchedulerState.RUNNING

        self.log(
            f"Task scheduler {self.scheduler_id} started"
        )

    def add_executor(self, executor):

        self.executors.append(executor)

        self.log(
            f"Executor {executor.executor_id} registered"
        )

    def submit(self, task):

        if self.state != TaskSchedulerState.RUNNING:
            raise RuntimeError(
                "Cannot submit task to task scheduler "
                f"in state {self.state.value}"
            )

        self.pending_tasks.append(task)

        self.metrics["tasks_submitted"] += 1

        self.log(
            f"Task {task.task_id} submitted"
        )

    def schedule(self, clock):

        if self.state != TaskSchedulerState.RUNNING:
            return

        for executor in self.executors:

            if not self.pending_tasks:
                break

            if not executor.can_run(
                self.pending_tasks[0]
            ):
                continue

            task = self.pending_tasks.pop(0)

            self.running_tasks.append(task)

            self.metrics["tasks_started"] += 1

            executor.run_task(
                task,
                clock
            )

            self.running_tasks.remove(task)

            if task.state.value == "SUCCEEDED":

                self.completed_tasks.append(task)

                self.metrics["tasks_completed"] += 1

            else:

                self.failed_tasks.append(task)

                self.metrics["tasks_failed"] += 1

    def stop(self):

        self.state = TaskSchedulerState.STOPPED

        self.log(
            f"Task scheduler {self.scheduler_id} stopped"
        )

    def log(self, message):

        self.logs.append(message)
