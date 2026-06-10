import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_msgs.msg import Float32
from std_msgs.msg import Bool


class Controller(Node):
    def __init__(self):
        super().__init__('Controller')
        self.tekst = None

        self.start_stop_subsriber=self.create_subsriber(  #maakt aan 
            Bool,   #type bericht lezen
            "/start",   #welk ding gesubscibt
            self.start_stop_callback,   #haalt data op
            10    #backlog aan msg
        )

        self.autmote_subsriber=self.create_subsriber(  #maakt aan 
            Bool,   #type bericht lezen
            "/automate",   #welk ding gesubscibt
            self.automate_callback,   #haalt data op
            10    #backlog aan msg
        )

        self.reset_subsriber=self.create_subsriber(  #maakt aan 
            Bool,   #type bericht lezen
            "/reset",   #welk ding gesubscibt
            self.reset_callback,   #haalt data op
            10    #backlog aan msg
        )

        self.shut_down_subsriber=self.create_subsriber(  #maakt aan 
            Bool,   #type bericht lezen
            "/shut_down",   #welk ding gesubscibt
            self.shut_down_callback,   #haalt data op
            10    #backlog aan msg
        )       

        self.voice_on_subsriber=self.create_subsriber(  #maakt aan 
            Bool,   #type bericht lezen
            "/voice_on",   #welk ding gesubscibt
            self.voice_on_callback,   #haalt data op
            10    #backlog aan msg
        )

        self.manual_override_subsriber=self.create_subsriber(  #maakt aan 
            Bool,   #type bericht lezen
            "/manual_overide",   #welk ding gesubscibt
            self.manual_overide_callback,   #haalt data op
            10    #backlog aan msg
        )

        self.snelheid_subsriber=self.create_subsriber(  #maakt aan 
            Float32,   #type bericht lezen
            "/snelheid",   #welk ding gesubscibt
            self.snelheid_callback,   #haalt data op
            10    #backlog aan msg
        )

        self.threshold_subsriber=self.create_subsriber(  #maakt aan 
            Float32,   #type bericht lezen
            "/threshold",   #welk ding gesubscibt
            self.threshold_callback,   #haalt data op
            10    #backlog aan msg
        )


    def start_stop_callback(self, msg):
        self.tekst = msg.data

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
    
