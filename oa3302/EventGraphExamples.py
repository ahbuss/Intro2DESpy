from simkit.base import SimEntityBase
from math import nan

""" Simple Event Graph models in DESpy

This is a collection of simple Event Graph models implemented in DESpy. They (roughly) correspond
to the models presented in OA3302 System Simulation class.

Models:
1. ArrivalProcess: simplest non-trivial Event Graph model
2. GG1: implements G/G/1 queue
3. ResourcePriority: Two servers, with one being "preferred"
4. NonPreEmptivePriorityQueue: Two types of customers, one "preferred"
5. TandemQueue: Two G/G/1 queues in tandem
6. TandemQueueWithBlocking: Two G/G/1 queues in tandem, but with a finite buffer for second queue that
   "blocks" customers at the first server from advancing when buffer is full
7. FailureModel: Server periodically "fails" and cannot continue processing until repaired
8. RenegingAndBalking: G/G/1 server with finite queue size (buffer); arriving customers finding the 
   buffer full leave without service ("balk"). Customers entering the queue will only wait
   for a certain amount of time, at which they exit the queue ("renege").

@author: Arnold Buss
@version: 1.0
"""

class ArrivalProcess(SimEntityBase):
    """
    Customers arrive periodically and are simply counted
    """

    def __init__(self, interarrival_time_generator):
        SimEntityBase.__init__(self) # Always call SimEntityBase's __init__(self)
        self.interarrival_time_generator = interarrival_time_generator  # t_a
        self.number_arrivals = nan  # N state variables initialy set to nan; initialized in reset()
        """
        :param interarrival_time_generator - RandomVariate to generate times between enter events (customer arrivals)
        """

    def reset(self):
        SimEntityBase.reset(self)
        self.number_arrivals = 0 # initialize number_arrivals to 0

    def run(self):
        self.notify_state_change("number_arrivals", self.number_arrivals) # notify initial state for nuumber_arrivals

        self.schedule("enter", self.interarrival_time_generator.generate()) # schedule next enter event

    def enter(self):
        self.number_arrivals = self.number_arrivals + 1 # increment number_arrivals & notify
        self.notify_state_change("number_arrivals", self.number_arrivals)

        self.schedule("enter", self.interarrival_time_generator.generate()) # schedule next enter event


class GG1(SimEntityBase):
    """
    Simple implementation of a G/G/1 model.
    """

    def __init__(self, interarrival_time_generator, service_time_generator):
        SimEntityBase.__init__(self)
        """
        :param interarrival_time_generator - RandomVariate to generate interarrival times
        :param service_time_generator - RandomVariate to generate service times
        """
        self.interarrival_time_generator = interarrival_time_generator  # t_a
        self.service_time_generator = service_time_generator  # t_s

        self.number_in_queue = nan #
        self.number_available_servers = nan

    def reset(self):
        SimEntityBase.reset(self)
        self.number_in_queue = 0 # initialize number_in_queue
        self.number_available_servers = 1 # intialize number_available_servers

    def run(self):
        self.notify_state_change("number_in_queue", self.number_in_queue)
        self.notify_state_change("number_available_servers", self.number_available_servers)

        self.schedule("enter", self.interarrival_time_generator.generate()) # schedule first enter event

    def enter(self):
        self.number_in_queue = self.number_in_queue + 1 # increment number_in_queue & notify
        self.notify_state_change("number_in_queue", self.number_in_queue)

        if self.number_available_servers > 0: # if available server, schedule start event
            self.schedule("start", 0.0)

        self.schedule("enter", self.interarrival_time_generator.generate()) # schedule next enter event

    def start(self):
        self.number_in_queue = self.number_in_queue - 1 # decrement number_in_queue
        self.notify_state_change("number_in_queue", self.number_in_queue)

        self.number_available_servers = self.number_available_servers - 1 # decrement number_available_servers
        self.notify_state_change("number_available_servers", self.number_available_servers)

        self.schedule("leave", self.service_time_generator.generate()) # schedule leave event

    def leave(self):
        self.number_available_servers = self.number_available_servers + 1 # increment number_available_servers
        self.notify_state_change("number_available_servers", self.number_available_servers)

        if (self.number_in_queue > 0): # if customer(s) in queue, schedule start event
            self.schedule("start", 0.0)


class ResourcePriority(SimEntityBase):
    """
    Two types of servers; server 1 is "preferred" to server 2. Each has their own service time generator
    """

    def __init__(self, interarrival_time_generator, service_time_generator_1, service_time_generator_2):
        SimEntityBase.__init__(self)
        """
        :param interarrival_time_generator - RandomVariate generates times between enter events
        :param service_time_generator_1 - RandomVariate generates service times for server 1
        :param service_time_generator_2 - RandomVariate generates service times for server 2
        """

        self.inter_arrival_time_generator = interarrival_time_generator
        self.service_time_generator_1 = service_time_generator_1
        self.service_time_generator_2 = service_time_generator_2

        self.number_in_queue = nan
        self.number_available_servers_1 = nan
        self.number_available_servers_2 = nan

    def reset(self):
        SimEntityBase.reset(self)
        self.number_in_queue = 0 # initially queue is empty
        self.number_available_servers_1 = 1 # initially 1 server of type 1 available
        self.number_available_servers_2 = 1 # initially 1 server of type 2 available

    def run(self):
        self.notify_state_change("number_in_queue", self.number_in_queue)
        self.notify_state_change("number_available_servers_1", self.number_available_servers_1)
        self.notify_state_change("number_available_servers_2", self.number_available_servers_2)

        self.schedule("enter", self.inter_arrival_time_generator.generate()) # schedule first enter event

    def enter(self):
        self.number_in_queue = self.number_in_queue + 1 # increment number_in_queue
        self.notify_state_change("numbver_in_queue", self.number_in_queue)

        if self.number_available_servers_1 > 0: # if a server_1`is available, schedule start1
            self.schedule("start1", 0.0)

        # if no server_1 available but a server_2 is, then schedule start2
        if self.number_available_servers_1 == 0 and self.number_available_servers_2 > 0:
            self.schedule("start2", 0.0)

        self.schedule("enter", self.inter_arrival_time_generator.generate()) # schedule next enter event

    def start1(self):
        self.number_in_queue = self.number_in_queue - 1 # decrement number_in_queue
        self.notify_state_change("number_in_queue", self.number_in_queue)

        self.number_available_servers_1 = self.number_available_servers_1 - 1 # decrement number_available_servers_1
        self.notify_state_change("number_available_servers_1", self.number_available_servers_1)

        self.schedule("leave1", self.service_time_generator_1.generate()) # schedule leave1

    def leave1(self):
        self.number_available_servers_1 = self.number_available_servers_1 + 1 # increment number_available_servers_1
        self.notify_state_change("number_available_servers_1", self.number_available_servers_1)

        if self.number_in_queue > 0:   # if customers in queue, schedule start1
            self.schedule("start1", 0.0)

    def start2(self):
        self.number_in_queue = self.number_in_queue - 1 # decrement number_in_queue
        self.notify_state_change("number_in_queue", self.number_in_queue)

        self.number_available_servers_2 = self.number_available_servers_2 - 1 # decrement number_available_servers_2
        self.notify_state_change("number_available_servers_2", self.number_available_servers_2)

        self.schedule("leave2", self.service_time_generator_2.generate()) # schedule leave2

    def leave2(self):
        self.number_available_servers_2 = self.number_available_servers_2 + 1 # increment number_available_servers_2
        self.notify_state_change("number_available_servers_2", self.number_available_servers_2)

        if self.number_in_queue > 0: # if customers in queue, schedule start2
            self.schedule("start2", 0.0)


class NonPreEmptivePriorityQueue(SimEntityBase):
    """
    Two types of customers - type 1 is "preferred". Each has their own service times. If the server is processing
    a type 2 customer when a type 1 arrives, the type 1 must wait until the server completes service (This is the
    "non-pre-emptive" part).
    """

    def __init__(self, interarrival_time_generator_1, interarrivel_time_generator_2, service_time_generator_1, service_time_generator_2):
        SimEntityBase.__init__(self)
        """
        :param interarrival_time_generator_1 - generates times between arrivals of type 1 customers
        :param interarrival_time_generator_2 - generates times between arrivals of type 2 customers
        :param service_time_generator_1 - servie times for type 1 customers
        :param service_time_generator_2 - service times for type 2 customers
        """
        self.interarrival_time_generator_1 = interarrival_time_generator_1
        self.interarrival_time_generator_2 = interarrivel_time_generator_2
        self.service_time_generator_1 = service_time_generator_1
        self.service_time_generator_2 = service_time_generator_2

        self.number_in_queue_1 = nan
        self.number_in_queue_2 = nan
        self.number_available_servers = nan

    def reset(self):
        SimEntityBase.reset(self)
        self.number_in_queue_1 = 0 # initially both queues are empty
        self.number_in_queue_2 = 0
        self.number_available_servers = 1 # initially one available server

    def run(self):

        self.notify_state_change("number_in_queue_1", self.number_in_queue_1)
        self.notify_state_change("number_in_queue_2", self.number_in_queue_2)
        self.notify_state_change("number_available_servers", self.number_available_servers)

        # schedule first enter events for type 1 and type 2 customers
        self.schedule("enter1", self.interarrival_time_generator_1.generate())
        self.schedule("enter2", self.interarrival_time_generator_2.generate())

    def enter1(self):
        self.number_in_queue_1 = self.number_in_queue_1 + 1 # increment number_in_queue_1
        self.notify_state_change("number_in_queue_1", self.number_in_queue_1)

        if self.number_available_servers > 0: # if sever is available,schedule start1
            self.schedule("start1", 0.0)

        self.schedule("enter1", self.interarrival_time_generator_1.generate()) # schedule next type 1 arrival

    def enter2(self):
        self.number_in_queue_2 = self.number_in_queue_2 + 1 # increment number_in_queue_2
        self.notify_state_change("number_in_queue_2", self.number_in_queue_2)

        if self.number_available_servers > 0: # if server is available, schedule start2
            self.schedule("start2", 0.0)

        self.schedule("enter2", self.interarrival_time_generator_1.generate()) # schedule next type 2 arrival

    def start1(self):
        self.number_in_queue_1 = self.number_in_queue_1 - 1 # decrement number_in_queue_1
        self.notify_state_change("number_in_queue_1", self.number_in_queue_1)

        self.number_available_servers = self.number_available_servers - 1; # decrement number_available_servers
        self.notify_state_change("number_available_servers", self.number_available_servers)

        self.schedule("leave", self.service_time_generator_1.generate()) # schedule leave event

    def start2(self):
        self.number_in_queue_2 = self.number_in_queue_2 - 1 # decrement number_in_queue_2
        self.notify_state_change("number_in_queue_2", self.number_in_queue_2)

        self.number_available_servers = self.number_available_servers - 1; # decrement number_available_servers
        self.notify_state_change("number_available_servers", self.number_available_servers)

        self.schedule("leave", self.service_time_generator_2.generate()) # schedule leave event

    def leave(self):
        self.number_available_servers += 1 # increment number_available_servers
        self.notify_state_change("number_available_servers", self.number_available_servers)

        if self.number_in_queue_1 > 0: # if type 1 customers waiting, service next type 1
            self.schedule("start1", 0.0)

        # if no type 1 customers waiting, but type 2 are, service the next type 2
        if self.number_in_queue_1 == 0 and self.number_in_queue_2 > 0:
            self.schedule("start2", 0.0)

class TandemQueue(SimEntityBase):
    """
    Two G/G/1 queues in tandem. Each customer is processed by the first server followed by the
    second, waiting in queue at each server if necessary. Both queues have infinite capacity.
    """

    def __init__(self, interarrival_time_generator, service_time_generator_1, service_time_generator_2):
        SimEntityBase.__init__(self)
        """
        :param interarrival_time_generator - time between cutomer arrivals to first server
        :param service_time_generator_1 - generates service times for first server
        :param service_time_generator_2 - generates service times for second server
        """
        self.interarrival_time_generator = interarrival_time_generator
        self.service_time_generator_1 = service_time_generator_1
        self.service_time_generator_2 = service_time_generator_2

        self.number_in_queue_1 = nan
        self.number_in_queue_2 = nan
        self.number_available_servers_1 = nan
        self.number_available_servers_2 = nan

    def reset(self):
        SimEntityBase.reset(self)
        self.number_in_queue_1 = 0 # both queue are initially empty
        self.number_in_queue_2 = 0
        self.number_available_servers_1 = 1 # both servers are initially available
        self.number_available_servers_2 = 1

    def run(self):
        self.notify_state_change("number_in_queue_1", self.number_in_queue_1)
        self.notify_state_change("number_in_queue_2", self.number_in_queue_2)
        self.notify_state_change("number_available_servers_1", self.number_available_servers_1)
        self.notify_state_change("number_available_servers_2", self.number_available_servers_2)

        self.schedule("enter", self.interarrival_time_generator.generate()) # schedule first enter event

    def enter(self):
        self.number_in_queue_1 += 1 # increment number_in_queue_1
        self.notify_state_change("number_in_queue_1", self.number_in_queue_1)

        if self.number_available_servers_1 > 0: # if server_1 is available, schedule start1
            self.schedule("start1", 0.0)

        self.schedule("enter", self.interarrival_time_generator.generate()) # schedule next enter event

    def start1(self):
        self.number_in_queue_1 -= 1 # decrement number_in_queue_1
        self.notify_state_change("number_in_queue_1", self.number_in_queue_1)

        self.number_available_servers_1 -= 1 # decrement number_available_servers_1
        self.notify_state_change("number_available_servers_1", self.number_available_servers_1)

        self.schedule("leave1", self.service_time_generator_1.generate()) # schedule leave event

    def leave1(self):
        self.number_available_servers_1 += 1 # increment number_available_servers_1
        self.notify_state_change("number_available_servers_1", self.number_available_servers_1)

        self.number_in_queue_2 += 1 # increment number_in_queue_2
        self.notify_state_change("number_in_queue_2", self.number_in_queue_2)

        if self.number_available_servers_2 > 0: # if server_2 is available, schedule start2
            self.schedule("start2", 0.0)

        if self.number_in_queue_1 > 0: # if customers waiting in first queue, schedule start1
            self.schedule("start1", 0.0)

    def start2(self):
        self.number_in_queue_2 -= 1 # decrement number_in_queue_2
        self.notify_state_change("number_in_queue_2", self.number_in_queue_2)

        self.number_available_servers_2 -= 1 # decrement number_available_servers_2
        self.notify_state_change("number_available_servers_2", self.number_available_servers_2)

        self.schedule("leave2", self.service_time_generator_2.generate()) # schedule leave2 event

    def leave2(self):
        self.number_available_servers_2 += 1 # increment number_available_servers_2
        self.notify_state_change("number_available_servers_2", self.number_available_servers_2)

        if self.number_in_queue_2 > 0: # if customers in second queue, schedule start2
            self.schedule("start2", 0.0)

class TandemQueueWithBlocking(SimEntityBase):
    """
    Two G/G/1 queues in tandem. The first queue has infinite capacity, but the second has finite capacity. A customer
    completing service at the first server who finds the buffer full must wait at the first server, preventing
    processing the next customer until a space opens in the second queue ("blocking")
    """

    def __init__(self, interarrival_time_generator, service_time_generator_1, service_time_generator_2, buffer):
        SimEntityBase.__init__(self)
        """
        :param interarrival_time_generator - generates times between customer arrivals
        :param service_time_generator_1 - generates service times for first server
        :param service_time_generator_2 - generates service times for second server
        :param buffer - maximum size of queue for second server
        """
        self.interarrival_time_generator = interarrival_time_generator
        self.service_time_generator_1 = service_time_generator_1
        self.service_time_generator_2 = service_time_generator_2
        self.buffer = buffer

        self.number_in_queue_1 = nan
        self.number_in_queue_2 = nan
        self.number_available_servers_1 = nan
        self.number_available_servers_2 = nan
        self.block = nan

    def reset(self):
        SimEntityBase.reset(self)
        self.number_in_queue_1 = 0 # initially both queues are empty
        self.number_in_queue_2 = 0
        self.number_available_servers_1 = 1 # initially both servers are available
        self.number_available_servers_2 = 1
        self.block = 0

    def run(self):
        self.notify_state_change("number_in_queue_1", self.number_in_queue_1)
        self.notify_state_change("number_in_queue_2", self.number_in_queue_2)
        self.notify_state_change("number_available_servers_1", self.number_available_servers_1)
        self.notify_state_change("number_available_servers_2", self.number_available_servers_2)
        self.notify_state_change("block", self.block)

        self.schedule("enter1", self.interarrival_time_generator.generate()) # schedule first enter event

    def enter1(self):
        self.number_in_queue_1 += 1 # increment number_in_queue_1
        self.notify_state_change("number_in_queue_1", self.number_in_queue_1)

        # if first server is available and not blocked, schedule start1
        if self.number_available_servers_1 > 0 and self.block == 0:
            self.schedule("start1", 0.0)

        self.schedule("enter1", self.interarrival_time_generator.generate()) # schedule next enter event

    def start1(self):
        self.number_in_queue_1 -= 1 # decrement number_in_queue_1
        self.notify_state_change("number_in_queue_1", self.number_in_queue_1)

        self.number_available_servers_1 -= 1 # decrement number_available_servers_1
        self.notify_state_change("number_available_servers_1", self.number_available_servers_1)

        self.schedule("leave1", self.service_time_generator_1.generate()) # schedule leave1 event

    def leave1(self):
        self.number_available_servers_1 += 1 # increment number_available_servers_1
        self.notify_state_change("number_available_servers_1", self.number_available_servers_1)

        self.block = 1 # block server, if only temporarily
        self.notify_state_change("block", self.block)

        if self.number_in_queue_2 < self.buffer: # if space in second queue, schedule enter2
            self.schedule("enter2", 0.0)

    def enter2(self):
        self.number_in_queue_2 += 1; # increment number_in_queue_2
        self.notify_state_change("number_in_queue_2", self.number_in_queue_2)

        self.block = 0 # unblock first server
        self.notify_state_change("block", self.block)

        if self.number_available_servers_2 > 0: # if second server is available, schedule start2
            self.schedule("start2", 0.0)

        if self.number_in_queue_1 > 0: # if customers in first queue, schedule start1
            self.schedule("start1", 0.0)

    def start2(self):
        self.number_in_queue_2 -= 1 # decrement number_in_queue_2
        self.notify_state_change("number_in_queue_2", self.number_in_queue_2)

        self.number_available_servers_2 -= 1 # decrement number_available_servers_2
        self.notify_state_change("number_available_servers_2", self.number_available_servers_2)

        self.schedule("leave2", self.service_time_generator_2.generate()) #schedule leave2

        if self.block == 1: # if first server is blocked, schedule enter2 to unblock
            self.schedule("enter2", 0.0)

    def leave2(self):
        self.number_available_servers_2 += 1 # increment number_available_servers_2
        self.notify_state_change("number_available_servers_2", self.number_available_servers_2)

        if self.number_in_queue_2 > 0: # if customers waiting in second queue, schedule start2
            self.schedule("start2", 0.0)


class FailureModel(SimEntityBase):
    """
    The G/G/1 model with server failures. A failure could occur whether the server is processing a customer
    or not. If it is, then the customer is "lost". Following a failure, the server is not available until
    it is repaired. A failed server does not have to queue up for a repair person, but can immediately
    start being repaired. When repair is complete, the server can process waiting customers (if any)
    """

    def __init__(self, interarrival_time_generator, service_time_generator, failure_generator, repair_generator):
        SimEntityBase.__init__(self)
        """
        :param interarrival_time_generator - generates times between customer arrivals
        :param service_time_generator - generates service times
        :param failure_generator - generates times to failure
        :param repair_generator - generates times to complete server repair following failure
        """
        self.interarrival_time_generator = interarrival_time_generator
        self.service_time_generator = service_time_generator
        self.failure_generator = failure_generator
        self.repair_generator = repair_generator

        self.number_in_queue = nan
        self.number_available_servers = nan
        self.number_failed_servers = nan

    def reset(self):
        SimEntityBase.reset(self)
        self.number_in_queue = 0 # initially queue is empty
        self.number_available_servers = 1 # initially server is available
        self.number_failed_servers = 0 # initially server is not failed

    def run(self):
        self.notify_state_change("number_in_queue", self.number_in_queue)
        self.notify_state_change("number_available_servers", 1)
        self.notify_state_change("number_failed_servers", self.number_failed_servers)

        self.schedule("enter", self.interarrival_time_generator.generate()) # schedule first customer arrival
        self.schedule("fail", self.failure_generator.generate()) # schedule first server failure

    def enter(self):
        self.number_in_queue += 1 # increment number_in_queue
        self.notify_state_change("number_in_queue", self.number_in_queue)

        if self.number_available_servers > 0: # is server is available, schedule start
            self.schedule("start", 0.0)

        self.schedule("enter", self.interarrival_time_generator.generate()) # schedule next customer arrival

    def start(self):
        self.number_in_queue -= 1 # decrement number_in_queue
        self.notify_state_change("number_in_queue", self.number_in_queue)

        self.number_available_servers = 0 # server is not available
        self.notify_state_change("number_available_servers", self.number_available_servers)

        self.schedule("leave", self.service_time_generator.generate()) # schedule leave event

    def leave(self):
        self.number_available_servers = 1 # server is available
        self.notify_state_change("number_available_servers", self.number_available_servers)

        if self.number_in_queue > 0: # schedule start if customers waiting
            self.schedule("start", 0.0)

    def fail(self):
        self.number_available_servers = 0 # server is not available
        self.notify_state_change("number_available_servers", self.number_available_servers)

        self.number_failed_servers = 1 # server is failed
        self.notify_state_change("number_failed_servers", self.number_failed_servers)

        self.cancel("leave") # cancel leave event (if any)

        self.schedule("repair", self.repair_generator.generate()) # schedule repair event

    def repair(self):
        self.number_available_servers = 1 # server is available
        self.notify_state_change("number_available_servers", self.number_available_servers)

        self.number_failed_servers = 0 # server is repaired (i.e. not failed)
        self.notify_state_change("number_failed_servers", self.number_failed_servers)

        if self.number_in_queue > 0: # if customers waiting, schedule start
            self.schedule("start", 0.0)

        self.schedule("fail", self.failure_generator.generate()) # schedule next failure

class RenegingAndBalking(SimEntityBase):
    """
        A G/G/1 model with finite capacity queue and "impatient" customers. An arriving customer who
        finds the queue full leaves ("balks"). A customer who enters the queue but does not receive
        service before their "impatient" time levaes the queue ("renege").
    """

    def __init__(self, interarrival_time_generator, service_time_generator, renege_time_generator, buffer_size):
        SimEntityBase.__init__(self)
        """
            :param interarrival_time_generator - generates times between customer arrivals ('arrive' events)
            :param service_time_generator - generates service times
            :param renege_time_generator - generates renege ("impatient") times
            :param buffer_size - maximum number of customers who can be in queue
        """
        self.interarrival_time_generator = interarrival_time_generator
        self.service_time_generator = service_time_generator
        self.renege_time_generator = renege_time_generator
        self.buffer_size = buffer_size

        self.number_in_queue = nan
        self.number_available_servers = nan
        self.number_arrivals = nan
        self.number_balks = nan
        self.number_reneges = nan

    def reset(self):
        SimEntityBase.reset(self)
        self.number_in_queue = 0 # initially queue is empty
        self.number_available_servers = 1 # initially server is available
        self.number_arrivals = 0 # initially no customers have arrived
        self.number_balks = 0 # initially no customers have balked
        self.number_reneges = 0 # initially no customers have reneged

    def run(self):
        self.notify_state_change("number_in_queue", self.number_in_queue)
        self.notify_state_change("number_available_servers", self.number_available_servers)
        self.notify_state_change("number_arrivals", self.number_arrivals)
        self.notify_state_change("number_balks", self.number_balks)
        self.notify_state_change("number_reneges", self.number_reneges)

        self.schedule("arrive", self.interarrival_time_generator.generate()) # schedule first arrive event

    def arrive(self):
        self.number_arrivals += 1  # increment number_arrivals
        self.notify_state_change("number_arrivals", self.number_arrivals)

        if self.number_in_queue < self.buffer_size: # if space in queue, schedule enter
            self.schedule("enter", 0.0)

        if self.number_in_queue == self.buffer_size: # if no space in queue, schedule balk
            self.schedule("balk", 0.0)

        self.schedule("arrive", self.interarrival_time_generator.generate())

    def enter(self):
        self.number_in_queue += 1 # increment number_in_queue
        self.notify_state_change("number_in_queue", self.number_in_queue)

        if self.number_available_servers > 0: # if server is available, schedule start
            self.schedule("start", 0.0)

        if self.number_available_servers == 0: # if server not available, schedule reneg event
            self.schedule("reneg", self.renege_time_generator.generate())

    def start(self):
        self.number_in_queue -= 1; # decrement number_in_queue
        self.notify_state_change("number_in_queue", self.number_in_queue)

        self.number_available_servers -= 1 # decrement number_available_servers
        self.notify_state_change("number_available_servers", self.number_available_servers)

        self.schedule("leave", self.service_time_generator.generate()) # schedule leave

    def leave(self):
        self.number_available_servers += 1 # increment number_available_servers
        self.notify_state_change("number_available_servers", self.number_available_servers)

        if self.number_in_queue > 0: # if customer(s) in queue ...
            self.cancel("reneg") # cancel next reneg event, and ...
            self.schedule("start", 0.0) # schedule start

    def balk(self):
        self.number_balks += 1; # increment number_balks
        self.notify_state_change("number_balks", self.number_balks)

    def reneg(self):
        self.number_in_queue -= 1 # decrement number_in_queue (since customer leaves)
        self.notify_state_change("number_in_queue", self.number_in_queue)

        self.number_reneges += 1; #increment number_reneges
        self.notify_state_change("number_reneges", self.number_reneges)
