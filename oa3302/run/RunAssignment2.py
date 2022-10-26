from oa3302.SimpleInventoryModel import InventoryModel
from simkit.rand import RandomVariate
from simkit.base import EventList
from simkit.stats import SimpleStatsTimeVarying
from simkit.stats import SimpleStatsTally
from math import sqrt
from simkit.quantiles import student_t
# Create the RandomVariates to be used
inter_demand_generator = RandomVariate.instance("Exponential", mean=1.3)
demand_generator = RandomVariate.instance("Discrete", values=[1,2,3,4,5], frequencies=[0.20, 0.30, 0.60, 0.50, 0.40])
lead_time_generator = RandomVariate.instance("Gamma", alpha=2.3, beta=1.8)

# Initial parameters - reorder_point will take on different values in the loop
initial_on_hand = 20
order_quantity = 20;
reorder_point = 1

# Instantiate the InventoryModel object and verify parameters
inventory_model = InventoryModel(inter_demand_generator, demand_generator, lead_time_generator, initial_on_hand, \
                                 reorder_point, order_quantity)
print(inventory_model.describe())

# Instantiate the statistics objects
on_hand_stat = SimpleStatsTimeVarying("on_hand")
backorder_stat = SimpleStatsTimeVarying("backorder")
on_order_stat = SimpleStatsTimeVarying("on_order")
# Note that the one for filled is a SimpleStatsTally
filled_stat = SimpleStatsTally("filled")

# Have them all "listen" to inventory_model
inventory_model.add_state_change_listener(on_hand_stat)
inventory_model.add_state_change_listener(backorder_stat)
inventory_model.add_state_change_listener(on_order_stat)
inventory_model.add_state_change_listener(filled_stat)

# Sun for 100,000 time units
stop_time = 100000;
EventList.stop_at_time(stop_time)
print("\nSimulations will be run for {:,.0f} time units".format(stop_time))

# Let's brute fore it and hope for the best ...
for reorder_point in range(16, 21):
    # Set this run's reorder_point
    inventory_model.reorder_point = reorder_point
    # Reset EventList
    EventList.reset()
    # Reset each of the stats objects
    on_hand_stat.reset()
    backorder_stat.reset()
    on_hand_stat.reset()
    filled_stat.reset()
    # Run the simulation
    EventList.start_simulation()

    # Note that the time-varying stats use time_varying_mean() but the tally stat for filled
    # simply uses mean
    print("\nreorder_point: {reorder_point:d}".format(reorder_point=inventory_model.reorder_point))
    print("Avg on_hand: {:.3f}".format(on_hand_stat.time_varying_mean()))
    print("Avg backorder: {:.3f}".format(backorder_stat.time_varying_mean()))
    print("Avg on_order: {:.3f}".format(on_order_stat.time_varying_mean()))
    print("Avg fill rate: {:.2f}%".format(100*filled_stat.mean))

"""
The following part wasn't part of the assignment. However, coming to conclusions based on a single replication
is not good practice. Therefore, let's take the reorder point that did give a fill rate above 90%, 18,
and run 30 independent replications of that value to compute a confidence interval for the fill rate
at that reorder point.
"""
inventory_model.reorder_point = 18
overall_fill_rate_stat = SimpleStatsTally("mean fill rate")
number_reps = 30
print("\nNow run for {rep:,d} replications and reorder_point {rop:,d}".\
      format(rep=number_reps, rop=inventory_model.reorder_point))
for rep in range(0,number_reps):
    EventList.reset()
    # Reset each of the stats objects
    on_hand_stat.reset()
    backorder_stat.reset()
    on_hand_stat.reset()
    filled_stat.reset()
    # Run the simulation
    EventList.start_simulation()
    # Each replication gives 1 independent estimate of fill rate via filled_stat.mean,
    # so finding the mean of these, together with the standard deviation, will allow us
    # to compute a confidence interval for the fill rate for a given reorder point
    overall_fill_rate_stat.new_observation(filled_stat.mean)

# Determine a 95% confidence interval for fill rate
mean = overall_fill_rate_stat.mean
std_dev = overall_fill_rate_stat.stdev
halfwidth = std_dev / sqrt(overall_fill_rate_stat.count) * student_t(0.925, overall_fill_rate_stat.count - 1)
print("95% CI for fill rate: {mean:,.2f} ± {hw:,.2f}".format(mean=mean * 100, hw=halfwidth * 100))