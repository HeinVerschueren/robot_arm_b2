#!/usr/bin/env python3

# Naam Student:
# Studentnummer:
# Datum:
# Verklaring: Door het inleveren van dit bestand verklaar ik dat ik deze opdracht zelfstandig heb uitgevoerd en 
# dat ik geen code van anderen heb gebruikt. Tevens ga ik akkoord met de beodordeling van deze opdracht.

from threading import Thread

import rclpy
import time
import math
from rclpy.executors import MultiThreadedExecutor   
from rclpy.node import Node

from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
from my_moveit_python import srdfGroupStates
from my_moveit_python import MovegroupHelper
import tf_transformations

from xarm_msgs.srv import VacuumGripperCtrl

from enum import Enum
from std_msgs.msg import Bool, String, Float32
from std_srvs.srv import Trigger
import json

# Status van de robot
class RobotState(Enum):
    HOME = 0
    wachtOpStart = 1
    RIGHT = 2
    wachtOpTransferFrame = 3
    PRE_PICK = 4
    PICK = 5
    MOVE_OVER = 6
    LEFT = 7
    PLACE = 8
    COMPLETE = 9
    ERROR = 10
    ESTOP = 11

# Gripper classe
class VacuumGripper(Node):
    def __init__(self):
        super().__init__('vacuum_gripper')

        self.client = self.create_client(
            VacuumGripperCtrl,
            '/xarm/set_vacuum_gripper')

        self.grijper_pub = self.create_publisher(Bool, "/grijper", 10)

        while not self.client.wait_for_service(timeout_sec=2.0):
            self.get_logger().info(
                'Waiting for vacuum gripper service...')

    def close(self):
        request = VacuumGripperCtrl.Request()
        request.on = True
        #request.wait = True
        self.grijper_pub = True

        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future)

        return future.result()

    def release(self):
        request = VacuumGripperCtrl.Request()
        request.on = False
        #request.wait = True
        self.grijper_pub = False

        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future)

        return future.result()

# Manipulator classe
class manipulatorController(Node):
    def __init__(self, node_name):
        
        # TEST TRANSFERFRAMES VERWIJDER ECHTE TEST
        self.TEST_MODE = True   # zet op False voor echte robot

        # State van de robot init
        self.state = RobotState.HOME

        self.start_signal = False
        self.stop_signal = False
        self.mode_auto = False #True
        self.manual_override = False

        self.estop = False

        self.gripper = VacuumGripper()

        self.transfer_translation = None
        self.transfer_rotation = None

        super().__init__(node_name)

        # Robot parameters
        prefix = ""
        self.joint_names = [
            prefix + "joint1",
            prefix + "joint2",
            prefix + "joint3",
            prefix + "joint4",
            prefix + "joint5",
            prefix + "joint6",
        ]
        self.base_link_name = "link_base"
        self.end_effector_name = "link6" #"link_eef"
        self.group_name = "lite6" #"xarm6"
        self.package_name = "my_uf_moveit_config" #"manipulation_moveit_config"
        self.srdf_file_name = "config/uf_robot.srdf" #"config/manipuation_environment.srdf"

        # TF setup
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # MoveIt helpers
        self.group_states = srdfGroupStates(
            self.package_name, self.srdf_file_name, self.group_name
        )
        self.move_group = MovegroupHelper(
            self, self.joint_names, self.base_link_name, self.end_effector_name, self.group_name
        )

        # --- Create subscribers, publishers, clients, timers here ---

        self.get_logger().info("manipulator node has been initialized.")

        # Publishers
        self.handshake_pub = self.create_publisher(Bool, "/handshake", 10)

        self.error_pub = self.create_publisher(Bool,"/robot_error",10)

        self.cycle_complete_pub = self.create_publisher(Bool, "/cycle_complete", 10)

        # Subscribers
        self.start_sub = self.create_subscription(
        Bool, "/start_signal", self.start_cb, 10)

        self.stop_sub = self.create_subscription(
        Bool, "/stop_signal", self.stop_cb, 10)

        self.mode_sub = self.create_subscription(
        Bool, "/robot_mode", self.mode_cb, 10)

        self.bin_sub = self.create_subscription(
        String, "/bak_locatie", self.bin_cb, 10)
        
        '''
        self.estop_sub = self.create_subscription(
        Bool, "/estop", self.estop_cb, 10)

        self.reset_sub = self.create_subscription(
        Bool, "/estop_reset", self.reset_cb, 10)
        '''

        self.speed_scale = 0.2  # default snelheid (50%)

        self.speed_sub = self.create_subscription(
        Float32, "/speed_scale", self.speed_cb, 10)

        self.manual_override_sub = self.create_subscription(
        Bool, "/manual_overide", self.manual_override_cb, 10)

        # Service clients
        self.call_for_product = self.create_client(Trigger, "/call_for_product")
        while not self.call_for_product.wait_for_service(timeout_sec=3.0):
            self.get_logger().info("Waiting for product service...")

    # --- Create callback functions here ---

    def start_cb(self, msg):
        self.start_signal = msg.data

    def stop_cb(self, msg):
        self.stop_signal = msg.data

    def mode_cb(self, msg):
        self.mode_auto = msg.data

    def bin_cb(self, msg):
        data = json.loads(msg.data)

        self.bin_translation = [
            data["x"],
            data["y"],
            data["z"]
        ]

        # vaste oriëntatie van de bak
        self.bin_rotation = [1.0, 0.0, 0.0, 0.0]

        self.get_logger().info(
            f"Nieuwe baklocatie: {self.bin_translation}")

    def estop_cb(self, msg):
        self.estop = msg.data
        self.state = RobotState.ESTOP

    def reset_cb(self, msg):
        if msg.data:
            self.estop = False
            self.state = RobotState.HOME

    def publish_error(self):
        msg = Bool()
        msg.data = True
        self.error_pub.publish(msg)

    def publish_cycle_done(self):
        msg = Bool()
        msg.data = True
        self.cycle_complete_pub.publish(msg)

    def publish_handshake(self):
        msg = Bool()
        msg.data = True
        self.handshake_pub.publish(msg)

    def speed_cb(self, msg):
        # clamp tussen 0.05 en 1.0 (veilig voor robot)
        scale = max(0.05, min(1.0, float(msg.data)))

        self.speed_scale = scale

        # pas MoveIt snelheid aan
        self.move_group.moveit2.max_velocity = scale
        self.move_group.moveit2.max_acceleration = scale

    def call_for_product_location(self):
        request = Trigger.Request()

        future = self.call_for_product.call_async(request)
        self.get_logger().info("Wachten op product...")

        while not future.done():

            # Manual override
            if self.manual_override:
                self.get_logger().warn("Manual override tijdens wachten op product")
                future.cancel()
                return False

            # E-stop
            if self.estop:
                self.get_logger().warn("E-stop tijdens wachten op product")
                future.cancel()
                return False

            time.sleep(0.05)

        result = future.result()

        if result is None:
            return False

        if result.success:

            data = json.loads(result.message)

            self.transfer_translation = [
                data["x"] / 1000.0,
                data["y"] / 1000.0,
                data["z"] / 1000.0
            ]

            q = tf_transformations.quaternion_from_euler(
                math.radians(180), 0, math.radians(data["z_rotatie"]))

            self.transfer_rotation = list(q)

            self.get_logger().info(
                f"Ontvangen product: pos={self.transfer_translation}, "
                f"rot={data['z_rotatie']}°"
            )

            return True

        return False
    
    def manual_override_cb(self, msg):
        self.manual_override = msg.data

        if self.manual_override:
            self.get_logger().warn("MANUAL OVERRIDE ACTIVE → returning to HOME")

            # reset inputs zodat robot niet doorgaat
            self.transfer_translation = None
            self.transfer_rotation = None
            self.start_signal = False
            self.stop_signal = False


    # --- Motion primitives ------------------------------------------------
    def move_to_state(self, state_name: str):
        result, joint_values = self.group_states.get_joint_values(state_name)
        if not result:
            self.get_logger().error(f"Failed to get joint values for state '{state_name}'.")
        self.get_logger().info(f"Moving to state '{state_name}'.")
        self.move_group.move_to_configuration(joint_values)

    def move_to_pose(self, translation, rotation):
        self.get_logger().info(f"Moving to pose: {translation}, {rotation}")
        self.move_group.move_to_pose(translation, rotation)

    def move_to_tf(self, from_frame: str, to_frame: str):
        try:
            t = self.tf_buffer.lookup_transform(
                to_frame, from_frame, rclpy.time.Time()
            )
            translation = [
                t.transform.translation.x,
                t.transform.translation.y,
                t.transform.translation.z,
            ]
            rotation = [
                t.transform.rotation.x,
                t.transform.rotation.y,
                t.transform.rotation.z,
                t.transform.rotation.w,
            ]
            self.get_logger().info(f"Moving to transform: {from_frame} → {to_frame}")
            self.move_to_pose(translation, rotation)
        except TransformException as ex:
            self.get_logger().warn(f"Could not transform {to_frame} to {from_frame}: {ex}")
    

    
    def safe_move_to_state(self, state_name, retries=3):

        result, joint_values = self.group_states.get_joint_values(state_name)

        for attempt in range(retries):

            self.move_group.moveit2.move_to_configuration(joint_values)

            success = self.move_group.moveit2.wait_until_executed()

            if success:
                return True

            self.get_logger().warn(f"Poging {attempt+1} mislukt")
            time.sleep(0.2)

        self.get_logger().error(f"{state_name} permanent mislukt")
        return False


    def safe_move_to_pose(self, translation, rotation, retries=3):

        for attempt in range(retries):

            self.move_to_pose(translation, rotation)

            if self.move_group.moveit2.motion_suceeded:
                return True

            self.get_logger().warn(
                f"Pose planning mislukt ({attempt+1}/{retries})"
            )
            time.sleep(0.2)

        return False


    # --- App sequence ----------------------------------------------------

    def execute_app(self):

        self.move_to_state("home")
        self.state = RobotState.wachtOpStart

        rate = self.create_rate(10)

        while rclpy.ok():

            if self.manual_override:
                self.get_logger().warn("Going home...")
                self.safe_move_to_state("home")
                self.state = RobotState.wachtOpStart
                self.manual_override = False
                time.sleep(0.1)
                continue

            if self.estop:
                time.sleep(0.1)
                continue

            # ---------------- HOME / WAIT START ----------------
            if self.state == RobotState.wachtOpStart:
                self.publish_handshake()
                self.manual_override = False

                if self.start_signal:
                    self.start_signal = False

                    if not self.safe_move_to_state("right"):
                        self.publish_error()
                        self.safe_move_to_state("home")
                        self.state = RobotState.wachtOpStart
                        continue
                    self.state = RobotState.wachtOpTransferFrame

            # ---------------- Wacht op transferframe----------------
            elif self.state == RobotState.wachtOpTransferFrame:


                #timeout = time.time() + 10.0
                
                product_ok = self.call_for_product_location()

                if self.manual_override:
                    self.safe_move_to_state("home")
                    self.manual_override = False
                    self.state = RobotState.wachtOpStart
                    continue

                if not product_ok:
                    self.publish_error()
                    self.safe_move_to_state("home")
                    self.state = RobotState.wachtOpStart
                    continue

                self.state = RobotState.PRE_PICK

            # ---------------- PRE PICK ----------------
            elif self.state == RobotState.PRE_PICK:
                
                if self.transfer_translation is None:
                    self.publish_error()
                    self.state = RobotState.ERROR
                    continue

                pre = self.transfer_translation.copy()
                pre[2] += 0.02  # 2 cm boven object

                self.get_logger().info(f"pre_pick = {pre}")

                if not self.safe_move_to_pose(pre, self.transfer_rotation):
                    self.state = RobotState.ERROR
                    continue

                self.state = RobotState.PICK

            # ---------------- PICK ----------------
            elif self.state == RobotState.PICK:

                if self.transfer_translation is None:
                    self.publish_error()
                    self.state = RobotState.ERROR
                    continue

                self.gripper.release()
                time.sleep(0.2)

                self.move_to_pose(
                    self.transfer_translation,
                    self.transfer_rotation)

                self.gripper.close()

                time.sleep(0.5)

                self.state = RobotState.MOVE_OVER

            # ---------------- MOVE OVER ----------------
            elif self.state == RobotState.MOVE_OVER:
                
                #for state in ["home", "left"]:
                self.move_to_pose(translation=[0.20, 0.20, 0.20], 
                                  rotation=[1, 0, 0, 0])
                time.sleep(0.1)
                self.move_to_state("right")

                for state in ["right", "left"]:
                    self.safe_move_to_state(state)
                    time.sleep(0.1)
                
                self.state = RobotState.PLACE

            # ---------------- PLACE ----------------
            elif self.state == RobotState.PLACE:

                self.safe_move_to_pose(
                    self.bin_translation,
                    self.bin_rotation)

                self.gripper.release()

                self.transfer_translation = None
                self.transfer_rotation = None

                self.publish_cycle_done()

                # STOP LOGICA
                if self.stop_signal:
                    self.stop_signal = False
                    self.move_to_state("home")
                    self.state = RobotState.wachtOpStart

                # AUTO MODE
                elif self.mode_auto:

                    for state in ["home", "right"]:
                        self.move_to_state(state)
                        time.sleep(0.3)
                    self.state = RobotState.wachtOpTransferFrame

                # MANUAL MODE
                else:
                    self.move_to_state("home")
                    self.state = RobotState.wachtOpStart

                self.transfer_translation = None
                self.transfer_rotation = None

            rate.sleep()

# --------------------------------------------------------------------------
# Do not modify the main function unless necessary.
# -------------------------------------------------------------------------
def main(args=None):
    rclpy.init(args=args)

    # Instantiate the manipulatorController node.
    # NOTE: This must be done before creating the executor to ensure callbacks are registered correctly.
    node = manipulatorController("manipulatorCodeB2")

    # Create a multithreaded executor with 2 threads.
    # Allows the node to handle multiple callbacks concurrently (e.g., subscriptions, timers).
    executor = MultiThreadedExecutor(num_threads=2)

    # Add the node to the executor so it can process its callbacks.
    executor.add_node(node)

    # Start the executor in a separate background thread.
    # Keeps the ROS event loop running while allowing the main thread to execute custom logic.
    executor_thread = Thread(target=executor.spin, daemon=True)
    executor_thread.start()

    # Create a 1 Hz rate object and sleep once to allow initialization.
    # Provides time for system setup (e.g., MoveIt, TF) before running main logic.
    node.create_rate(1.0).sleep()

    # Execute the main application logic defined in the node.
    # Typically runs robot motion, computations, or control behaviors.
    #time.sleep(5.0)
    node.execute_app()

    # Shutdown ROS gracefully after main logic completes.
    rclpy.shutdown()

    # Wait for the executor thread to exit cleanly before terminating the program.
    executor_thread.join()



if __name__ == "__main__":
    main()

