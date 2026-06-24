import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_msgs.msg import Float32
from std_msgs.msg import Int32
from std_msgs.msg import Bool
from sensor_msgs.msg import Image
from std_msgs.msg import Int32MultiArray
from std_srvs.srv import Trigger 
import json
import threading
import re
import tf2_ros
from geometry_msgs.msg import PointStamped
import math


class Controller(Node):
    def __init__(self):
        super().__init__('Controller')
        self.tekst = None
        self.object_resultaat = None
        self.automate = False
        self.maan_teller = 0
        self.kubus_teller = 0
        self.balk_teller = 0
        self.octagon_teller = 0
        self.gekozen_product = None
        self.robot_status=None
        self.start_stop=False
##################### publishers ########################
        self.HMI_camera_publisher = self.create_publisher(
            Image,    #type bericht sturen
            'camera_image_raw',   #welk ding sturen
            10   #backlog aan msg
        )

        self.HMI_teller_publisher = self.create_publisher(
            Int32MultiArray,    #type bericht sturen
            'teller',   #welk ding sturen
            10   #backlog aan msg
        )

        self.gripper_status_publisher = self.create_publisher(
            Bool,    #type bericht sturen
            'gripper_status',   #welk ding sturen
            10   #backlog aan msg
        )

        self.robot_status_publisher = self.create_publisher(
            String,    #type bericht sturen <___________--- moet nog aangepast worden naar juiste type
            'robot_status',   #welk ding sturen
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

        self.noodstop_robot_publisher = self.create_publisher(
            Bool,    #type bericht sturen
            'estop',   #welk ding sturen
            10   #backlog aan msg
        )

        self.object_locatie_publisher = self.create_publisher(
            String,    #type bericht sturen <___________--- moet nog aangepast worden naar juiste type
            'aruco_pose',   #welk ding sturen
            10   #backlog aan msg
        )

        self.geen_product_publisher = self.create_publisher(#geen product gevonden stuur dit
            Bool,
            'geen_product',
            10
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

        self.call_for_product_sub=self.create_subscription(
            Bool,
            "/call_for_product",
            self.call_call_for_product,  #roept aan dat er een product naar de robot gestuurt wordt
            10
        )

############# client/servies ##############
        self.product_keuze_client = self.create_client(
            Trigger,
            '/product_keuze'
        )
        
##########callbacks##########

    def start_stop_callback(self, msg):
        self.start_stop = msg.data
        if self.start_stop==True:
            self.start_robot_publisher.publish(Bool(data=True))
        elif self.start_stop==False:
            self.stop_robot_publisher.publish(Bool(data=True))
        else:
            self.get_logger().info("Invalid start/stop signal received.")

    def automate_callback(self, msg):
        self.automate = msg.data

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


    def handshake_callback(self, msg):
        self.tekst = msg.data
        self.robot_status="stand-by"
        self.stuur_product_locatie

    def robot_error_callback(self, msg):    
        self.tekst = msg.data
    
    def cycle_complete_callback(self, msg):
        self.tekst = msg.data
        if self.automate==False or self.start_stop==False:
            self.robot_status="stand-by"
            self.stuur_product_locatie


    def call_call_for_product(self,msg):
        self.tekst = msg.data
        self.robot_status="busy"
        self.stuur_product_locatie

############ publishers en zo###############################
    def robot_status_verzenden(self):
        msg=String()
        msg.data=self.robot_status
        self.robot_status_publisher


    def teller_verzenden(self):
        teller_msg = Int32MultiArray()
        teller_msg.data = [self.kubus_teller, self.balk_teller, self.maan_teller, self.octagon_teller]
        self.HMI_teller_publisher.publish(teller_msg)
     
    def product_keuze_call_client(self):
        request = Trigger.Request() #zendt product keuze request naar service
        future = self.product_keuze_client.call_async(request)
        rclpy.spin_until_future_complete(self, future) #blijf draaien tot er een response is van de service
        if future.result() is not None: #als het iets is
            response = future.result()
            self.gekozen_product = response.message
        else:
            self.get_logger().error('Service call failed.')
            return None
        
    def stuur_product_locatie(self):
        if self.automate==False:  #kijkt of je handmatig keuze moet maken
            self.product_keuze_call_client  #roept keuze maken aan
            data_keuze=self.object_resultaat  #kijkt naar producten labels en locatie
            match=None  #er is geen match
            for obj in data_keuze:  #voor alle objecten
                if self.gekozen_product==obj:  #als het product label overeenkomt met de keuze dan
                    match=obj  #match wordt het momentele object
                    if obj=="Kubus":  #stuurt de bak naar manipulator
                       self.kubus_bak
                    elif obj=="Balk":
                       self.balk_bak
                    elif obj=="Maan":
                       self.maan_bak
                    elif obj=="Octagon":
                        self.octagon_bak
                    break  #ga uit de loop van for

            if match:  #als er een match is pak coordinaten en rotatie
                self.x_mm = match['x_mm']
                self.y_mm = match['y_mm']
                self.hoogte_mm = match['hoogte_mm']
                self.rotatie_deg = match['rotatie_deg']
                self.transorm_camxy_robot_xy #transformeer het
            else:
                print('geen gekozen product ligt er of is geen product') # geen match van procut
                msg=Bool()
                msg.data=True
                self.geen_product_publisher(msg)

        
        elif self.automate==True:
            data_keuze=self.object_resultaat
            if data_keuze is not None:
                obj_clean = re.sub(r'\d+', '', data_keuze['label']) #geen nummer in label
                self.x_mm = data_keuze['x_mm']  #x positie 
                self.y_mm = data_keuze['y_mm']
                self.hoogte_mm = data_keuze['hoogte_mm']
                self.rotatie_deg = data_keuze ['rotatie_deg']
                self.transorm_camxy_robot_xy  #zorg voor transformatie van positie en rotatie
                if obj=="Kubus":  #stuurt de bak naar manipulator
                   self.kubus_bak
                elif obj=="Balk":
                    self.balk_bak
                elif obj=="Maan":
                    self.maan_bak
                elif obj=="Octagon":
                    self.octagon_bak
            else:
                print('geen product gevonden') #geen product in camera beeld  
                msg=Bool()
                msg.data=True
                self.geen_product_publisher(msg)
            

    def transorm_camxy_robot_xy(self):
        #translatie in mm
        tx=290
        ty=290
        tz=0

            # --- rotatie ---
        theta = math.radians(135)

        cos_t = math.cos(theta)
        sin_t = math.sin(theta)

        # --- rotatie toepassen ---
        x_rot = cos_t * self.x_mm - sin_t * self.y_mm
        y_rot = sin_t * self.x_mm + cos_t * self.y_mm

        # --- translatie toepassen ---
        x_robot = x_rot + tx
        y_robot = y_rot + ty
        z_robot = self.hoogte_mm + tz

        #rotatie object toepassen
        robot_rotatie=self.rotatie_deg+theta
        
        cordinaten_product={
            'x':x_robot,
            'y':y_robot,
            'z':z_robot,
            'x_rotatie':0,
            'y_rotatie':0,
            'z_rotatie':robot_rotatie}
        msg=String()
        msg.data=json.dumps(cordinaten_product)
        self.object_locatie_publisher(msg)

###########stuur bakken door#############
    def kubus_bak(self):
        msg=Int32()#<-----------moet nog aangepast worden
        msg.data=[0.13, -0.275, 0.25]
        self.bak_locatie_publisher(msg)
        self.kubus_teller += 1
        self.teller_verzenden

    def maan_bak(self):
        msg=Int32#<-----------moet nog aangepast worden
        msg.data=[0.13, -0.175, 0.25]
        self.bak_locatie_publisher(msg)
        self.maan_teller += 1
        self.teller_verzenden

    def balk_bak(self):
        msg=Int32#<-----------moet nog aangepast worden
        msg.data=[0.25, -0.275, 0.25]
        self.bak_locatie_publisher(msg)
        self.balk_teller += 1
        self.teller_verzenden

    def octagon_bak(self):
        msg=Int32#<-----------moet nog aangepast worden
        msg.data=[0.25, -0.175, 0.25]
        self.bak_locatie_publisher(msg)
        self.octagon_teller += 1
        self.teller_verzenden

        

def main():
    rclpy.init()
    node = Controller()
    rclpy.spin(node)

if __name__ == "__main__":
    main()
    
