from oa3302.EventGraphExamples import RenegingAndBalking
from simkit.rand import RandomVariate, Triangular
from simkit.base import EventList
from simkit.simutil import SimpleStateChangeDumper
from simkit.stats import SimpleStatsTimeVarying

EventList.cold_reset()

interarrival_time_generator = RandomVariate.instance("Exponential", mean=1.5)
service_time_generator = RandomVariate.instance("Gamma", alpha=1.8, beta=1.2)
renege_time_generator = RandomVariate.instance("Uniform", min=2.0, max=6.0)
buffer = 3

reneging_and_balking = RenegingAndBalking(interarrival_time_generator, service_time_generator, renege_time_generator, buffer)
print(reneging_and_balking.describe())

simple_state_dumper = SimpleStateChangeDumper()
# reneging_and_balking.add_state_change_listener(simple_state_dumper)

number_in_queue_stat = SimpleStatsTimeVarying("number_in_queue")
number_available_servers_stat = SimpleStatsTimeVarying("number_available_servers")

reneging_and_balking.add_state_change_listener(number_in_queue_stat)
reneging_and_balking.add_state_change_listener(number_available_servers_stat)

EventList.verbose = False

EventList.stop_at_time(100000.0)

EventList.reset()
EventList.start_simulation()

print("Simulation ended at time {time:,.2f}".format(time=EventList.simtime))
print("Avg # in queue: {mean:,.4f}".format(mean=number_in_queue_stat.mean))
print("Avg utilization: {util:,.2f}%".format(util = 100 * (1 - number_available_servers_stat.time_varying_mean())))
print("% balks: {balks:,.2f}".format(balks=100*reneging_and_balking.number_balks / reneging_and_balking.number_arrivals))
print("% reneges: {reneges:,.2f}".format(reneges=100*reneging_and_balking.number_reneges / reneging_and_balking.number_arrivals))
print("% lost: {lost:,.2f}".format(lost = 100 * (reneging_and_balking.number_balks + reneging_and_balking.number_reneges) / reneging_and_balking.number_arrivals))