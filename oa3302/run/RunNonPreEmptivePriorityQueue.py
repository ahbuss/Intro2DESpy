from oa3302.EventGraphExamples import NonPreEmptivePriorityQueue
from simkit.rand import RandomVariate
from simkit.base import EventList
from simkit.simutil import SimpleStateChangeDumper
from simkit.stats import SimpleStatsTimeVarying

EventList.cold_reset()

interarrival_time_generator_1 = RandomVariate.instance("Exponential", mean=5.1)
interarrival_time_generator_2 = RandomVariate.instance("Exponential", mean=3.1)
service_time_generator_1 = RandomVariate.instance("Gamma", alpha=1.5, beta=1.2)
service_time_generator_2 = RandomVariate.instance("Gamma", alpha=2.0, beta=1.2)

non_pre_emptive_priority_queue = NonPreEmptivePriorityQueue(interarrival_time_generator_1, interarrival_time_generator_2,
                                                            service_time_generator_1, service_time_generator_2)
print(non_pre_emptive_priority_queue.describe())

simple_state_dumper = SimpleStateChangeDumper()
# non_pre_emptive_priority_queue.add_state_change_listener(simple_state_dumper)

number_in_queue_1_stat = SimpleStatsTimeVarying("number_in_queue_1")
number_in_queue_2_stat = SimpleStatsTimeVarying("number_in_queue_2")
number_available_servers_stat = SimpleStatsTimeVarying("number_available_servers")

non_pre_emptive_priority_queue.add_state_change_listener(number_in_queue_1_stat)
non_pre_emptive_priority_queue.add_state_change_listener(number_in_queue_2_stat)
non_pre_emptive_priority_queue.add_state_change_listener(number_available_servers_stat)

EventList.verbose = False

EventList.stop_at_time(200000.0)

EventList.reset()
EventList.start_simulation()

print("\nSimulation ended at time {time:,.2f}\n".format(time=EventList.simtime))

print("Avg # type 1 in queue: {avg:,.4f}".format(avg=number_in_queue_1_stat.time_varying_mean()))
print("Avg # type 2 in queue: {avg:,.4f}".format(avg=number_in_queue_2_stat.time_varying_mean()))

print("Avg utilization: {util:,.2f}%".format(util=100 * (1 - number_available_servers_stat.time_varying_mean())))
