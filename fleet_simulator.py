# src/fleet_simulator.py
import os
import json
import time
import sys
import asyncio

# Connect root path for configurations and optimizer access
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.route_optimizer import SupplyChainOptimizer

class FleetSimulator:
    def __init__(self):
        self.optimizer = SupplyChainOptimizer()
        self.primary_wh = self.optimizer.primary_wh

    async def stream_fleet_telemetry(self):
        """Generates a step-by-step rolling broadcast of active trucks moving on their routes"""
        print("📡 Fleet Simulator Engine ignited. Analyzing routing matrices...")
        optimized_routes = self.optimizer.optimize_routes()
        
        if not optimized_routes:
            yield json.dumps({"status": "error", "message": "No active routes to simulate."})
            return

        # Continuous loops to simulate persistent business operations
        while True:
            print("🚚 Starting a new morning delivery dispatch shift...")
            
            for route in optimized_routes:
                route_id = route["route_id"]
                orders = route["assigned_orders"]
                
                # Start vehicle at primary hub station coordinates
                curr_x, curr_y = self.primary_wh["x_coord"], self.primary_wh["y_coord"]
                
                # Broadcast initial departure event
                yield {
                    "event": "DISPATCHED",
                    "truck_id": route_id,
                    "location_name": self.primary_wh["name"],
                    "x": curr_x,
                    "y": curr_y,
                    "current_load_kg": route["total_weight_kg"],
                    "accumulated_cost_usd": 0.0,
                    "log_message": f"Truck {route_id} departed from main hub with {len(orders)} shipments."
                }
                await asyncio.sleep(1.5)  # Brief pause between route tracking updates

                accumulated_cost = 0.0
                
                # Move through each package drop point sequentially
                for order in orders:
                    # Calculate distance metrics to this stop
                    distance_chunk = self.optimizer.calculate_distance(curr_x, curr_y, order["dest_x"], order["dest_y"])
                    
                    # Update simulated financial accumulation metrics
                    from config.logistics_config import BASE_FUEL_COST_PER_KM, DRIVER_WAGE_PER_HOUR, AVERAGE_SPEED_KMH
                    time_taken = distance_chunk / AVERAGE_SPEED_KMH
                    accumulated_cost += (distance_chunk * BASE_FUEL_COST_PER_KM) + (time_taken * DRIVER_WAGE_PER_HOUR)
                    
                    # Relocate vehicle to stop
                    curr_x, curr_y = order["dest_x"], order["dest_y"]
                    
                    yield {
                        "event": "DELIVERED",
                        "truck_id": route_id,
                        "location_name": order["destination_name"],
                        "x": curr_x,
                        "y": curr_y,
                        "current_load_kg": order["weight_kg"],
                        "accumulated_cost_usd": round(accumulated_cost, 2),
                        "log_message": f"Successfully delivered Order {order['order_id']} to {order['destination_name']}."
                    }
                    await asyncio.sleep(2.0)  # Sleep represents drop-off processing delay

                # Final trip segment: Return journey back to base hub
                final_return_dist = self.optimizer.calculate_distance(curr_x, curr_y, self.primary_wh["x_coord"], self.primary_wh["y_coord"])
                return_time = final_return_dist / AVERAGE_SPEED_KMH
                accumulated_cost += (final_return_dist * BASE_FUEL_COST_PER_KM) + (return_time * DRIVER_WAGE_PER_HOUR)
                
                yield {
                    "event": "RETURNED",
                    "truck_id": route_id,
                    "location_name": self.primary_wh["name"],
                    "x": self.primary_wh["x_coord"],
                    "y": self.primary_wh["y_coord"],
                    "current_load_kg": 0,
                    "accumulated_cost_usd": round(accumulated_cost, 2),
                    "log_message": f"Truck {route_id} completed loop and returned to Mumbai Central Hub safely."
                }
                await asyncio.sleep(1.5)

            print("😴 Shift completed. Resetting simulation loop...")
            await asyncio.sleep(5)  # Delay between warehouse dispatch cycles