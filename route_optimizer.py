# src/route_optimizer.py
import os
import json
import numpy as np
import pandas as pd
import sys

# Connect root path for configurations
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.logistics_config import FLEET_VEHICLE_CAPACITY_KG, BASE_FUEL_COST_PER_KM, DRIVER_WAGE_PER_HOUR, AVERAGE_SPEED_KMH

class SupplyChainOptimizer:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.warehouses = self._load_warehouses()
        self.primary_wh = next((wh for wh in self.warehouses if wh['is_primary']), self.warehouses[0])

    def _load_warehouses(self):
        with open(os.path.join(self.base_dir, "data", "warehouses.json"), "r") as f:
            return json.load(f)["warehouses"]

    def calculate_distance(self, x1, y1, x2, y2):
        """Calculates straight-line Euclidean distance between grid points"""
        return float(np.sqrt((x2 - x1)**2 + (y2 - y1)**2))

    def optimize_routes(self):
        """Groups pending shipments into optimized vehicle loads to minimize total cost"""
        orders_path = os.path.join(self.base_dir, "data", "shipment_orders.csv")
        if not os.path.exists(orders_path):
            print("❌ Error: shipment_orders.csv not found.")
            return []

        df_orders = pd.read_csv(orders_path)
        
        # Convert orders to a list of dictionaries for iterative clustering
        pending_orders = df_orders.to_dict(orient="records")
        optimized_routes = []
        
        # Start the clustering logic
        while len(pending_orders) > 0:
            current_route_orders = []
            current_weight = 0.0
            
            # Anchor route to the primary distribution hub coordinates
            curr_x, curr_y = self.primary_wh["x_coord"], self.primary_wh["y_coord"]
            
            while True:
                best_next_index = None
                best_distance = float('inf')
                
                # Look for the closest unassigned delivery point that fits weight capacity limits
                for idx, order in enumerate(pending_orders):
                    if current_weight + order["weight_kg"] <= FLEET_VEHICLE_CAPACITY_KG:
                        dist = self.calculate_distance(curr_x, curr_y, order["dest_x"], order["dest_y"])
                        if dist < best_distance:
                            best_distance = dist
                            best_next_index = idx
                
                # If no remaining orders can fit in this vehicle, dispatch it
                if best_next_index == None:
                    break
                
                # Pull the selected order and add it to the active truck asset array
                selected_order = pending_orders.pop(best_next_index)
                current_route_orders.append(selected_order)
                current_weight += selected_order["weight_kg"]
                
                # Move our tracking cursor to the new dropoff location coordinate point
                curr_x, curr_y = selected_order["dest_x"], selected_order["dest_y"]
            
            # Calculate total economic metrics for this individual route loop
            route_distance = 0.0
            prev_x, prev_y = self.primary_wh["x_coord"], self.primary_wh["y_coord"]
            
            for order in current_route_orders:
                route_distance += self.calculate_distance(prev_x, prev_y, order["dest_x"], order["dest_y"])
                prev_x, prev_y = order["dest_x"], order["dest_y"]
            
            # Add return journey back to primary hub
            route_distance += self.calculate_distance(prev_x, prev_y, self.primary_wh["x_coord"], self.primary_wh["y_coord"])
            
            transit_time_hours = route_distance / AVERAGE_SPEED_KMH
            fuel_cost = route_distance * BASE_FUEL_COST_PER_KM
            labor_cost = transit_time_hours * DRIVER_WAGE_PER_HOUR
            total_financial_cost = fuel_cost + labor_cost
            
            optimized_routes.append({
                "route_id": f"TRUCK-ROUTE-{len(optimized_routes) + 1}",
                "assigned_orders": current_route_orders,
                "total_weight_kg": current_weight,
                "total_distance_km": round(route_distance, 2),
                "estimated_time_hours": round(transit_time_hours, 2),
                "calculated_cost_usd": round(total_financial_cost, 2)
            })
            
        return optimized_routes

if __name__ == "__main__":
    print("🚛 Running Standalone Logistics Core Diagnostics...")
    optimizer = SupplyChainOptimizer()
    results = optimizer.optimize_routes()
    
    for route in results:
        print(f"\n🔹 {route['route_id']} Verified:")
        print(f"  📦 Load: {route['total_weight_kg']}kg / {FLEET_VEHICLE_CAPACITY_KG}kg")
        print(f"  🛣️ Distance: {route['total_distance_km']} km")
        print(f"  💰 Run Cost: ${route['calculated_cost_usd']}")
        print(f"  🎯 Drops: {[o['order_id'] for o in route['assigned_orders']]}")