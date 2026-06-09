import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_msgs.msg import Float32
from std_msgs.msg import Bool
import tkinter as tk
from tkinter import ttk


class HMI(Node):
    def __init__(self):
        super().__init__('HMI_node')
        self.publisher_start_stop = self.create_publisher(
        Bool,    #bool for start and stop button
        'start',   #send to /start
        10   #backlog of msg to send
        )

        self.publisher_automate = self.create_publisher(
        Bool,    #bool for start and stop button
        'automate',   #send to /start
        10   #backlog of msg to send
        )

        self.publisher_reset = self.create_publisher(
        Bool,    #bool for start and stop button
        'reset',   #send to /start
        10   #backlog of msg to send
        )

        self.publisher_voice_on = self.create_publisher(
        Bool,    #bool for start and stop button
        'voice_on',   #send to /start
        10   #backlog of msg to send
        )

        self.publisher_shut_down = self.create_publisher(
        Bool,    #bool for start and stop button
        'shut_down',   #send to /start
        10   #backlog of msg to send
        )
        self.publisher_snelheid = self.create_publisher(
        Float32,    #bool for start and stop button
        'snelheid',   #send to /start
        10   #backlog of msg to send
        )

        self.publisher_threshold = self.create_publisher(
        Float32,    #bool for start and stop button
        'threshold',   #send to /start
        10   #backlog of msg to send
        )

        self.publisher_manual_overide = self.create_publisher(
        Bool,    #bool for start and stop button
        'manual_overide',   #send to /start
        10   #backlog of msg to send
        )


######################## window with buttons and such  ###################

        self.root = tk.Tk()  #main window
        self.root.title("Mijn GUI") #title of window
        self.root.geometry("1000x600")

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

        self.checkbox_auto = tk.BooleanVar()  #make variable for switch
        self.switch_auto = tk.Checkbutton(  #for switch
           self.root,
           text="automatisch",
           variable=self.checkbox_auto
           )
        self.switch_auto.grid(row=3, column=0, padx=10, pady=5, sticky="nw")   #make visiable in window

        self.checkbox_voice_on = tk.BooleanVar()  #make variable for switch
        self.switch_voice_on = tk.Checkbutton(  #for switch
           self.root,
           text="voice command",
           variable=self.checkbox_voice_on
           )
        self.switch_voice_on.grid(row=4, column=0, padx=10, pady=5, sticky="nw")   #make visiable in window

        self.button_exit = tk.Button( #make button
            self.root,
            text="Afsluiten",  #name
            command=self.close  #function
            )
        self.button_exit.grid(row=10, column=0, padx=10, pady=5, sticky="nw")   #make visiable

        tk.Label(self.root, text="Snelheid (%)").grid(row=5, column=0, sticky="w")

        self.number_var_snelheid = tk.IntVar()  #maakt make number varibale for hmi
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

        self.number_var_threshold = tk.IntVar()  # make number varibale for hmi
        self.number_entry_threshold = tk.Entry(
            self.root,
            textvariable=self.number_var_threshold,
            width=5)
        self.number_entry_threshold.grid(row=8, column=0, padx=10, pady=5, sticky="nw")

        button = tk.Button(
            self.root,
            text="stuur threshold",
            command=self.threshold_zendt)
        button.grid(row=8, column=1, padx=10, pady=5, sticky="nw")

        self.checkbox_manual_overide = tk.BooleanVar()  #make variable for switch
        self.switch_manual_overide = tk.Checkbutton(  #for switch
           self.root,
           text="manual override",
           variable=self.checkbox_manual_overide
           )
        self.switch_manual_overide.grid(row=9, column=0, padx=10, pady=5, sticky="nw")   #make visiable in window


        self.columns = ("kubus", "balk", "maan", "ocatagon")  #naam colomen
        self.tree = ttk.Treeview(self.root, columns=self.columns, show="headings", height=1) 
        for col in self.columns:    #maakt collomen aan
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80)
        self.tree.insert("", tk.END, values=("3", "25", "6","test"))  #hoeveelheid in kolom
        self.tree.grid(row=0, column=4, rowspan=2, padx=20, pady=5, sticky="ne")  #zorgt for rechts tabel

        self.status_grijper = tk.StringVar()
        self.status_grijper.set("grijper: open")

        self.status_label_grijper = tk.Label(
            self.root,
            textvariable=self.status_grijper,
            bg="gray",
            fg="white",
            width=20
        )
        self.status_label_grijper.grid(row=0, column=2, padx=20, pady=5, sticky="n")

        self.status_robot = tk.StringVar()
        self.status_robot.set("robot: stand-by")

        self.status_label_robot = tk.Label(
            self.root,
            textvariable=self.status_robot,
            bg="orange",
            fg="white",
            width=20
        )
        self.status_label_robot.grid(row=1, column=2, padx=20, pady=5, sticky="n")

############ end classs #########################

    def run(self):
        self.root.mainloop()  #activeeerd HMI

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
        msg=Float32()
        snelheid=float(self.number_var_snelheid.get())
        msg.data=snelheid
        self.publisher_snelheid.publish(msg)

    def threshold_zendt(self):
        msg=Float32()
        msg.data=float(self.number_var_threshold.get())
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

def main():
    rclpy.init()
    node = HMI()
    node.run()
    rclpy.spin(node)

    
if __name__ == "__main__":
    main()