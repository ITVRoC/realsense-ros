#!/usr/bin/env python
# license removed for brevity

import rospy
import math
import sys
from nav_msgs.msg import Odometry
from std_msgs.msg import Float32
from std_srvs.srv import Trigger, TriggerResponse

x_ant = 0
y_ant = 0
z_ant = 0
total_dist  = 0
print("\nLOCOMOTION  DATA - Espeleo \n \n")

def trigger_response(request):
    ''' 
    Callback function used by the service server to process
    requests from clients. It returns a TriggerResponse
    '''
    global total_dist

    total_dist = 0.0

    rospy.loginfo("Reset odometry distance to 0")

    return TriggerResponse(
        success=True,
        message="Distance set to 0"
    )


def dist_pnt(x,y,z=0.0):
    global total_dist, x_ant,y_ant, z_ant, elev
    
    dist = math.sqrt((x-x_ant)**2 +(y-y_ant)**2 + (z-z_ant)**2)
    total_dist = total_dist + dist
    x_ant = x
    y_ant = y
    z_ant = z
    #sys.stdout.write("\033[F")  # back to previous line
    #sys.stdout.write("\033[K")  # clear line
    rospy.logdebug("Total distance: %.4fm ---- Current elevation: %.4fm", total_dist, z)
    pub.publish(total_dist)


def odometry_callback(msg):
    x = float("{0:.2f}".format(msg.pose.pose.position.x))
    y = float("{0:.2f}".format(msg.pose.pose.position.y))
    z = float("{0:.2f}".format(msg.pose.pose.position.z))
    dist_pnt(x,y)
    text = [repr(msg.header.stamp.secs), repr(msg.header.stamp.nsecs), repr(msg.pose.pose), repr(msg.twist.twist)]
    file.write('\n secs:' + text[0] + '\n nsecs: ' + text[1] + '\n' + text[2] + '\n' + text[3] + '\n' )


if __name__ == '__main__':
    rospy.init_node('t265_data', anonymous=True)
    
    seconds = repr(rospy.get_rostime())
    file_name = "T265_time_" + seconds[11:30] + ".txt"
    file = open(file_name, "w")

    rospy.loginfo("Setting up odometry distance...")

    pub = rospy.Publisher('dist', Float32, queue_size=10)

    # distance service
    dist_service = rospy.Service(                    
        '/reset_t265_dist_measurement', Trigger, trigger_response
    )

    # odom subscriber
    rospy.Subscriber(
        'camera/odom/sample', Odometry, odometry_callback
    )

    while not rospy.is_shutdown():    
        rospy.spin()