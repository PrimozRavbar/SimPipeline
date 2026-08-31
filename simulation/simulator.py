from .clock import Clock
from .service import Service

class Simulator:

    def __init__(self):
        self.clock = Clock()

        # All services running in the simulation
        self.services = {}

        # Global event bus (NOT Kafka)
        self.event_bus = []

        # Global configuration
        self.config = {}

        # Failure injection
        self.scenarios = []

        # Metrics about the simulation itself
        self.metrics = {}

        # Randomness
        self.random = random.Random(42)

        self.running = False

    #def register(self, service):
      #  self.services[service.name] = service

    def register(self, service):
        self.services[service.name] = service
        service.start(self)

    def unregister(self, name):
        del self.services[name]

    #def publish(self, event):
       # self.event_bus.append(event)
    """
    def publish(self, event):
        print(event)
        self.event_bus.append(event)
    """
    def publish(self, event):

        print(event)

        kafka = self.get_service("Kafka")

        kafka.receive(event)


    def get_service(self, name):
        return self.services[name]

    def tick(self):

        self.clock.tick()

        for service in self.services.values():
            service.tick(self)

    def run(self, ticks=None):

        self.running = True

        while self.running:

            self.tick()

            if ticks is not None:
                ticks -= 1
                if ticks == 0:
                    break

    def stop(self):
        self.running = False