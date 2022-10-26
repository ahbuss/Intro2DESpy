from simkit.base import SimEntityBase
from math import nan


class InventoryModel(SimEntityBase):
    def __init__(self,demand_time_generator, lead_time_generator, demand_generator, initial_inventory, order_quantity, reorder_point):
        SimEntityBase.__init__(self)

        self.demand_time_generator = demand_time_generator #t_D
        self.lead_time_generator = lead_time_generator  # t_L
        self.demand_generator = demand_generator
        self.initial_inventory = initial_inventory
        self.order_quantity = order_quantity
        self.reorder_point = reorder_point

        self.inventory_amount = nan #OH
        self.backorder_amount = nan #BO
        self.amount_on_order = nan #OO
        self.order_possible = nan #F

    def reset(self):
        SimEntityBase.reset(self)
        self.inventory_amount = self.initial_inventory
        self.backorder_amount = 0
        self.amount_on_order = 0
        self.order_possible = nan

    def run(self):
        self.notify_state_change("inventory_amount", self.inventory_amount)
        self.notify_state_change("backorder_amount", self.backorder_amount)
        self.notify_state_change("amount_on_order", self.amount_on_order)

        self.schedule("demand", self.demand_time_generator.generate())

    def demand(self):
        demand = self.demand_generator.generate()
        if demand <= self.inventory_amount:
            self.order_possible = 1
        else:
            self.order_possible = 0
        self.notify_state_change("order_possible", self.order_possible)

        net = self.inventory_amount - self.backorder_amount - demand

        self.inventory_amount = max(0, net)
        self.notify_state_change("inventory_amount", self.inventory_amount)

        self.backorder_amount = max(0, -net)
        self.notify_state_change("backorder_amount", self.backorder_amount)

        self.schedule("demand", self.demand_time_generator.generate())

        if net + self.amount_on_order <= self.reorder_point:
            self.schedule("place_order", 0.0)

    def place_order(self):
        self.amount_on_order += self.order_quantity
        self.notify_state_change("amount_on_order", self.amount_on_order)

        self.schedule("order_arrives", self.lead_time_generator.generate())

    def order_arrives(self):
        self.amount_on_order -= self.order_quantity
        self.notify_state_change("amount_on_order", self.amount_on_order)

        net = self.inventory_amount - self.backorder_amount + self.order_quantity

        self.inventory_amount = max(0, net)
        self.notify_state_change("inventory_amount", self.inventory_amount)

        self.backorder_amount = max(0, -net)
        self.notify_state_change("backorder_amount", self.backorder_amount)

