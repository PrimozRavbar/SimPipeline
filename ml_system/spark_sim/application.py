from enum import Enum


class ApplicationState(Enum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class SparkApplication:

    def __init__(
        self,
        application_id,
        name,
        driver
    ):
        self.application_id = application_id
        self.name = name
        self.driver = driver

        self.state = ApplicationState.CREATED

        self.jobs = []

        self.start_time = None
        self.end_time = None

        self.metrics = {
            "jobs_submitted": 0,
            "jobs_succeeded": 0,
            "jobs_failed": 0
        }

        self.logs = []

    def start(self, clock):

        self.start_time = clock.now
        self.state = ApplicationState.RUNNING

        self.log(
            f"Application {self.application_id} started"
        )

        self.driver.start(clock)

    def submit_job(self, job):

        if self.state != ApplicationState.RUNNING:
            raise RuntimeError(
                "Cannot submit a job to an application "
                f"in state {self.state.value}"
            )

        self.jobs.append(job)

        self.metrics["jobs_submitted"] += 1

        self.log(
            f"Job {job.job_id} submitted"
        )

        self.driver.submit_job(job)

    def complete(self, clock):

        self.state = ApplicationState.SUCCEEDED
        self.end_time = clock.now

        self.log(
            f"Application {self.application_id} completed"
        )

    def fail(self, clock, error):

        self.state = ApplicationState.FAILED
        self.end_time = clock.now

        self.log(
            f"Application {self.application_id} failed: {error}"
        )

    def cancel(self, clock):

        self.state = ApplicationState.CANCELLED
        self.end_time = clock.now

        self.log(
            f"Application {self.application_id} cancelled"
        )

    def log(self, message):

        self.logs.append(message)
