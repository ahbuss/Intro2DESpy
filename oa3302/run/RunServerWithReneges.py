from simkit.rand import RandomVariate
from simkit.base import EventList
from simkit.simutil import SimpleStateChangeDumper
from simkit.stats import SimpleStatsTally, SimpleStatsTimeVarying, CollectionSizeTimeVarying
from oa3302.EventGraphModelsWithEntities import ServerWithReneges

interarrival_time_generator = RandomVariate.instance("Exponential", mean=1.5)
service_time_generator = RandomVariate.instance("Gamma", alpha=2.5, beta=1.2)
total_number_servers = 2;
renege_time_generator = RandomVariate.instance("Uniform", min=4.0, max=6.0)

server_with_reneges = ServerWithReneges(interarrival_time_generator, service_time_generator, total_number_servers,\
                                        renege_time_generator)

simple_state_change_dumper = SimpleStateChangeDumper()
# server_with_reneges.add_state_change_listener(simple_state_change_dumper)

delay_in_queue_served_stat = SimpleStatsTally("delay_in_queue_served")
delay_in_queue_renege_stat = SimpleStatsTally("delay_in_queue_reneged")
time_in_system_served_stat = SimpleStatsTally("time_in_system_served")
number_in_queue_stat = CollectionSizeTimeVarying("queue")
number_available_servers_stat = SimpleStatsTimeVarying("number_available_servers")

server_with_reneges.add_state_change_listener(delay_in_queue_renege_stat)
server_with_reneges.add_state_change_listener(delay_in_queue_served_stat)
server_with_reneges.add_state_change_listener(time_in_system_served_stat)
server_with_reneges.add_state_change_listener(number_in_queue_stat)
server_with_reneges.add_state_change_listener(number_available_servers_stat)

print(server_with_reneges.describe())

EventList.verbose = False
# EventList.stop_on_event(4000, "leave")

EventList.stop_at_time(100000)
EventList.reset()
EventList.start_simulation()

print("\nSimulation ended at time {simtime:,.2f}".format(simtime=EventList.simtime))
print("{arrivals:,d} arrivals and {renege:,d} reneges".format(arrivals=server_with_reneges.number_arrivals, \
                                                              renege=server_with_reneges.number_reneges))
print("percent reneges: {percent:,.2f}%".format(percent=100 * server_with_reneges.number_reneges / server_with_reneges.number_arrivals))

print("\nAvg # in queue: {queue:,.4f}".format(queue=number_in_queue_stat.mean))
print("Avg utilization: {util:,.4f}".format(util=1.0 - number_available_servers_stat.time_varying_mean() / server_with_reneges.total_number_servers))
print("Avg delay in queue served: {avg:,.4f}".format(avg=delay_in_queue_served_stat.mean))
print("Avg delay in queue reneged: {avg:,.4f}".format(avg=delay_in_queue_renege_stat.mean))
print("Avg time in system (served): {avg:,.4f}".format(avg=time_in_system_served_stat.mean))