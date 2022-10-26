from oa3302.EventGraphExamples import GG1
from simkit.rand import RandomVariate
from simkit.base import EventList
from simkit.simutil import SimpleStateChangeDumper
from simkit.stats import SimpleStatsTimeVarying

EventList.cold_reset()

interarrival_time_generator = RandomVariate.instance("Exponential", mean=2.0)
# Note the parameters for the Gamma RandomVariate
service_time_generator = RandomVariate.instance("Gamma", alpha=1.5, beta=1.2)

gg1 = GG1(interarrival_time_generator, service_time_generator)
print(gg1.describe())

# This was used when debugging, but is commented out for "production" runs
# If errors pop up, uncomment to see state transitions as they occur
simple_state_dumper = SimpleStateChangeDumper()
# gg1.add_state_change_listener(simple_state_dumper)

# SimpleStatsTimeVarying works by "listening" for specific state transitions.
# Each one then updates by computing the area under the curve as each state changes
number_in_queue_stat = SimpleStatsTimeVarying("number_in_queue")
number_available_servers_stat = SimpleStatsTimeVarying("number_available_servers")

# Like SimpleStateChangeDumper, the SimpleStatsTimeVarying objects must explicitly "listen" to
# an Event Graph component, in this case the gg1 instance
gg1.add_state_change_listener(number_in_queue_stat)
gg1.add_state_change_listener(number_available_servers_stat)

EventList.verbose = False # Was True for debugging; False for long runs

# stop_time = 20.0
stop_time = 200000.0
EventList.stop_at_time(stop_time) # Stopping after a longer time

# These two calls are always made to execute the simulation
EventList.reset()
EventList.start_simulation()

print("\nSimulation ended at time {time:,.2f}\n".format(time=EventList.simtime))

# For SimpleStatsTimeVarying, use time_varying_mean() for the time-varying mean
print("Avg # in queue: {avg:,.4f}".format(avg=number_in_queue_stat.time_varying_mean()))
print("Avg # available servers: {avg:,.4f}".format(avg=number_available_servers_stat.time_varying_mean()))
# Utilization is the percent of time the server was busy
print("Avg utilization: {util:,.2f}%".format(util = 100 * (1 - number_available_servers_stat.time_varying_mean())))