from oa3302.EventGraphExamples import TandemQueue
from simkit.simutil import SimpleStateChangeDumper
from simkit.base import EventList
from simkit.rand import RandomVariate
from simkit.stats import SimpleStatsTimeVarying

EventList.cold_reset()

interarrival_time_generator = RandomVariate.instance("Exponential", mean=2.4)

service_time_generator_1 = RandomVariate.instance("Gamma", alpha=1.4, beta=1.2)
service_time_generator_2 = RandomVariate.instance("Gamma", alpha=1.7, beta=1.2)

tandem_queue = TandemQueue(interarrival_time_generator, service_time_generator_1, service_time_generator_2)
print(tandem_queue.describe())

simple_state_change_dumper = SimpleStateChangeDumper()
# tandem_queue.add_state_change_listener(simple_state_change_dumper)

number_in_queue_1_stat = SimpleStatsTimeVarying("number_in_queue_1")
number_in_queue_2_stat = SimpleStatsTimeVarying("number_in_queue_2")
number_available_servers_stat_1 = SimpleStatsTimeVarying("number_available_servers_1")
number_available_servers_stat_2 = SimpleStatsTimeVarying("number_available_servers_2")

tandem_queue.add_state_change_listener(number_in_queue_1_stat)
tandem_queue.add_state_change_listener(number_in_queue_2_stat)
tandem_queue.add_state_change_listener(number_available_servers_stat_1)
tandem_queue.add_state_change_listener(number_available_servers_stat_2)

EventList.verbose = False
EventList.stop_at_time(200000.0)

EventList.reset()
EventList.start_simulation()

print("\nSimulation ended at time {:,}\n".format(EventList.simtime))
print("avg # in queue 1: {:,.4f}".format(number_in_queue_1_stat.mean))
print("avg # in queue 2: {:,.4f}".format(number_in_queue_2_stat.mean))
print("Avg utilization server 1: {util:,.2f}%".format(util=100 * (1 - number_available_servers_stat_1.time_varying_mean())))
print("Avg utilization server 2: {util:,.2f}%".format(util=100 * (1 - number_available_servers_stat_2.time_varying_mean())))
