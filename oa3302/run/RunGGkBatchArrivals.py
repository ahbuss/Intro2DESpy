from simkit.base import EventList
from simkit.rand import RandomVariate
from oa3302.MoreEventGraphExamples import GGkBatchArrivals
from simkit.simutil import SimpleStateChangeDumper
from simkit.stats import SimpleStatsTimeVarying

EventList.cold_reset()

interarrival_time_generator = RandomVariate.instance("Exponential", mean=2.0)
service_time_generator = RandomVariate.instance("Gamma", alpha=2.1, beta=1.5)
batch_generator = RandomVariate.instance("Discrete", values=[1,2,3,4], frequencies=[20,30,40,10])

ggk_batch_arrivals = GGkBatchArrivals(interarrival_time_generator, service_time_generator, 2, batch_generator)
print(ggk_batch_arrivals.describe())

simple_state_change_dumper = SimpleStateChangeDumper()
# ggk_batch_arrivals.add_state_change_listener(simple_state_change_dumper)

number_in_queue_stat = SimpleStatsTimeVarying("number_in_queue")
ggk_batch_arrivals.add_state_change_listener(number_in_queue_stat)

EventList.verbose = False
# EventList.stop_at_time(20.0)
number_service_completions = 20000
EventList.stop_on_event(number_service_completions, "leave")

print("Simulation will run for {:,d} service completions".format(number_service_completions))
for k in range(1,10):
    ggk_batch_arrivals.total_number_servers = k
    EventList.reset()
    number_in_queue_stat.reset()
    EventList.start_simulation()

    print("{k:,d} servers, Avg # in queue: {avg:,.4f}".format(k=k,avg=number_in_queue_stat.time_varying_mean()))