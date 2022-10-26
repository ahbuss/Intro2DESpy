from oa3302.EventGraphExamples import ResourcePriority
from simkit.rand import RandomVariate
from simkit.base import EventList
from simkit.simutil import SimpleStateChangeDumper
from simkit.stats import SimpleStatsTimeVarying

EventList.cold_reset()

interarrival_time_generator = RandomVariate.instance("Exponential", mean=1.1)

service_time_generator_1 = RandomVariate.instance("Gamma", alpha=1.5, beta=1.2)
service_time_generator_2 = RandomVariate.instance("Gamma", alpha=2.0, beta=1.2)

resource_priority = ResourcePriority(interarrival_time_generator, service_time_generator_1, service_time_generator_2)
print(resource_priority.describe())

simple_state_dumper = SimpleStateChangeDumper()
# resource_priority.add_state_change_listener(simple_state_dumper)

number_in_queue_stat = SimpleStatsTimeVarying("number_in_queue")
number_available_servers_stat_1 = SimpleStatsTimeVarying("number_available_servers_1")
number_available_servers_stat_2 = SimpleStatsTimeVarying("number_available_servers_2")

resource_priority.add_state_change_listener(number_in_queue_stat)
resource_priority.add_state_change_listener(number_available_servers_stat_1)
resource_priority.add_state_change_listener(number_available_servers_stat_2)

EventList.verbose = False

EventList.stop_at_time(200000.0)

EventList.reset()
EventList.start_simulation()

print("\nSimulation ended at time {time:,.2f}\n".format(time=EventList.simtime))

print("Avg # in queue: {avg:,.4f}".format(avg=number_in_queue_stat.time_varying_mean()))

print("Avg utilization server 1: {util:,.2f}%".format(util=100 * (1 - number_available_servers_stat_1.time_varying_mean())))
print("Avg utilization server 2: {util:,.2f}%".format(util=100 * (1 - number_available_servers_stat_2.time_varying_mean())))
