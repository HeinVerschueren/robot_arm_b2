import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_msgs.msg import Float32
from std_msgs.msg import Int32
from std_msgs.msg import Bool
from sensor_msgs.msg import Image
import json


class Controller(Node):
    def __init__(self):
        super().__init__('Controller')
        self.tekst = None

        self.object_resultaat = None
##################### publishers ########################
        self.HMI_camera_publisher = self.create_publisher(
            Image,    #type bericht sturen
            'camera_image_raw',   #welk ding sturen
            10   #backlog aan msg
        )

        self.start_robot_publisher = self.create_publisher(
            Bool,    #type bericht sturen
            'start_signal',   #welk ding sturen
            10   #backlog aan msg
        )

        self.stop_robot_publisher = self.create_publisher(  
            Bool,    #type bericht sturen
            'stop_signal',   #welk ding sturen
            10   #backlog aan msg
        )

        self.autmate_robot_publisher = self.create_publisher(
            Bool,    #type bericht sturen
            'robot_mode',   #welk ding sturen
            10   #backlog aan msg
        )

        self.bak_locatie_publisher = self.create_publisher(
            Int32,    #type bericht sturen <___________--- moet nog aangepast worden naar juiste type
            'bak_locatie',   #welk ding sturen
            10   #backlog aan msg
        )

        self.reset_robot_publisher = self.create_publisher(
            Bool,    #type bericht sturen
            'estop_reset',   #welk ding sturen
            10   #backlog aan msg
        )

        self.reset_robot_publisher = self.create_publisher(
            Bool,    #type bericht sturen
            'estop',   #welk ding sturen
            10   #backlog aan msg
        )

        self.object_locatie_publisher = self.create_publisher(
            String,    #type bericht sturen <___________--- moet nog aangepast worden naar juiste type
            'aruco_pose',   #welk ding sturen
            10   #backlog aan msg
        )

###########subscriptions##########
        self.start_stop_subsriber=self.create_subscription(  #maakt aan 
            Bool,   #type bericht lezen
            "/start",   #welk ding gesubscibt
            self.start_stop_callback,   #haalt data op
            10    #backlog aan msg
        )

        self.autmote_subsriber=self.create_subscription(  #maakt aan 
            Bool,   #type bericht lezen
            "/automate",   #welk ding gesubscibt
            self.automate_callback,   #haalt data op
            10    #backlog aan msg
        )

        self.reset_subsriber=self.create_subscription(  #maakt aan 
            Bool,   #type bericht lezen
            "/reset",   #welk ding gesubscibt
            self.reset_callback,   #haalt data op
            10    #backlog aan msg
        )

        self.shut_down_subsriber=self.create_subscription(  #maakt aan 
            Bool,   #type bericht lezen
            "/shut_down",   #welk ding gesubscibt
            self.shut_down_callback,   #haalt data op
            10    #backlog aan msg
        )       

        self.voice_on_subsriber=self.create_subscription(  #maakt aan 
            Bool,   #type bericht lezen
            "/voice_on",   #welk ding gesubscibt
            self.voice_on_callback,   #haalt data op
            10    #backlog aan msg
        )

        self.manual_override_subsriber=self.create_subscription(  #maakt aan 
            Bool,   #type bericht lezen
            "/manual_overide",   #welk ding gesubscibt
            self.manual_overide_callback,   #haalt data op
            10    #backlog aan msg
        )

        self.snelheid_subsriber=self.create_subscription(  #maakt aan 
            Float32,   #type bericht lezen
            "/snelheid",   #welk ding gesubscibt
            self.snelheid_callback,   #haalt data op
            10    #backlog aan msg
        )

        self.threshold_subsriber=self.create_subscription(  #maakt aan 
            Float32,   #type bericht lezen
            "/threshold",   #welk ding gesubscibt
            self.threshold_callback,   #haalt data op
            10    #backlog aan msg
        )

        self.camera_sub=self.create_subscription(  #maakt aan 
            Image,   #type bericht lezen
            "/camera_beelden",   #welk ding gesubscibt
            self.camera_callback,   #haalt data op
            10    #backlog aan msg
        )

        self.object_detectie_sub=self.create_subscription(  #maakt aan 
            String,   #type bericht lezen
            '/detectie_resultaten',   #welk ding gesubscibt
            self.object_detectie_callback,   #haalt data op
            10    #backlog aan msg
        )

        self.handshake_sub=self.create_subscription(  #maakt aan 
            Bool,   #type bericht lezen 
            "/handshake",   #welk ding gesubscibt
            self.handshake_callback,   #haalt data op
            10    #backlog aan msg
        )

        self.robot_error_sub=self.create_subscription(  #maakt aan 
            String,   #type bericht lezen
            "/robot_error",   #welk ding gesubscibt
            self.robot_error_callback,   #haalt data op
            10    #backlog aan msg
        )

        self.cycle_complete_sub=self.create_subscription(  #maakt aan 
            Bool,   #type bericht lezen
            "/cycle_complete",   #welk ding gesubscibt
            self.cycle_complete_callback,   #haalt data op
            10    #backlog aan msg
        )
        
##########callbacks##########

    def start_stop_callback(self, msg):
        self.tekst = msg.data
        if self.tekst==True:
            self.start_robot_publisher.publish(Bool(data=True))
        elif self.tekst==False:
            self.stop_robot_publisher.publish(Bool(data=True))
        else:
            self.get_logger().info("Invalid start/stop signal received.")

    def automate_callback(self, msg):
        self.tekst = msg.data

    def reset_callback(self, msg):
        self.tekst = msg.data

    def shut_down_callback(self, msg):
        self.tekst = msg.data

    def voice_on_callback(self, msg):
        self.tekst = msg.data

    def snelheid_callback(self, msg):
        self.tekst = msg.data

    def threshold_callback(self, msg):
        self.tekst = msg.data   

    def manual_overide_callback(self, msg):
        self.tekst = msg.data

    def camera_callback(self, msg):
        self.HMI_camera_publisher.publish(msg)  # Publish the image to the HMI camera topic

    def object_detectie_callback(self, msg):
        self.object_resultaat = json.loads(msg.data)
        label = resultaat['label']
        confidence = resultaat['confidence']
        x_px = resultaat['x_px']
        y_px = resultaat['y_px']
        x_mm = resultaat['x_mm']
        y_mm = resultaat['y_mm']
        z_mm = resultaat['z_mm']
        hoogte_mm = resultaat['hoogte_mm']
        rotatie_deg = resultaat['rotatie_deg']

    def handshake_callback(self, msg):
        self.tekst = msg.data 

    def robot_error_callback(self, msg):    
        self.tekst = msg.data
    
    def cycle_complete_callback(self, msg):
        self.tekst = msg.data
     

        

def main():
    rclpy.init()
    node = Controller()
    rclpy.spin(node)

if __name__ == "__main__":
    main()
    
