from simkit.rand import RandomVariate
from simkit.base import EventList
from simkit.stats import SimpleStatsTimeVarying
from simkit.simutil import SimpleStateChangeDumper
from oa3302.MoreEventGraphExamples import GGk
"""
This illustrates how to run multiple replications with diferent parameter values.
Since this is still only giving one replication per parameter value, it doesn't
have statistical validity.
"""
EventList.cold_reset()

interarrival_time_generator = RandomVariate.instance("Exponential", mean=2.0)
service_time_generator = RandomVariate.instance("Uniform", min=3.0, max=6.0)
total_number_servers = 1

ggk = GGk(interarrival_time_generator, service_time_generator, total_number_servers)
print(ggk.describe())

simple_state_change_dumper = SimpleStateChangeDumper()
# ggk.add_state_change_listener(simple_state_change_dumper)

number_in_queue_stat = SimpleStatsTimeVarying("number_in_queue")
ggk.add_state_change_listener(number_in_queue_stat)

EventList.verbose = False
# Each replication will end after 10,000 leave events
EventList.stop_on_event(10000, "leave")

# replications are wrapped in a 'for' loop
for k in range(1,5):
    ggk.total_number_servers = k # Each pass through the loop increments total_number_servers
    EventList.reset()  # Re-initializes state variables, sets simtime to 0.0 and schedules run events
    number_in_queue_stat.reset() # since the same stats object is being re-used, it must be reset() "manually"
    EventList.start_simulation() # run this replication and print the result

    print("{k:,d} servers, Avg # in queue: {avg:,.4f}".format(k=ggk.total_number_servers, avg=number_in_queue_stat.time_varying_mean()))