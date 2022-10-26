from oa3302.EventGraphExamples import FailureModel
from simkit.base import EventList
from simkit.rand import RandomVariate
from simkit.stats import SimpleStatsTimeVarying
from simkit.simutil import SimpleStateChangeDumper

EventList.cold_reset()

interarrival_generator = RandomVariate.instance("Exponential", mean=2.2)
service_genarator = RandomVariate.instance("Gamma", alpha=1.2, beta=1.4)
failure_genarator = RandomVariate.instance("Gamma", alpha=3.4, beta=4.0)
repair_generator = RandomVariate.instance("Gamma", alpha=2.0, beta=2.0)

failureModel = FailureModel(interarrival_generator, service_genarator, failure_genarator, repair_generator)
print(failureModel.describe())

number_in_queue_stat = SimpleStatsTimeVarying("number_in_queue")
number_available_servers_stat = SimpleStatsTimeVarying("number_available_servers")
number_failed_servers_stat = SimpleStatsTimeVarying("number_failed_servers")

simple_state_dumper = SimpleStateChangeDumper()
# failureModel.add_state_change_listener(simple_state_dumper)

failureModel.add_state_change_listener(number_in_queue_stat)
failureModel.add_state_change_listener(number_available_servers_stat)
failureModel.add_state_change_listener(number_failed_servers_stat)

EventList.verbose = False
EventList.stop_at_time(200000.0)

EventList.reset()
EventList.start_simulation()

print("\nSimulation ended at time {time:,.2f}\n".format(time=EventList.simtime))

print("Avg # in queue: {avg:,.4f}".format(avg=number_in_queue_stat.time_varying_mean()))
print("Avg utilization: {util:,.2f}%".format(util = 100 * (1 - number_available_servers_stat.time_varying_mean())))
print("Avg # failed machines: {failed:,.4f}".format(failed=number_failed_servers_stat.time_varying_mean()))