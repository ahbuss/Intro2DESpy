from heapq import heappush, heappop
from simkit.base import SimEntityBase, Entity, Priority
from math import nan
from math import ceil
from simkit.rand import RandomVariate
from oa3302.EventGraphExamples import GG1


class GGk(SimEntityBase):
    def __init__(self, interarrival_time_generator, service_time_generator, total_number_servers):
        """ Multiple server queue with possibly more than one server

        :param interarrival_time_generator: generates times between arrivals
        :param service_time_generator: generates service times
        :param total_number_servers: this many servers in parallel
        """
        SimEntityBase.__init__(self)
        self.interarrival_time_generator = interarrival_time_generator
        self.service_time_generator = service_time_generator
        self.total_number_servers = total_number_servers

        self.number_in_queue = nan
        self.number_available_servers = nan

    # Initialize number_in_queue to 0 and number_available_servers to total_number_servers
    def reset(self):
        SimEntityBase.reset(self)
        self.number_in_queue = 0
        self.number_available_servers = self.total_number_servers

    # Schedule first enter event
    def run(self):
        self.notify_state_change("number_in_queue", self.number_in_queue)
        self.notify_state_change("number_available_servers", self.number_available_servers)

        self.schedule("enter", self.interarrival_time_generator.generate())

    # increment number_in_queue; is available server, schedule start event; schedule next enter event
    def enter(self):
        self.number_in_queue += 1
        self.notify_state_change("number_in_queue", self.number_in_queue)

        if self.number_available_servers > 0:
            self.schedule("start", 0.0)

        self.schedule("enter", self.interarrival_time_generator.generate())

    # decrement number_in_queue and number_available_servers; schedule leave event
    def start(self):
        self.number_in_queue -= 1
        self.notify_state_change("number_in_queue", self.number_in_queue)

        self.number_available_servers -= 1
        self.notify_state_change("number_available_servers", self.number_available_servers)

        self.schedule("leave", self.service_time_generator.generate())

    # increment number_available_servers; if customers in queue, schedule start event
    def leave(self):
        self.number_available_servers += 1
        self.notify_state_change("number_available_servers", self.number_available_servers)

        if self.number_in_queue > 0:
            self.schedule("start", 0.0)


class GGkBatchArrivals(SimEntityBase):
    def __init__(self, interarrival_time_generator, service_time_generator, total_number_servers, batch_generator):
        """ G/G/k queue with batch arrivals

        :param interarrival_time_generator: generates interarrival times
        :param service_time_generator: generates service times
        :param total_number_servers: total # servers
        :param batch_generator: generates batch sizes
        """
        SimEntityBase.__init__(self)
        self.interarrival_time_generator = interarrival_time_generator
        self.service_time_generator = service_time_generator
        self.total_number_servers = total_number_servers
        self.batch_generator = batch_generator

        self.number_in_queue = nan
        self.number_available_servers = nan
        self.total_number_servers

    def reset(self):
        SimEntityBase.reset(self)
        self.number_in_queue = 0
        self.number_available_servers = self.total_number_servers

    def run(self):
        self.notify_state_change("number_in_queue", self.number_in_queue)
        self.notify_state_change("number_available_servers", self.number_available_servers)

        self.schedule("enter", self.interarrival_time_generator.generate())

    # generate batch and increment number_in_queue by that; if available server, schedule start event
    def enter(self):
        self.number_in_queue += ceil(self.batch_generator.generate())
        self.notify_state_change("number_in_queue", self.number_in_queue)

        if self.number_available_servers > 0:
            self.schedule("start", 0.0)

        self.schedule("enter", self.interarrival_time_generator.generate())

    # decrement number_in_queue and number_available_servers; schedule leave event.
    # If there are still customers in queue and available servers, schedule another start event
    def start(self):
        self.number_in_queue -= 1
        self.notify_state_change("number_in_queue", self.number_in_queue)

        self.number_available_servers -= 1
        self.notify_state_change("number_available_servers", self.number_available_servers)

        self.schedule("leave", self.service_time_generator.generate())

        if self.number_available_servers > 0 and self.number_in_queue > 0:
            self.schedule("start", 0.0)

    # increment number_available_servers; if customers in queue, schedule start event
    def leave(self):
        self.number_available_servers += 1
        self.notify_state_change("number_available_servers", self.number_available_servers)

        if (self.number_in_queue > 0):
            self.schedule("start", 0.0)


class GGkWithVaryingServers(SimEntityBase):
    def __init__(self, interarrival_time_generator, service_time_generator, queue_threshold):
        """G/G/k queue with servers added when queue grows

        :param interarrival_time_generator: generates interarrival times
        :param service_time_generator: generates service times
        :param queue_threshold: when queue size exceeds this, another server is added
        """
        SimEntityBase.__init__(self)
        self.interarrival_time_generator = interarrival_time_generator
        self.service_time_generator = service_time_generator
        self.queue_threshold = queue_threshold

        self.number_in_queue = nan # number in queue
        self.number_available_servers = nan # number of available servers
        self.total_number_servers = nan # how many servers are currently working

    # initialized number_in_queue to 0, number_available_servers to 1, and total_number_servers to 1
    def reset(self):
        SimEntityBase.reset(self)
        self.number_in_queue = 0
        self.number_available_servers = 1
        self.total_number_servers = 1

    # Schedule first enter event
    def run(self):
        self.notify_state_change("number_in_queue", self.number_in_queue)
        self.notify_state_change("number_available_servers", self.number_available_servers)
        self.notify_state_change("total_number_servers", self.total_number_servers)

        self.schedule("enter", self.interarrival_time_generator.generate())

    # Increment number_in_queue; if server is available, schedule start event;
    # If queue excceeds threshold, schedule add event
    def enter(self):
        self.number_in_queue += 1
        self.notify_state_change("number_in_queue", self.number_in_queue)

        if self.number_available_servers > 0:
            self.schedule("start", 0.0)

        self.schedule("enter", self.interarrival_time_generator.generate())

        if self.number_in_queue > self.queue_threshold:
            self.schedule("add", 0.0)

    # decrement number_in_queue and number_available_servers; schedule leave event
    def start(self):
        self.number_in_queue -= 1
        self.notify_state_change("number_in_queue", self.number_in_queue)

        self.number_available_servers -= 1
        self.notify_state_change("number_available_servers", self.number_available_servers)

        self.schedule("leave", self.service_time_generator.generate())

    # Increment number_available_servers; is customers in queue, schedule start event;
    # If no customers in queue and more than 1 total servers, schedule remove
    def leave(self):
        self.number_available_servers += 1
        self.notify_state_change("number_available_servers", self.number_available_servers)

        if self.number_in_queue > 0:
            self.schedule("start", 0.0)

        if self.number_in_queue == 0 and self.total_number_servers > 1:
            self.schedule("remove", 0.0)

    # Increment total_number_servers and number_available_servers; schedule start event
    def add(self):
        self.number_available_servers += 1
        self.notify_state_change("number_available_servers", self.number_available_servers)

        self.total_number_servers += 1
        self.notify_state_change("total_number_servers", self.total_number_servers)

        self.schedule("start", 0.0)

    # Decrement total_number_servers and number_available_servers
    def remove(self):
        self.number_available_servers -= 1
        self.notify_state_change("number_available_servers", self.number_available_servers)

        self.total_number_servers -= 1
        self.notify_state_change("total_number_servers", self.total_number_servers)

class Rework(GG1):
    def __init__(self, interarrival_time_generator, service_time_generator, prob_rework):
        GG1.__init__(self, interarrival_time_generator, service_time_generator)

        self.rework_generator = RandomVariate.instance("Discrete", values=[False, True], \
                                                       frequencies = [1 - prob_rework, prob_rework])
    def leave(self):
        self.number_available_servers += 1
        self.notify_state_change("number_available_servers", self.number_available_servers)

        if self.rework_generator.generate():
            self.number_in_queue += 1
            self.notify_state_change("number_in_queue", self.number_in_queue)

        if self.number_in_queue > 0:
            self.schedule("start", 0.0)


'''
An instance of this class can be a "SimEvent Listener" to an instance of GGk. It will 
simply count the number of enter events, thus allowing an estimate of the 
arrival rate to the system.
'''
class ArrivalCounter(SimEntityBase):
    def __init__(self):
        SimEntityBase.__init__(self)

        self.number_arrivals = nan

    def reset(self):
        SimEntityBase.reset(self)
        self.number_arrivals = 0

    def enter(self):
        self.number_arrivals += 1
        self.notify_state_change("number_arrivals", self.number_arrivals)

'''
This model of a G/G/k queueing system allows for direct estimation of 
delay in queue and time in system. It also illustrates using Entity objects
to represent individual customers.
'''
class GGkWithEntities(SimEntityBase):
    def __init__(self, interarrival_time_generator, total_number_servers, service_time_generator):
        SimEntityBase.__init__(self)

        self.interarrival_time_generator = interarrival_time_generator
        self.total_number_servers = total_number_servers
        self.service_time_generator = service_time_generator

        self.queue =[]
        self.number_available_servers = nan

        self.delay_in_queue = nan
        self.time_in_system = nan

    def reset(self):
        SimEntityBase.reset(self)
        self.queue.clear()
        self.number_available_servers = self.total_number_servers

    def run(self):

        self.notify_state_change("queue", self.queue.copy())
        self.notify_state_change("number_available_servers", self.number_available_servers)

        self.schedule("arrival", self.interarrival_time_generator.generate())

    def arrival(self):
        customer = Entity(name="Customer")
        customer.stamp_time()
        heappush(self.queue, customer)

        self.notify_state_change("queue", self.queue.copy())

        if self.number_available_servers > 0:
            self.schedule("start_service", 0.0, priority=Priority.HIGH)

        self.schedule("arrival", self.interarrival_time_generator.generate())

    def start_service(self):
        customer = heappop(self.queue)
        self.notify_state_change("queue", self.queue.copy())

        self.number_available_servers -= 1
        self.notify_state_change("number_available_servers", self.number_available_servers)

        self.delay_in_queue = customer.elapsed_time()
        self.notify_state_change("delay_in_queue", self.delay_in_queue)

        self.schedule("end_service", self.service_time_generator.generate(), customer)

    def end_service(self, customer):

        self.time_in_system = customer.elapsed_time()
        self.notify_state_change("time_in_system", self.time_in_system)

        self.number_available_servers += 1
        self.notify_state_change("number_available_servers", self.number_available_servers)

        if self.queue:
            self.schedule("start_service", 0.0, priority=Priority.HIGH)