from oa3302.EventGraphExamples import TandemQueueWithBlocking
from simkit.base import EventList
from simkit.rand import RandomVariate
from simkit.stats import SimpleStatsTimeVarying

# This is necessary for interactive consoles (like Spyder)
EventList.cold_reset()

# These are the parameters for the model
interarrival_time_generator = RandomVariate.instance("Exponential", mean=2.6)
service_time_generator_1 = RandomVariate.instance("Gamma", alpha=1.4, beta=1.6)
service_time_generator_2 = RandomVariate.instance("Uniform", min=1.0, max=3.0)
buffer = 1 # we'll start with a buffer of 1, which will be modified in the loop

# Instantiate the TandemQueueWithBlocking object and verify parameters
tandem_queue_with_blocking = TandemQueueWithBlocking(interarrival_time_generator, service_time_generator_1, service_time_generator_2, buffer)
print(tandem_queue_with_blocking.describe())

# Each of the states are time-varying
# Instantiate a statistics object for each one ...
number_in_queue_1_stat = SimpleStatsTimeVarying("number_in_queue_1")
number_in_queue_2_stat = SimpleStatsTimeVarying("number_in_queue_2")
number_available_servers_stat_1 = SimpleStatsTimeVarying("number_available_servers_1")
number_available_servers_stat_2 = SimpleStatsTimeVarying("number_available_servers_2")
number_blocked_stat = SimpleStatsTimeVarying("block")

# ... and make sure they are "listening" to the Event Graph object
tandem_queue_with_blocking.add_state_change_listener(number_in_queue_1_stat)
tandem_queue_with_blocking.add_state_change_listener(number_in_queue_2_stat)
tandem_queue_with_blocking.add_state_change_listener(number_available_servers_stat_1)
tandem_queue_with_blocking.add_state_change_listener(number_available_servers_stat_2)
tandem_queue_with_blocking.add_state_change_listener(number_blocked_stat)

# Set the stop time on the EventList
stop_time = 100000.0;
EventList.stop_at_time(stop_time)
print("\nSimulation will be run for {:,} time units\n".format(stop_time))

# Loop from buffer size 1 to 10
for buffer in range(1,11):
    tandem_queue_with_blocking.buffer = buffer # Make sure this run has the correct buffer size

# This clears the previous EventList, invokes reset() on the Event Graph object
# and schedule all run() events
    EventList.reset()

    # Reset each stat object for each replication
    number_in_queue_1_stat.reset()
    number_in_queue_2_stat.reset()
    number_available_servers_stat_1.reset()
    number_available_servers_stat_2.reset()
    number_blocked_stat.reset()

# Run the simulation
    EventList.start_simulation()

# Print the results of each run
    print("\nBuffer size: {buffer:d}".format(buffer=tandem_queue_with_blocking.buffer))
    print("Avg # in queue 1: {:,.4f}".format(number_in_queue_1_stat.time_varying_mean()))
    print("Avg # in queue 2: {:,.4f}".format(number_in_queue_2_stat.time_varying_mean()))
    print("Avg utilization server 1: {util:,.2f}%".format(util=100 * \
        (1 - number_available_servers_stat_1.time_varying_mean() + number_blocked_stat.time_varying_mean())))
    print("Avg utilization server 2: {util:,.2f}%".format(util=100 * (1 - number_available_servers_stat_2.time_varying_mean())))
    print("Avg # blocked: {:,.4f}".format(number_blocked_stat.mean))

