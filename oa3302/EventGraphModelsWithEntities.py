from simkit.base import SimEntityBase
from simkit.base import Entity
from math import nan
from heapq import heappush, heappop

class MultipleServerQueue(SimEntityBase):
    def __init__(self, interarrival_time_generator, service_time_generator, total_number_servers):
        SimEntityBase.__init__(self)

        self.interarrival_time_generator = interarrival_time_generator
        self.service_time_generator = service_time_generator
        self.total_number_servers = total_number_servers

        self.number_available_servers = nan
        self.delay_in_queue = nan
        self.time_in_system = nan
        self.queue = []

    def reset(self):
        SimEntityBase.reset(self)
        self.number_available_servers = self.total_number_servers
        self.queue.clear()
        self.delay_in_queue = nan
        self.time_in_system = nan

    def run(self):
        self.notify_state_change("number_available_servers", self.number_available_servers)
        self.notify_state_change("queue", self.queue.copy())
        self.notify_state_change("delay_in_queue", self.delay_in_queue)
        self.schedule("enter", self.interarrival_time_generator.generate())

    def enter(self):
        e = Entity(name='Customer')
        e.stamp_time()
        heappush(self.queue, e)
        self.notify_state_change("queue", self.queue.copy())

        if self.number_available_servers > 0:
            self.schedule("start", 0.0)

        self.schedule("enter", self.interarrival_time_generator.generate())

    def start(self):
        e = heappop(self.queue)
        self.notify_state_change("queue", self.queue.copy())

        self.delay_in_queue = e.age()
        self.notify_state_change("delay_in_queue", self.delay_in_queue)

        self.number_available_servers -= 1
        self.notify_state_change("number_available_servers", self.number_available_servers)

        self.schedule("leave", self.service_time_generator.generate(), e)

    def leave(self, e):
        self.time_in_system = e.age()
        self.notify_state_change("time_in_system", self.time_in_system)

        self.number_available_servers += 1
        self.notify_state_change("number_available_servers", self.number_available_servers)

        if self.queue.__len__() > 0:
            self.schedule("start", 0.0)

class ServerWithReneges(SimEntityBase):
    def __init__(self, interarrival_time_generator, service_time_generator, total_number_servers,\
                 renege_time_generator):
        SimEntityBase.__init__(self)

        self.interarrival_time_generator = interarrival_time_generator
        self.service_time_generator = service_time_generator
        self.total_number_servers = total_number_servers
        self.renege_time_generator = renege_time_generator

        self.number_available_servers = nan
        self.queue =[]
        self.number_arrivals = nan
        self.number_reneges = nan
        self.delay_in_queue_served = nan
        self.delay_in_queue_reneged = nan
        self.time_in_system_served = nan

    def reset(self):
        SimEntityBase.reset(self)
        self.number_available_servers = self.total_number_servers
        self.queue.clear()
        self.number_arrivals = 0;
        self.number_reneges = 0
        self.delay_in_queue_served = nan
        self.delay_in_queue_reneged = nan
        self.time_in_system_served = nan

    def run(self):
        self.notify_state_change("number_available_servers", self.number_available_servers)
        self.notify_state_change("queue", self.queue.copy())
        self.notify_state_change("number_arrivals", self.number_arrivals)
        self.notify_state_change("number_reneges", self.number_reneges)

        self.schedule("enter", self.interarrival_time_generator.generate())

    def enter(self):
        e = Entity("Customer")
        heappush(self.queue, e)
        self.notify_state_change("queue", self.queue.copy())

        self.number_arrivals += 1;
        self.notify_state_change("number_arrivals", self.number_arrivals)

        self.schedule("enter", self.interarrival_time_generator.generate())

        self.schedule("renege", self.renege_time_generator.generate(), e)

        if self.number_available_servers > 0:
            self.schedule("start", 0.0)

    def start(self):
        e = heappop(self.queue)
        self.notify_state_change("queue", self.queue.copy())

        self.delay_in_queue_served = e.age()
        self.notify_state_change("delay_in_queue_served", self.delay_in_queue_served)

        self.number_available_servers -=1
        self.notify_state_change("number_available_servers", self.number_available_servers)

        self.cancel("renege", e)

        self.schedule("leave", self.service_time_generator.generate(), e)

    def leave(self, e):
        self.time_in_system_served = e.age()
        self.notify_state_change("time_in_system_served", self.time_in_system_served)

        self.number_available_servers += 1
        self.notify_state_change("number_available_servers", self.number_available_servers)

        if self.queue.__len__() > 0:
            self.schedule("start", 0.0)

    def renege(self, e):
        self.number_reneges += 1
        self.notify_state_change("number_reneges", self.number_reneges)

        self.delay_in_queue_reneged = e.age()
        self.notify_state_change("delay_in_queue_reneged", self.delay_in_queue_reneged)

        self.queue.remove(e)
        self.notify_state_change("queue", self.queue.copy())