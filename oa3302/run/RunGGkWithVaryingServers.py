from oa3302.MoreEventGraphExamples import GGkWithVaryingServers
from simkit.rand import RandomVariate
from simkit.base import EventList
from simkit.simutil import SimpleStateChangeDumper
from simkit.stats import SimpleStatsTimeVarying

EventList.cold_reset()

interarrival_time_generator = RandomVariate.instance("Exponential", mean=1.0)
service_time_generator = RandomVariate.instance("Gamma", alpha=1.5, beta=1.2)

threshold = 3
ggk_with_varying_servers = GGkWithVaryingServers(interarrival_time_generator, service_time_generator, threshold)
print(ggk_with_varying_servers.describe())

simple_state_dumper = SimpleStateChangeDumper()
# ggk_with_varying_servers.add_state_change_listener(simple_state_dumper)

number_in_queue_stat = SimpleStatsTimeVarying("number_in_queue")
number_available_servers_stat = SimpleStatsTimeVarying("number_available_servers")
total_number_servers_stat = SimpleStatsTimeVarying("total_number_servers")

ggk_with_varying_servers.add_state_change_listener(number_in_queue_stat)
ggk_with_varying_servers.add_state_change_listener(number_available_servers_stat)
ggk_with_varying_servers.add_state_change_listener(total_number_servers_stat)

EventList.verbose = False # Was True for debugging; False for long runs

# The ending criterion is this many leave events
number_leave_events = 100000
# This instructs the EventList to end after number_leave_events 'leave' events
EventList.stop_on_event(number_leave_events, "leave")
print("\nSimulation will be run for {num:,d} leave events".format(num=number_leave_events))

EventList.reset()
EventList.start_simulation()

print("\nSimulation ended at time {time:,.2f}\n".format(time=EventList.simtime))

print("Avg # in queue: {avg:,.4f}".format(avg=number_in_queue_stat.time_varying_mean()))
print("Avg # available servers: {avg:,.4f}".format(avg=number_available_servers_stat.time_varying_mean()))
print("Avg total #  servers: {avg:,.4f}".format(avg=total_number_servers_stat.time_varying_mean()))
print("Max # servers: {max:,d}".format(max=total_number_servers_stat.max))