from simkit.base import EventList
from simkit.simutil import SimpleStateChangeDumper
from simkit.rand import RandomVariate
from simkit.stats import SimpleStatsTally, CollectionSizeTimeVarying, SimpleStatsTimeVarying
from oa3302.MoreEventGraphExamples import GGkWithEntities

interarrival_time_generator = RandomVariate.instance("Exponential", mean=1.7)
number_servers = 2
service_time_generator = RandomVariate.instance("Gamma", alpha=1.7, beta=1.8)

ggk = GGkWithEntities(interarrival_time_generator, number_servers, service_time_generator)
print(ggk.describe())

simple_state_change_dumper = SimpleStateChangeDumper()
# ggk.add_state_change_listener(simple_state_change_dumper)

delay_in_queue_stat = SimpleStatsTally("delay_in_queue")
time_in_system_stat = SimpleStatsTally("time_in_system")
number_in_queue_stat = CollectionSizeTimeVarying("queue")
number_available_servers_stat = SimpleStatsTimeVarying("number_available_servers")

ggk.add_state_change_listener(delay_in_queue_stat)
ggk.add_state_change_listener(time_in_system_stat)
ggk.add_state_change_listener(number_in_queue_stat)
ggk.add_state_change_listener(number_available_servers_stat)

number_service_completions = 100000
EventList.stop_on_event(number_service_completions, "end_service")

print("\nSimulation will be run for {num:,d} service completions".format(num=number_service_completions))
EventList.verbose = False

EventList.reset()
EventList.start_simulation()

print("Simulation ended at time {time:,.3f}".format(time=EventList.simtime))
print("\nAvg # in queue: {avg:,.4f}".format(avg=number_in_queue_stat.time_varying_mean()))
print("Avg utilization: {avg:,.4f}".format(avg=1.0 - number_available_servers_stat.time_varying_mean()/ggk.total_number_servers))
print("Avg delay in queue: {avg:,.4f}".format(avg=delay_in_queue_stat.mean))
print("Avg time in system: {avg:,.4f}".format(avg=time_in_system_stat.mean))
