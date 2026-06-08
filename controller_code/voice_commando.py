import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_msgs.msg import Float
from std_msgs.msg import Bool
import tkinter as tk

class HMI(Node):
    def __init__(self):
        super().__init__('HMI_node')
        self.publisher_start_stop = self.create_publisher(
        Bool,    #bool voor start and stop button
        '/start',   #send to /start
        10   #backlog of msg to send
        )

        self.publisher_automate = self.create_publisher(
        Bool,    #bool voor start and stop button
        '/start',   #send to /start
        10   #backlog of msg to send
        )

        self.publisher_reset = self.create_publisher(
        Bool,    #bool voor start and stop button
        '/start',   #send to /start
        10   #backlog of msg to send
        )

        self.publisher_manual = self.create_publisher(
        Bool,    #bool voor start and stop button
        '/start',   #send to /start
        10   #backlog of msg to send
        )

        root = tk.Tk()  #main window
        root.title("Mijn GUI") #title of window

        button = tk.Button(  #make button
           root, #put it in window
           text="Start", #text on the button
           command=node.start   #do function start on press
           ) 
        button.pack()  #make visiable

        button = tk.Button(  #make button
            root, #put it in window
            text="Stop", #text on the button
            command=node.stop   #do function start on press
            ) 
        button.pack()  #make visiable
        root.mainloop()  #activeeerd HMI

    def stop(self):
        msg=Bool()
        msg.data=False
        self.publisher_start_stop.publish(msg)
    
    def start(self):
        msg=Bool()
        msg.data=True
        self.publisher_start_stop.publish(msg)
    

    

node=HMI()





    

