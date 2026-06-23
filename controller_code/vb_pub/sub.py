import rclpy
from rclpy.node import Node
from std_msgs.msg import String




class MinimalPublisher(Node):

    def __init__(self):
        super().__init__('minimal_publisher')

        # Maak een publisher voor String-berichten
        self.publisher_ = self.create_publisher(
            String,    #type message
            'chatter',   #waarop je het stuurt
            10   #backlog aaan msg om te sturen
        )


    def timer_callback(self):
        msg = String()     #maakt message een string
        msg.data = f'Hallo ROS2! Bericht {self.counter}'  #maakt de data het bericht

        self.publisher_.publish(msg)   #publish het 

class Subscriber(Node):
    def __init__(self):
        super().__init__('subscriber')
        self.tekst = None

        self.create_subscription(  #maakt aan 
            String,   #type bericht lezen
            'chatter',   #welk ding gesubscibt
            self.callback,  #haalt data op
            10    #backlog aan msg
        )

        def callback(self, msg):
            self.tekst = msg.data

def main(args=None):
    rclpy.init(args=args)

    node1 = MinimalPublisher()
    node2= Subscriber()

    try:
        rclpy.spin(node1)
        rclpy.spin(node2)
        print ({node2.tekst})
    except KeyboardInterrupt:  #sluit het af met een toets
        pass

    node.destroy_node()
    rclpy.shutdown()
    


if __name__ == '__main__':
    main()



checkbox_var = tk.BooleanVar()  #make variable voor switch
checkbox = tk.Checkbutton(  #for switch
    root,
    text="Motor aan",
    variable=checkbox_var
)
checkbox.pack() #make visiable in window