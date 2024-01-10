ip_address = 'localhost' # Enter your IP Address here
project_identifier = 'P2B' # Enter the project identifier i.e. P2A or P2B
#--------------------------------------------------------------------------------
import sys
sys.path.append('../')
from Common.simulation_project_library import *

hardware = False
QLabs = configure_environment(project_identifier, ip_address, hardware).QLabs
arm = qarm(project_identifier,ip_address,QLabs,hardware)
potentiometer = potentiometer_interface()
#--------------------------------------------------------------------------------
# STUDENT CODE BEGINS
#---------------------------------------------------------------------------------
import random 

# Pickup Container - Danyella Weinberger
# Define a function that will pickup the container based on its size and spawned coordinates
def pickup_container(list_spawn_coordinates, size):
    # Return arm to original position
    arm.home()
    time.sleep(1)
    # Make spawned coordinates the home position
    list_home = arm.effector_position()
    time.sleep(1)
    # Move the arm to the spawn coordinates
    arm.move_arm(list_spawn_coordinates[0], list_spawn_coordinates[1], list_spawn_coordinates[2])
    time.sleep(2)
    # Create If statement to differentiate between big and small containers
    if size == "large":
        arm.control_gripper(25)
    elif size == "small":
        arm.control_gripper(35)
    time.sleep(2)
    # Move arm back to home position
    arm.move_arm(list_home[0], list_home[1], list_home[2])
    time.sleep(1)

# Rotate Q-arm Base - Andrew Habib
# Define a function that will rotate the base of the q-arm while passing in the colour of the container as a parameter
def rotate_qarm_base(colour):
    # Declare a variable that will store the initial right potentiometer reading value multiplied by 320 
    # 0.0 to 1.0 potentiometer values need to be converted to movable degree values to move the arm in degrees ranging from 0 to 320 
    old_potentiometer_reading = potentiometer.right() * 100 * 3.2
    # Declare and initialize a variable that will store the final potentiometer reading value after the right potentiometer has been moved by the user multiplied by 320
    new_potentiometer_reading = potentiometer.right() * 100 * 3.2
    # Execute the below code indefinitely until the arm lands on the correct autoclave colour that corresponds with the container's colour in its hand
    while arm.check_autoclave(colour) == False:
        # Update the old potentiometer reading to the value of the previous new potentiometer 
        old_potentiometer_reading = new_potentiometer_reading
        # Update the new potentiometer reading to the new selected value of the right potentiometer reading by the user multiplied by 320
        new_potentiometer_reading = potentiometer.right() * 100 * 3.2
        # Declare a variable that will store the difference / change between the final and initial potentiometer reading values
        # This variable store the increment of the change that the user has moved the potentiometer which should correspond to the increment of change of the quarm
        degree_motion = new_potentiometer_reading - old_potentiometer_reading
        # Rotate the qarm based on the change in potentiometer readings determined above
        arm.rotate_base(degree_motion)
    # Delay the continuation of the code by 1 second
    time.sleep(1)

# Drop off Container - Danyella Weinberger
# Define a function that will drop off the container to their correct locations based on colour, size and location parameters
def drop_off_container(colour, size, location):
    dropped_off = False
    # Iterate indefinitely until the container has been dropped off successfully
    while not dropped_off:
        # Check if the container is small and the left potentiometer value corresponds to the small container threshold values (between 0.5 and 1.0 non-inclusive)
        if size == "small" and potentiometer.left() > 0.5 and potentiometer.left() < 1.0:
            # Move arm to appropriate drop off position
            arm.move_arm(location[0], location[1], location[2])
            time.sleep(1)
            # Drop the container
            arm.control_gripper(-35)
            time.sleep(1)
            # Return the arm to home position
            arm.home()
            time.sleep(1)
            # Update the drop off variable to True to end the while loop
            dropped_off = True
        # Otherwise, check if the container is large and the left potentiometer value corresponds to the large container threshold values (1.0 exactly)
        elif size == "large" and potentiometer.left() == 1.0:
            # Activate the autoclaves
            arm.activate_autoclaves()
            time.sleep(1)
            # Open the autoclave based on the colour of the container
            arm.open_autoclave(colour, True)
            time.sleep(1)
            # Move arm to appropriate drop off position
            arm.move_arm(location[0], location[1], location[2])
            time.sleep(1)
            # Drop the container
            arm.control_gripper(-25)
            time.sleep(1)
            # Return arm to home position
            arm.home()
            time.sleep(1)
            # Close autoclave based on the colour of the container
            arm.open_autoclave(colour, False)
            time.sleep(1)
            # De-activate the autoclaves
            arm.deactivate_autoclaves()
            time.sleep(1)
            # Update the drop off variable to True to end the while loop
            dropped_off = True

# Halting the Program - Andrew Habib
# Define a function that will      
def halt_program():
    # Inform the user that they must reset the potentiometer values back to 50% before another box spawns
    print("Set left and right potentiometers to default value of 50%.")
    # Iterate indefinitely
    while True:
        # Infinite loop will continue preventing the program to continue until both potentiometer values are set back to 50% in which case the loop breaks
        if potentiometer.left() == 0.5 and potentiometer.right() == 0.5:
            break

# Main Function (Continue or Terminate Program) - Andrew Habib
# Create a function to identify the size and colour of randomly spawned containers
def main():
    # List of random numbers from 1 to 6 (Used to spawn random containers)
    list_random_containers = random.sample(range(1, 7), 6)
    # [2, 4, 1, 3, 6, 5]
    # Create a list passing in the coordinates of the size and colour of each container
    list_colour_size_containers = [["red", "small", (0.0, 0.600, 0.200)],
        ["green", "small", (-0.580, 0.260, 0.200)], ["blue", "small", (0.0, -0.600, 0.200)],
        ["red", "large", (0.0, 0.400, 0.150)], ["green", "large", (-0.460, 0.160, 0.150)],
        ["blue", "large", (0.0, -0.400, 0.150)]]
    spawn_location = [0.550, 0.050, -0.002]
    # Create a for loop to go through each container
    for container in range(len(list_random_containers)):
        # Spawn a random cage
        arm.spawn_cage(list_random_containers[container])
        # Pick up the container and take it to drop off location
        pickup_container(spawn_location,
            list_colour_size_containers[list_random_containers[container] - 1][1])
        rotate_qarm_base(list_colour_size_containers[list_random_containers[container] - 1][0])
        drop_off_container(list_colour_size_containers[list_random_containers[container] - 1][0],
            list_colour_size_containers[list_random_containers[container] - 1][1],
            list_colour_size_containers[list_random_containers[container] - 1][2])
        halt_program()
    # Show completion of task and terminate the program
    print("Drop-offs Completed")
main()










#---------------------------------------------------------------------------------
# STUDENT CODE ENDS
#---------------------------------------------------------------------------------
    

    

