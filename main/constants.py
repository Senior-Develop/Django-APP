from datetime import datetime

STOP = 0
MOVE = 1
BR_FILTER = 0.5

D_STOP_RADIUS = 0.1 
V_STOP_MAX = 3 #m/s
T_STOP_MIN = 4 * 60 #sec
C_CONT_STOP_MIN = 2 #points count
T_MOVE_MIN = 1 * 60 #sec
D_MOVE_MIN = 2 #km
C_CONT_MOVE_MIN = 2 #count number of cordinate points with v > V_STOP_MAX
C_SEG_MOVE_MIN = 4 #count number of cordinate points with v > V_STOP_MAX
BR_CHG_SEG_MAX = 100 #degrees - MOVE segments with a mean bearing charge > this will be set to a STOP segment
ACCR_FILTER_LIMIT = 1000
ACCR_FILTER_LIMIT_LOW = 200
ACCR_FILTER_LIMIT_OSRM = 350
FREQ_LOC_RADIUS_KM = 0.2 
MY_CHARGE_LOC_OPTION_COUNT = 10 #present this many frequent locations to choose charging locations from
MY_CHRG_LOC_I = [0, 1] #this will be user input - which frequent locations are charge 
LOW_CHARGE_LIMIT_PERCENT = 0.10
QUICK_CHARGE_UPPER_LIMIT_PERCENT = 0.80
T_FLIGHT_MIN = 60 * 60 #seconds = 1 hr

#unit conversions
KM_PER_MILE = 1.60934
EARTH_RADIUS_KM = 6371.008667

#user inputs
MY_CHRG_LOC_TYPES = ['240v', '120v']
MY_CHRG_NAMES = ['Home', 'Work']
MY_VEHICLE_IDS = [41276, 41190]

TIME_FRAME = [datetime(2019, 8, 29) , datetime(2019, 9, 7)] #Josh subset - Prescott 

ACTIVITY_TIME_DELTA = 5000 #miliseconds
KEEP_ACTIVITY_TYPE_COUNT = 4
IGNORE_ACTIVITY_TYPE = ['TILTING','UNKNOWN']
#VEHICLE_ACTIVITY_HEADER = ['IN_CAR_CONF', 'IN_RAIL_VEHICLE_CONF', 'IN_BUS_CONF', 'IN_TWO_WHEELER_VEHICLE_CONF']
#VEHICLE_ACTIVITY_HEADER = ['IN_ROAD_VEHICLE_CONF', 'IN_RAIL_VEHICLE_CONF']
VEHICLE_ACTIVITY_HEADER = ['IN_VEHICLE_CONF']
NON_VEHICLE_ACTIVITY_HEADER = ['STILL_CONF', 'ON_FOOT_CONF', 'ON_BICYCLE_CONF', 'UNKNOWN_CONF']
#EV_INCLUDE_ACTIVITY_TYPE = ['IN_ROAD_VEHICLE']
#EV_INCLUDE_ACTIVITY_TYPE = ['IN_VEHICLE']
EV_INCLUDE_ACTIVITY_TYPE = ['IN_PASSENGER_VEHICLE', 'IN_VEHICLE']

ENERGY_COST = {'Electricity': 0.1053, 'Wind': 0.1153, 'Regular Gasoline': 2.581, 'Midgrade Gasoline': 2.913, 'Premium Gasoline': 3.175, 'Diesel': 3.012} #dolars per kwh or gallon
#source: https://www.eia.gov/electricity/state/
#could use API: https://www.eia.gov/opendata/qb.php?category=711295

FUEL_GHG = {'Electricity': 0.707, 'Wind': 0.011, 'Regular Gasoline': 8.9, 'Midgrade Gasoline': 8.9, 'Premium Gasoline': 8.9, 'Diesel': 10.19} #kg per kwh or gallon
#source: https://www.epa.gov/energy/greenhouse-gas-equivalencies-calculator
#source: https://www.epa.gov/energy/greenhouse-gas-equivalencies-calculator
#source: https://www.epa.gov/energy/greenhouse-gas-equivalencies-calculator
#source: https://en.wikipedia.org/wiki/Life-cycle_greenhouse-gas_emissions_of_energy_sources

LOC_HIST_FILE_SUBDIR = "loc_hist/"
