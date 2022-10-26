from oa3302.EventGraphModelsWithEntities import MultipleServerQueue
from simkit.rand import RandomVariate
from simkit.base import EventList
from simkit.simutil import SimpleStateChangeDumper
from simkit.stats import SimpleStatsTally, SimpleStatsTimeVarying, CollectionSizeTimeVarying

interarrival_time_generator = RandomVariate.instance("Exponential", mean=1.7)
service_time_generator = RandomVariate.instance("Gamma", alpha=1.7, beta=1.8)
total_number_servers = 2;

multiple_server_queue = MultipleServerQueue(interarrival_time_generator, service_time_generator, total_number_servers)
print(multiple_server_queue.describe())

simple_state_change_dumper = SimpleStateChangeDumper()
# multiple_server_queue.add_state_change_listener(simple_state_change_dumper)

delay_in_queue_stat = SimpleStatsTally("delay_in_queue")
time_in_system_stat = SimpleStatsTally("time_in_system")
number_available_servers_stat = SimpleStatsTimeVarying("number_available_servers")
number_in_queue_stat = CollectionSizeTimeVarying("queue")

multiple_server_queue.add_state_change_listener(delay_in_queue_stat)
multiple_server_queue.add_state_change_listener(time_in_system_stat)
multiple_server_queue.add_state_change_listener(number_available_servers_stat)
multiple_server_queue.add_state_change_listener(number_in_queue_stat)

EventList.verbose = False
# EventList.stop_at_time(100000.0)

EventList.stop_on_event(100000, "leave")
EventList.reset()
EventList.start_simulation()

print("Simulation ended at time {time:,.2f}".format(time=EventList.simtime))

print("Avg delay in queue: {delay:.4f}".format(delay=delay_in_queue_stat.mean))
print("Avg time in system: {time:.4f}".format(time=time_in_system_stat.mean))
utlization = 1.0 - number_available_servers_stat.time_varying_mean() / multiple_server_queue.total_number_servers
print("Avg Utilization: {util:.4f}".format(util=utlization))
arrival_rate = (delay_in_queue_stat.count + multiple_server_queue.queue.__len__() ) / EventList.simtime

print("Avg number in queue: {avg:.4f}".format(avg=number_in_queue_stat.time_varying_mean()))
little_delay = number_in_queue_stat.time_varying_mean() / arrival_rate

print("Avg delay (Little): {avg:.4f}".format(avg=little_delay))
