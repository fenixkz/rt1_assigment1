from __future__ import print_function

import time
from sr.robot import *



a_th = 2.0
""" float: Threshold for the control of the linear distance"""

d_th = 0.4
""" float: Threshold for the control of the orientation"""

SAFE_DISTANCE = 0.7
""" float: Linear threshold for indetifying a golden obstacle in front of the robot """

R = Robot()

def drive(speed, seconds):
    """
    Function for setting a linear velocity

    Args: speed (int): the speed of the wheels
	  seconds (int): the time interval
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0

def turn(speed, seconds):
    """
    Function for setting an angular velocity

    Args: speed (int): the speed of the wheels
	  seconds (int): the time interval
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = -speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0

def find_silver_token():
    """
    Retrieved from exercise3_solution.py

    Function to find the closest silver token

    Returns:
	dist (float): distance of the closest silver token (-1 if no silver token is detected)
	rot_y (float): angle between the robot and the silver token (-1 if no silver token is detected)
    """
    dist=100
    for token in R.see():
        if token.dist < dist and token.info.marker_type is MARKER_TOKEN_SILVER:
            dist=token.dist
	    rot_y=token.rot_y
    if dist==100:
	return -1, -1
    else:
   	return dist, rot_y

def find_golden_token():
    """
    Retrieved from exercise3_solution.py

    Function to find the closest silver token

    Returns:
	dist (float): distance of the closest silver token (-1 if no silver token is detected)
	rot_y (float): angle between the robot and the silver token (-1 if no silver token is detected)
    """
    dist=100
    for token in R.see():
        if token.dist < dist and token.info.marker_type is MARKER_TOKEN_GOLD:
            dist=token.dist
	    rot_y=token.rot_y
    if dist==100:
	return -1, -1
    else:
   	return dist, rot_y

def left_or_right():
    """
    Function to decide which turn to take by comparing the distance to the nearest obstacle on the left side and on the right side
    the angles to check are defined by the angle_high and angle_low variables
    Arguments: None
    Return: boolean variable, where 1 turning to the left and 0 turning to the right
    """
    dist = 100
    angle_high = 100
    angle_low = 80

    #Finding the closest left golden box
    for token in R.see():
        if token.rot_y < angle_high and token.rot_y > angle_low and token.dist < dist:
            dist = token.dist
    dist_left = dist

    #Finding the closest right golden box
    dist = 100
    for token in R.see():
        if token.rot_y > -angle_high and token.rot_y < -angle_low and token.dist < dist:
            dist = token.dist
    dist_right = dist

    return dist_left > dist_right

def find_token():
    """
    Function to find the closest token

    Returns:
	dist (float): distance of the closest token (-1 if no token is detected)
	rot_y (float): angle between the robot and the token (-1 if no token is detected)
    """
    dist = 100
    type = None

    # print(len(R.see()))
    for token in R.see():
        if token.dist < dist:
            dist = token.dist
            type = token.info.marker_type
	    rot_y = token.rot_y
    if dist == 100:
        return -1, -1, None
    else:
        return dist, rot_y, type


def turn_around():
    """
    Function to rotate the robot 180 degree
    Return: 1 if success
    """
    turn(60, 1) # Experimentally derived to turn around of 180 degrees
    return 1

def avoid(dist, rot):
    """
    Function to avoid the golden boxes
    There are three possible outcomes: if the obstacle is on the right, then turn left
    if the obstacle is on the left, then turn right.
    Sometimes a situation occurs when the robot approaches a box from the left, but it needs the correct turn should be also left
    it happens when the angle is small: it is resolved by the third if condition

    Arguments: distance and orientation to the nearest golden box
    Return: void
    """
    avoided = 0
    while not avoided:
        if rot <= -20: # If the obstacle on the right
            turn(20, 0.5)
        elif rot >= 20: # If the obstacle on the left
            turn(-20, 0.5)
        else: # The third condition
            bool = left_or_right()
            if bool:
                turn(20, 0.5)
            else:
                turn(-20, 0.5)

        dist_new, rot_new, _ = find_token()
        if abs(rot_new) > abs(rot) or dist_new >= dist: # If the rot increased or distance is safe we can conclude that the obstacle is avoided
            avoided = 1


def grab_silver(dist, rot):
    """
    Function to grab the silver token
    Retrieved from exercise2_solution.py

    Argument:
    distance and rotation angle to the nearest silver token
    Returns:
    1 if success
    0 if not
    """
    if dist < d_th:
        print("mmm, my precious!")
        R.grab() # if we are close to the token, we grab it.
        success = turn_around()
        if success:
            R.release()
            return 1
    elif -a_th <= rot <= a_th: # if the robot is well aligned with the token, we go forward
       drive(10, 0.5)

    elif rot < -a_th: # if the robot is not well aligned with the token, we move it on the left or on the right
       turn(-2, 0.5)
    elif rot > a_th:
       turn(+2, 0.5)
    return 0

"""
Main loop
Check for the nearest tokens: if silver the robot grabs it, if golden the robot avoids it
The boxes are considered only in the field of vision of the robot: [-90; 90]

"""
while True:
    dist, rot, type = find_token()

    if type is MARKER_TOKEN_GOLD: # avoid golden boxes
        if dist < SAFE_DISTANCE and abs(rot) < 90:
            print("Obstacle is found, avoiding ...")
            avoid(dist, rot)
    elif type is MARKER_TOKEN_SILVER: # grab silver boxes
        if abs(rot) < 90:
            print("Found a silver token, trying to grab it...")
            while not grab_silver(dist, rot):
                dist, rot = find_silver_token()
            drive(-20, 1) # move a little bit behind not to touch the token while rotating
            turn_around()
        else:
            drive(10,0.5)

    dist_g, rot_g = find_golden_token()
    """
    We move forward only if the distance to the nearest token is beyond safe distance or
    it is in the back (meaning that it cannot collide with it)
    """
    if dist_g > SAFE_DISTANCE or abs(rot_g) > 90:
        print("Moving forward")
        drive(30, 0.5)
    else:
        continue
