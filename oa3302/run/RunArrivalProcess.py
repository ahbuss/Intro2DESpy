# These are the imports needed to run the ArrivalProcess component
# It is preferred to explicitly import each class to be clear as to which one is being utilized
# However, one could use "import oa3302.EventGraphExamples", import simkit.base", etc instead
from oa3302.EventGraphExamples import ArrivalProcess
from simkit.rand import RandomVariate
from simkit.base import EventList
from simkit.simutil import SimpleStateChangeDumper

# This is to clear previous objects when running in an interactive console environment (like Spyder)
EventList.cold_reset()

# This is how to instantiate a RandomVariate object
# Each RandomVariate class has its own set of parameters - see the documentation
interarrival_time_generator = RandomVariate.instance("Exponential", mean=1.7)

# Instantiate an ArrivalProcess, which requires a RandomVariate to its constructor
# ArrivalProcess is an "Event Graph component" - that is, a class that can schedule and execute
# events and perform state transitions
arrival_process = ArrivalProcess(interarrival_time_generator)
print(arrival_process.describe()) # describe() verifies that the argument(s) passed have been received

# The SimpleStateDumper class prints state transitions to the command line
# whenever a notify_state_change() is called
simple_state_dumper = SimpleStateChangeDumper()
# To do this, it must "listen" to the Event Graph component
arrival_process.add_state_change_listener(simple_state_dumper)

# EventList.verbose = True tells the EventList to print each event as it occurs, together with all pending events
EventList.verbose = True
# This tells the EventList to end the simulation at the given time.
# It does this by creating a "Stopper" instance and scheduling a "Stop" event at the given time
EventList.stop_at_time(20.0)

# EventList.reset() does several things:
#  1. Clears the event list and sets simtime to 0.0
#  2. Calls reset() on all Event Graph components
#  3. Schedules all "Run" events (called "run" in DESpy)
EventList.reset()

# This starts the simulation by running the event list algorithm: while there are pending
# events, advance simtime and execute the next event.
EventList.start_simulation()

print("Simulation ended at time {time:,.2f}".format(time=EventList.simtime))
print("There have been {num:,d} arrivals".format(num=arrival_process.number_arrivals))