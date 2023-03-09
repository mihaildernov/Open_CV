from dronekit import *
import time
import math
import argparse
import dronekit_sitl
from pymavlink import mavutil

parser = argparse.ArgumentParser(description="commands")
parser.add_argument("--connect")
args = parser.parse_args()
connection_sting = args.connect
the_connection = mavutil.mavlink_connection('udpout:localhost:14540')

sitl = None

if not connection_sting:
    sitl = dronekit_sitl.start_default()
    connection_sting = sitl.connection_string()

vehicle = connect(connection_sting, wait_ready=True)
vehicle = connect()

def arm_and_takeoff(aTargetAltitude):
    print("Предполетные проверки")
    while not vehicle.is_armable:
        print("Ждем коптер...")
        time.sleep(1)
    print("Запускаем двигатели")

    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    while not vehicle.armed:
        print(" Ждем моторы...")
        time.sleep(1)
    print("Взлет!")
    vehicle.simple_takeoff(aTargetAltitude)

    while True:
        print(" Текущая высота: ", vehicle.location.global_relative_frame.alt)
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Поднялись на %d метров" % vehicle.location.global_relative_frame.alt)
            break
        time.sleep(1)

def recv_match(self, condition=None, type=None, blocking=False, timeout=None):

    '''Receive the next MAVLink message that matches the given type and condition
    type:        Message name(s) as a string or list of strings - e.g. 'SYS_STATUS'
    condition:   Condition based on message values - e.g. 'SYS_STATUS.mode==2 and SYS_STATUS.nav_mode==4'
    blocking:    Set to wait until message arrives before method completes.
    timeout:     ? <!-- timeout for blocking message when the system will return. Is this just a time? -->'''

    msg = the_connection.recv_match(blocking=True)
    # Wait for a 'SYS_STATUS' message with the specified values.
    msg = the_connection.recv_match(type='SYS_STATUS', condition='SYS_STATUS.mode==2 and SYS_STATUS.nav_mode==4',
                                    blocking=True)

def set_velocity_body(vehicle, vx, vy, vz):
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,
        0, 0,
        mavutil.mavlink.MAV_FRAME_BODY_NED,
        0b0000111111000111,  # -- BITMASK -> Consider only the velocities
        0, 0, 0,  # -- POSITION
        vx, vy, vz,  # -- VELOCITY
        0, 0, 0,  # -- ACCELERATIONS
        0, 0)
    vehicle.send_mavlink(msg)
    vehicle.flush()

arm_and_takeoff(20)
a_location = LocationGlobalRelative(-27.114346, -109.357912, 20)
vehicle.simple_goto(a_location)
vehicle.groundspeed = 7.5

def distance_to_current_waypoint():
    nextwaypoint = vehicle.commands.next
    if nextwaypoint == 0:
        return None
    missionitem = vehicle.commands[nextwaypoint-1]
    lat = missionitem.x
    lon = missionitem.y
    alt = missionitem.z
    while not is_arrived(lat, lon, alt):
        time.sleep(3)

def is_arrived(lat, lon, alt, precision=0.3):
    veh_loc = vehicle.location.global_relative_frame
    diff_lat_m = (lat - veh_loc.lat) * 1.113195e5
    diff_lon_m = (lon - veh_loc.lon) * 1.113195e5
    diff_alt_m = alt - veh_loc.alt
    dist_xyz = math.sqrt(diff_lat_m ** 2 + diff_lon_m ** 2 + diff_alt_m ** 2)

    if dist_xyz < precision:
        print("Прибыли на место")
        return True
    else:
        print("Еще не долетели")
        return False

time.sleep(10)

print("Close vehicle object")
vehicle.close()

if sitl is not None:
    sitl.stop()