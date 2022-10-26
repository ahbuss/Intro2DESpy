from simkit.base import EventList
from simkit.rand import RandomVariate
from simkit.stats import SimpleStatsTimeVarying
from simkit.simutil import SimpleStateChangeDumper
from oa3302.MoreEventGraphExamples import GGk, ArrivalCounter

'''
This illustrates how to use Little's formula to estimate the average delay in queue 
and time in system. An ArrivalCounter instance is used to estimate the arrival rate.
This is also a simple example of sim_event_listener pattern.
'''
if __name__ == "__main__":
    interarrival_time_generator = RandomVariate.instance("Exponential", mean=1.7)
    service_time_generator = RandomVariate.instance("Gamma", alpha=1.7, beta=1.8)
    number_servers = 2

    ggk = GGk(interarrival_time_generator, service_time_generator, number_servers)

    arrival_counter = ArrivalCounter()
    ggk.add_sim_event_listener(arrival_counter)

    simple_state_change_dumper = SimpleStateChangeDumper()
    # ggk.add_state_change_listener(simple_state_change_dumper)
    # arrival_counter.add_state_change_listener(simple_state_change_dumper)

    number_in_queue_stat = SimpleStatsTimeVarying("number_in_queue")
    number_available_servers_stat = SimpleStatsTimeVarying("number_available_servers")

    ggk.add_state_change_listener(number_in_queue_stat)
    ggk.add_state_change_listener(number_available_servers_stat)

    print(ggk.describe())

    EventList.verbose = False

    number_arrivals = 100000
    EventList.stop_on_event(number_arrivals, "leave")

    print("\nSimulation ill be run for {num:,d} arrivals".format(num=number_arrivals))
    EventList.reset()
    EventList.start_simulation()

    print("Simulation ended at time {time:,.4f}".format(time=EventList.simtime))

    avg_number_in_system = number_in_queue_stat.time_varying_mean() + ggk.total_number_servers - \
        number_available_servers_stat.time_varying_mean()

    arrival_rate = arrival_counter.number_arrivals / EventList.simtime

    avg_time_in_system = avg_number_in_system / arrival_rate
    avg_delay_in_queue = number_in_queue_stat.time_varying_mean() / arrival_rate

    print("\nAvg delay in queue: {avg:,.4f}".format(avg=avg_delay_in_queue))
    print("Avg time in system: {avg:,.4f}".format(avg = avg_time_in_system))

