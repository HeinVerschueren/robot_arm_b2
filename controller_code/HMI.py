from numpy import int32

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_msgs.msg import Float32
from std_msgs.msg import Bool
from sensor_msgs.msg import Image as RosImage
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
from cv_bridge import CvBridge
from std_srvs.srv import Trigger
from std_msgs.msg import Int32MultiArray
import threading

class HMI(Node):
    def __init__(self):
        super().__init__('HMI_node')
        self.kubus_tel = 0
        self.balk_tel = 0
        self.maan_tel = 0
        self.octagon_tel = 0

        self.publisher_start_stop = self.create_publisher(
           Bool,    #bool for start and stop button
           'start',   #send to /start
           10   #backlog of msg to send
        )

        self.publisher_automate = self.create_publisher(
           Bool,    #bool for automate and stop button
           'automate',   #send to /automate
            10   #backlog of msg to send
        )

        self.publisher_reset = self.create_publisher(
           Bool,    #bool for reset and stop button
           'reset',   #send to /reset
           10   #backlog of msg to send
        )

        self.publisher_voice_on = self.create_publisher(
            Bool,    #bool for voice on and stop button
            'voice_on',   #send to /voice_on
            10   #backlog of msg to send
        )

        self.publisher_shut_down = self.create_publisher(
            Bool,    #bool for shut down 
            'shut_down',   #send to /shut_down
            10   #backlog of msg to send
        )
        self.publisher_snelheid = self.create_publisher(
            Float32,    #float for snelheid
            'snelheid',   #send to /snelheid
            10   #backlog of msg to send
        )

        self.publisher_threshold = self.create_publisher(
            Float32,    #float for threshold
            'threshold',   #send to /threshold
            10   #backlog of msg to send
        )

        self.publisher_manual_overide = self.create_publisher(
            Bool,    #bool manual override
            'manual_overide',   #send to /manual_overide
            10   #backlog of msg to send
        )

################# service
        self.product_keuze_service = self.create_service(
            Trigger,    
             'product_keuze',   #send to /product_keuze
            self.product_keuze_callback   #backlog of msg to send
        )
####################### subscriber ###########################
        self.bridge = CvBridge()
        self.latest_frame = None

        self.camera_subscriber = self.create_subscription(
           RosImage,
           '/camera_image_raw',
            self.Image_callback,
           10,
        )

        self.gripper_status_subscriber = self.create_subscription(
            Bool,
            '/gripper_status',
            self.gripper_status_callback,
            10,
        )

        self.robot_status_subscriber = self.create_subscription(
            String,
            '/robot_status',
            self.robot_status_callback,
            10,
        )

        self.teller_subscriber = self.create_subscription(
            Int32MultiArray,
            '/teller',
            self.teller_callback,
            10,
        )
######################## window with buttons and such  ###################

        self.root = tk.Tk()  #main window
        self.root.title("Mijn GUI") #title of window
        self.root.geometry("1200x800")
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))

        self.button_start = tk.Button(  #make button
           self.root, #put it in window
           text="Start", #text on the button
           command=self.start   #do function start on press
           ) 
        self.button_start.grid(row=0, column=0, padx=10, pady=5, sticky="nw")  #make visiable

        self.button_stop = tk.Button(  #make button
            self.root, #put it in window
            text="Stop", #text on the button
            command=self.stop   #do function start on press
            ) 
        self.button_stop.grid(row=1, column=0, padx=10, pady=5, sticky="nw")    #make visiable

        self.button_reset = tk.Button(  #make button
           self.root, #put it in window
           text="Reset", #text on the button
           command=self.reset   #do function start on press
           ) 
        self.button_reset.grid(row=2, column=0, padx=10, pady=5, sticky="nw")    #make visiable


        self.keuze_active = False
        self.maan_button = tk.Button(  #make button
            self.root, #put it in window
            text="Maan", #text on the button
            command=lambda:   ##do function when activated
            self.keuze_gemaakt("maan")
            ) 
        self.maan_button.grid(row=4, column=3, padx=10, pady=5, sticky="nw")    #make visiable

        self.kubus_button = tk.Button(  #make button
            self.root, #put it in window
            text="Kubus", #text on the button
            command=lambda:   #do function when activated
            self.keuze_gemaakt("kubus")  #wait for user to make choice
            ) 
        self.kubus_button.grid(row=4, column=4, padx=10, pady=5, sticky="nw")    #make visiable

        self.balk_button = tk.Button(  #make button
            self.root, #put it in window
            text="Balk", #text on the button
            command=lambda:   #do function when activated
            self.keuze_gemaakt("balk")  #wait for user to make choice
            ) 
        self.balk_button.grid(row=4, column=5, padx=10, pady=5, sticky="nw")    #make visiable

        self.octagon_button = tk.Button(  #make button
            self.root, #put it in window
            text="Octagon", #text on the button
            command=lambda:   #do function when activated
            self.keuze_gemaakt("octagon")
            ) 
        self.octagon_button.grid(row=4, column=6, padx=10, pady=5, sticky="nw")    #make visiable

########## checkboxen/switches ############

        self.checkbox_auto = tk.BooleanVar()  #make variable for switch
        self.switch_auto = tk.Checkbutton(  #for switch
           self.root,
           text="automatisch",
           variable=self.checkbox_auto,
           command=self.automatisch
           )
        self.switch_auto.grid(row=3, column=0, padx=10, pady=5, sticky="nw")   #make visiable in window

        self.checkbox_voice_on = tk.BooleanVar()  #make variable for switch
        self.switch_voice_on = tk.Checkbutton(  #for switch
           self.root,
           text="voice command",
           variable=self.checkbox_voice_on,
           command=self.voice_on
           )
        self.switch_voice_on.grid(row=4, column=0, padx=10, pady=5, sticky="nw")   #make visiable in window

        self.button_exit = tk.Button( #make button
            self.root,
            text="Afsluiten",  #name
            command=self.close  #function
            )
        self.button_exit.grid(row=10, column=0, padx=10, pady=5, sticky="nw")   #make visiable

########### snelheid en threshold input ############   

        tk.Label(self.root, text="Snelheid (%)").grid(row=5, column=0, sticky="w")

        self.number_var_snelheid = tk.StringVar()  #maakt make number varibale for hmi
        self.number_entry_snelheid = tk.Entry(
            self.root,
            textvariable=self.number_var_snelheid,
            width=5)
        self.number_entry_snelheid.grid(row=6, column=0, padx=10, pady=5, sticky="nw")

        button = tk.Button(
            self.root,
            text="stuur snelheid",
            command=self.snelheid_zendt)
        button.grid(row=6, column=1, padx=10, pady=5, sticky="nw")

        tk.Label(self.root, text="threshold (%)").grid(row=7, column=0, sticky="w")

        self.number_var_threshold = tk.StringVar()  # make number varibale for hmi
        self.number_entry_threshold = tk.Entry(
            self.root,
            textvariable=self.number_var_threshold,
            width=5)
        self.number_entry_threshold.grid(row=8, column=0, padx=10, pady=5, sticky="nw")

        button = tk.Button(
            self.root,
            text="stuur threshold",
            command=self.threshold_zendt)  #funciton for button
        button.grid(row=8, column=1, padx=10, pady=5, sticky="nw")

        self.checkbox_manual_overide = tk.BooleanVar()  #make variable for switch
        self.switch_manual_overide = tk.Checkbutton(  #for switch
           self.root,
           text="manual override",
           variable=self.checkbox_manual_overide,
           command=self.manual_overide
           )
        self.switch_manual_overide.grid(row=9, column=0, padx=10, pady=5, sticky="nw")   #make visiable in window

############ teller tabel ########################
        self.columns = ("kubus", "balk", "maan", "ocatagon")  #naam colomen
        self.tree = ttk.Treeview(self.root, columns=self.columns, show="headings", height=1) 
        for col in self.columns:    #maakt collomen aan
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80)
        self.tree.insert("", tk.END, values=(self.kubus_tel, self.balk_tel, self.maan_tel, self.octagon_tel))  #hoeveelheid in kolom
        self.tree.grid(row=0, column=4, rowspan=2, padx=20, pady=5, sticky="ne")  #zorgt for rechts tabel

############## status labels/camera beeld ########################
        self.status_grijper = tk.StringVar()
        self.status_grijper.set("grijper: open")

        self.status_label_grijper = tk.Label( #grijper status label
            self.root,
            textvariable=self.status_grijper,
            bg="gray",
            fg="white",
            width=20
        )
        self.status_label_grijper.grid(row=0, column=2, padx=20, pady=5, sticky="n")

        self.status_robot = tk.StringVar()
        self.status_robot.set("robot: stand-by")

        self.status_label_robot = tk.Label( #robot status label
            self.root,
            textvariable=self.status_robot,
            bg="orange",
            fg="white",
            width=20
        )
        self.status_label_robot.grid(row=1, column=2, padx=20, pady=5, sticky="n")

        self.keuze_Status = tk.StringVar()
        self.keuze_Status.set("bezig")

        self.status_label_keuze = tk.Label( #keuze status label
            self.root,
            textvariable=self.keuze_Status,
            bg="orange",
            fg="white",
            width=20
        )
        self.status_label_keuze.grid(row=2, column=2, padx=20, pady=5, sticky="n")

        self.snelheid_Status = tk.StringVar()
        self.snelheid_Status.set("snelheid:100%")

        self.status_label_snelheid = tk.Label( #snelheid status label
            self.root,
            textvariable=self.snelheid_Status,
            bg="LightGray",
            fg="Black",
            width=20
        )
        self.status_label_snelheid.grid(row=6, column=2, padx=20, pady=5, sticky="n")

        self.threshold_Status = tk.StringVar()
        self.threshold_Status.set("threshold:85%")

        self.status_label_threshold = tk.Label( #threshold status label
            self.root,
            textvariable=self.threshold_Status,
            bg="LightGray",
            fg="Black",
            width=20
        )
        self.status_label_threshold.grid(row=8, column=2, padx=20, pady=5, sticky="n")

        self.camera_label = tk.Label(self.root, bg="black") #voor camera beeld
        self.camera_label.grid(
            row=5,
            column=3,
            rowspan=10,  # neemt meerdere rijen in beslag
            columnspan=10,  #neemt meerdere colomen in beslag
            padx=20,
            pady=10
        )
        self.keuze_event = threading.Event()

############ end init #########################
    def ros_thread(self):
        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.01)

    def run(self):
        threading.Thread(
            target=self.ros_thread,
            daemon=True
        ).start()

        self.root.mainloop()

####### knoppen functies ############
    def close(self):  #stopt alles
        msg=Bool()
        msg.data=True
        self.publisher_shut_down.publish(msg)
        self.destroy_node()
        rclpy.shutdown()
        self.root.destroy()
            

    def stop(self):  #publish stop
        msg=Bool()
        msg.data=False
        self.publisher_start_stop.publish(msg)
    
    def start(self):  #publish start
        msg=Bool()
        msg.data=True
        self.publisher_start_stop.publish(msg)

    def reset(self):  #publish reset
        msg=Bool()
        msg.data=True
        self.publisher_reset.publish(msg)

    def automatisch(self):  #publish automatisch
        msg=Bool()
        msg.data=self.checkbox_auto.get()
        self.publisher_automate.publish(msg)

    def voice_on(self):   #publish voice command
        msg=Bool()
        msg.data=self.checkbox_voice_on.get()
        self.publisher_voice_on.publish(msg)

    def snelheid_zendt(self):
        raw_snelheid=self.number_var_snelheid.get()
        check_snelheid=float(raw_snelheid)
        if check_snelheid > 100:
            snelheid=100
        elif check_snelheid < 0:
            snelheid=0
        else:
            snelheid=check_snelheid
        snelheid_float=float(snelheid)
        msg=Float32()
        msg.data=snelheid_float
        self.snelheid_bezig(snelheid_float)
        self.publisher_snelheid.publish(msg)

    def threshold_zendt(self):
        raw_threshold=self.number_var_threshold.get()
        check_threshold=float(raw_threshold)
        if check_threshold > 100:
            threshold=100
        elif check_threshold < 0:
            threshold=0
        else: 
            threshold=check_threshold
        threshold_float=float(threshold)
        msg=Float32()
        msg.data=threshold_float
        self.threshold_bezig(threshold_float)
        self.publisher_threshold.publish(msg)  
    
    def manual_overide(self):  #publish automatisch
        msg=Bool()
        msg.data=self.checkbox_manual_overide.get()
        self.publisher_manual_overide.publish(msg)

####### statusen aanpassen ##########
    def Grijper_close(self):
        self.status_grijper.set("grijper: close")
        self.status_label_grijper.config(bg="blue")

    def Grijper_open(self):
        self.status_grijper.set("grijper: copen")
        self.status_label_grijper.config(bg="gray")

    def robot_stand_by(self):
        self.status_robot.set("robot:stand-by")
        self.status_label_robot.config(bg="orange")

    def robot_noodstop(self):
        self.status_robot.set("robot:noodstop")
        self.status_label_robot.config(bg="red")
    
    def robot_bezig(self):
        self.status_robot.set("robot:busy")
        self.status_label_robot.config(bg="green")
    
    def robot_error(self):
        self.status_robot.set("robot:error")
        self.status_label_robot.config(bg="red")

    def keuze_bezig(self):
        self.keuze_Status.set("bezig")
        self.status_label_keuze.config(bg="orange")

    def keuze_maken(self):
        self.keuze_Status.set("keuze: maken")
        self.status_label_keuze.config(bg="green")

    def snelheid_bezig(self,snelheid):
        self.snelheid_Status.set(f"snelheid: {snelheid}%")
        self.status_label_snelheid.config(bg="LightGray")

    def threshold_bezig(self,threshold):
        self.threshold_Status.set(f"threshold: {threshold}%")
        self.status_label_threshold.config(bg="LightGray")
########## call baccks for subscriber ########################
    def Image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        self.latest_frame = frame
        self.root.after(0, self.update_camera)

    def gripper_status_callback(self, msg):
        gripper=msg.data
        if gripper==True:
            self.Grijper_open()
        elif gripper==False:
            self.Grijper_close()

    def robot_status_callback(self, msg):
        status=msg.data
        if status=="stand-by":
            self.robot_stand_by()
        elif status=="noodstop":
            self.robot_noodstop()
        elif status=="busy":
            self.robot_bezig()
        elif status=="error":
            self.robot_error()

    def teller_callback(self, msg):
        self.kubus_tel=msg.data[0]
        self.balk_tel=msg.data[1]
        self.maan_tel=msg.data[2]
        self.octagon_tel=msg.data[3]
        self.tree.delete(*self.tree.get_children()) #verwijder oude waarden van tabel
        self.tree.insert("", tk.END, values=
        (self.kubus_tel, self.balk_tel, self.maan_tel, self.octagon_tel)) #hoeveelheid in kol
    
    def product_keuze_callback(self, request, response):
       self.keuze_event.clear()
       self.keuze_active = True
       self.keuze_response = response   # tijdelijk opslaan
       # GUI activeren in Tkinter thread
       self.root.after(0, self.enable_keuze_knoppen)
       self.keuze_maken()  # update status label
        # wacht tot gebruiker klikt
       self.keuze_event.wait()
       self.keuze_bezig()  # update status label
       
       return self.keuze_response
    
    def enable_keuze_knoppen(self):
        self.maan_button.config(state="normal")
        self.octagon_button.config(state="normal")
        self.balk_button.config(state="normal")
        self.kubus_button.config(state="normal")

    def keuze_gemaakt(self, keuze):
        if not self.keuze_active:
           return

        self.keuze_response.success = True
        self.keuze_response.message = keuze

        self.keuze_active = False
        self.keuze_event.set()

        self.maan_button.config(state="disabled")
        self.octagon_button.config(state="disabled")
        self.balk_button.config(state="disabled")
        self.kubus_button.config(state="disabled")


    def update_camera(self):
        if self.latest_frame is not None:

            ##image = Image.fromarray(self.latest_frame)###<---- code voor op echte camera
            image_1 = cv2.imread("/home/student/ros2_industrial_ws/robot_arm_b2/controller_code/test/test_camera_beeld.jpg")  ###<---- code voor test camera
            image_size=cv2.resize(image_1, (640, 480))
            # schaal naar gewenste grootte
            image_pil = Image.fromarray(image_size)
            #cv2/numpy naar pil image

            photo = ImageTk.PhotoImage(image_pil)
            #pil image naar tk image
            self.camera_label.config(image=photo)
            self.camera_label.image = photo

        


def main():
    rclpy.init()
    node = HMI()
    node.run()


    
if __name__ == "__main__":
    main()