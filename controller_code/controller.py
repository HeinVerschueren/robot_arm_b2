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
import time
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup


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
        print("grippper")
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
        print("robot start")
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
        print("bakken")
        self.bak_locatie_publisher = self.create_publisher(
            Int32,    #type bericht sturen <___________--- moet nog aangepast worden naar juiste type
            'bak_locatie',   #welk ding sturen
            10   #backlog aan msg
        )
        print("reset robot")
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
        print("geen product")
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
        print("automate sub")
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
        print("kut voice")
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
        print("threshold")
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

        print("subscriber aangemaakt")
        self.object_detectie_sub = self.create_subscription(
           String,
           '/detectie_resultaten',
            self.object_detectie_callback,
            10
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

############# client/servies ##############
        self.cb_group = ReentrantCallbackGroup()

        self.call_for_product_server = self.create_service(
            Trigger,
            '/call_for_product',
            self.call_call_for_product,
            callback_group=self.cb_group
        )

        self.product_keuze_client = self.create_client(
           Trigger,
          '/product_keuze',
           callback_group=self.cb_group
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
        self.automate=msg.data
        self.autmate_robot_publisher.publish(msg)

    def reset_callback(self, msg):
        self.tekst = msg.data
        self.reset_robot_publisher.publish(msg)

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
        data = json.loads(msg.data)
        # Zorg altijd voor een lijst, of de node nu een dict of lijst stuurt
        if isinstance(data, dict):
            self.object_resultaat = [data]
        else:
            self.object_resultaat = data

    def handshake_callback(self, msg):
        self.tekst = msg.data
        self.robot_status="stand-by"
        self.robot_status_verzenden()

    def robot_error_callback(self, msg):    
        self.tekst = msg.data
    
    def cycle_complete_callback(self, msg):
        self.tekst = msg.data
        if self.automate==False or self.start_stop==False:
            self.robot_status="stand-by"

    def call_call_for_product(self,request,response):
        self.product_response=response

        self.robot_status="busy"
        self.robot_status_verzenden()

        self.stuur_product_locatie()

        print("service einde")
        return self.product_response

############ publishers en zo###############################
    def robot_status_verzenden(self):
        msg=String()
        msg.data=self.robot_status
        self.robot_status_publisher.publish(msg)


    def teller_verzenden(self):
        teller_msg = Int32MultiArray()
        teller_msg.data = [self.kubus_teller, self.balk_teller, self.maan_teller, self.octagon_teller]
        self.HMI_teller_publisher.publish(teller_msg)
     
    def product_keuze_call_client(self):  #product
        request = Trigger.Request()

        future = self.product_keuze_client.call_async(request)

        self.get_logger().info("Wachten op response...")

        while not future.done():
            time.sleep(0.05)  # 50ms wachten per iteratie

        if future.result():
            self.gekozen_product = future.result().message
            print({self.gekozen_product})
            return self.gekozen_product

        self.get_logger().error("Service failed")
        return None
        
    def stuur_product_locatie(self):  #stuur gekozen product lokatie
        if self.object_resultaat is None:  #geen object is er
            self.get_logger().warn("Nog geen detectie resultaten beschikbaar")
            self.product_response.success = False
            self.product_response.message = "geen product gevonden"
            return

        data_keuze = self.object_resultaat.copy()  # altijd een lijst van dicts

        if not self.automate:
            # --- Handmatig: zoek het object waarvan LABELS overeenkomt met de keuze ---
            self.product_keuze_call_client()

            match = None
            for obj in data_keuze:
                if self.gekozen_product == obj["LABELS"]:
                    match = obj
                    break  # eerste match is genoeg

            if match:
                #self._stuur_bak(match["LABELS"])
                self._stel_coordinaten_in(match)
                self.transorm_camxy_robot_xy()
            else:
                self.get_logger().warn("Geen match gevonden voor gekozen product")
                self.product_response.success = False
                self.product_response.message = "geen product gevonden"

        else:
        #  Automatisch: pak altijd het eerste object uit de lijst
            if data_keuze:
                obj = data_keuze[0]
                #self._stuur_bak(obj["LABELS"])
                self._stel_coordinaten_in(obj)
                self.transorm_camxy_robot_xy()
            else:
                self.get_logger().warn("Lege lijst, geen product gevonden")
                self.product_response.success = False
                self.product_response.message = "geen product gevonden"


    def _stel_coordinaten_in(self, obj):
       #Haalt x/y/z/rotatie uit een object-dict.
       self.x_mm       = obj['x_mm']
       self.y_mm       = obj['y_mm']
       self.hoogte_mm  = obj['hoogte_mm']
       self.rotatie_deg = obj['rotatie_deg']


    def _stuur_bak(self, label):
    #Publiceert de bak-locatie op basis van het label.
        if label == "Kubus":
            self.kubus_bak()
        elif label == "Balk":
            self.balk_bak()
        elif label == "Maan":
            self.maan_bak()
        elif label == "Octagon":
            self.octagon_bak()
        else:
            self.get_logger().warn(f"Onbekend label: {label}")
            

    def transorm_camxy_robot_xy(self):
        #translatie in mm
        tx=290
        ty=290
        tz=0

            # --- rotatie ---
        theta = math.radians(135)
        print("reached 5")

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
        robot_rotatie=self.rotatie_deg+135
        
        cordinaten_product={
            'x':x_robot,
            'y':y_robot,
            'z':z_robot,
            'x_rotatie':0,
            'y_rotatie':0,
            'z_rotatie':robot_rotatie}
        self.product_response.success=True
        self.product_response.message=json.dumps(cordinaten_product)

        

###########stuur bakken door#############
    def kubus_bak(self):
        msg=Int32()#<-----------moet nog aangepast worden
        msg.data=[0.13, -0.275, 0.25]
        self.bak_locatie_publisher.publish(msg)
        self.kubus_teller += 1
        self.teller_verzenden()

    def maan_bak(self):
        msg=Int32#<-----------moet nog aangepast worden
        msg.data=[0.13, -0.175, 0.25]
        self.bak_locatie_publisher.publish(msg)
        self.maan_teller += 1
        self.teller_verzenden()

    def balk_bak(self):
        msg=Int32#<-----------moet nog aangepast worden
        msg.data=[0.25, -0.275, 0.25]
        self.bak_locatie_publisher.publish(msg)
        self.balk_teller += 1
        self.teller_verzenden()

    def octagon_bak(self):
        msg=Int32#<-----------moet nog aangepast worden
        msg.data=[0.25, -0.175, 0.25]
        self.bak_locatie_publisher.publish(msg)
        self.octagon_teller += 1
        self.teller_verzenden()

        

def main():
    rclpy.init()
    node = Controller()

    executor = MultiThreadedExecutor()
    executor.add_node(node)

    executor.spin()

if __name__ == "__main__":
    main()
    
