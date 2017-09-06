import rospy
from pid import PID
from yaw_controller import YawController
#GAS_DENSITY = 2.858
#ONE_MPH = 0.44704


class Controller(object):
    def __init__(self, **kwargs):
        # TODO: Implement
        max_lat_acc = kwargs['max_lat_acc']
        max_steer_angle = kwargs['max_steer_angle']
        steer_ratio = kwargs['steer_ratio']
        wheel_base = kwargs['wheel_base']

        self.accel_limit = kwargs['accel_limit']
        self.brake_deadband = kwargs['brake_deadband']
        self.decel_limit = kwargs['decel_limit']



        # Create Variable for the last update time
        self.last_ut = None

        # Create a PID Controller
        # TODO: Tune for simulator. Figure out a way to tune 
        # for the Actual vehicle on the track
        self.pid_c = PID(0.1,0.0001,0.4)

        # Create a steering controller
        self.steer_c = YawController(wheel_base=wheel_base, steer_ratio=steer_ratio, min_speed = 0.0, max_lat_accel = max_lat_acc, max_steer_angle = max_steer_angle)

        pass

    def control(self, **kwargs):
        # TODO: Change the arg, kwarg list to suit your needs
        # Return throttle, brake, steer

        # Get the variables from the arguments
        twist_linear = kwargs['twist_command'].twist.linear
        twist_angular = kwargs['twist_command'].twist.angular

        cv_linear = kwargs['current_velocity'].twist.linear
        cv_angular = kwargs['current_velocity'].twist.angular

        # Set the Error
        vel_err = twist_linear.x - cv_linear.x

        # Set the present and target values
        target_v = twist_linear.x
        present_v = cv_linear.x
        target_w = twist_angular.z

        if self.last_ut is not None:
            # Get current time
            time = rospy.get_time()

            # Compute timestep between updates and save 
            # for next iteration
            dt = time - self.last_ut
            self.last_ut = time

            # PID class returns output for throttle and 
            # brake axes as a joint forward_backward axis
            forward_axis = self.pid_c.step(vel_err, dt)
            reverse_axis = -forward_axis

            # if forward axis is positive only then give any throttle
            throttle = max(0.0,forward_axis)
            # Only apply brakes if the reverse axis value is large enough to supersede the deadband
            #TODO: Figure out how this tuning will work for the real vehicle
            brake = max(0.0, reverse_axis - self.brake_deadband)

            # get the steering value from the yaw controller
            steering = self.steer_c.get_steering(target_v, target_w, present_v)

            return throttle, brake, steering
        else:
            # Update the last_update time and send Zeroes tuple
            self.last_ut = rospy.get_time()
            return 0., 0., 0.