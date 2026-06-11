# config/logistics_config.py

# Network Server Configuration
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8060  # Dedicated separate port for the Supply Chain Lab

# Fleet Operations Constraints
FLEET_VEHICLE_CAPACITY_KG = 2500.0  # Max cargo weight per truck
BASE_FUEL_COST_PER_KM = 1.20        # Cost in dollars per kilometer
DRIVER_WAGE_PER_HOUR = 25.00        # Hourly driver cost
AVERAGE_SPEED_KMH = 60.0            # Average fleet transit speed

# Optimization Scoring Weights
WEIGHT_DISTANCE = 0.6               # Priority multiplier for minimizing mileage
WEIGHT_TIME = 0.4                   # Priority multiplier for minimizing delivery time