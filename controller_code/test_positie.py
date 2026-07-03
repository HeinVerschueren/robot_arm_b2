#!/usr/bin/env python3
# Standalone test: stuurt de robot rechtstreeks naar Cartesische doelposities,
# ZONDER vision_node of controller.py ertussen — om te testen of de robot
# zelf nauwkeurig naar de opgegeven coordinaten beweegt, los van de
# camera-transformatie in transorm_camxy_robot_xy().
#
# Gebruik:
#   1. Start je normale robot-driver / MoveIt2 launch (dezelfde als anders),
#      maar laat vision_node en controller.py UIT staan.
#   2. Pas TEST_PUNTEN hieronder aan naar de marker-relatieve (x_mm, y_mm)
#      punten die je wilt testen (bv. je goede en slechte hoek).
#   3. Run dit script. Na elke beweging pauzeert het zodat je de werkelijke
#      TCP-positie t.o.v. de marker kan opmeten (liniaal) en vergelijken
#      met het opgegeven punt.

import math
import threading
import time
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
import tf_transformations

from my_moveit_python import srdfGroupStates, MovegroupHelper

# --- Zelfde transformatie-constanten als controller.py -----------------
TX = 362.2
TY = 324.8
THETA_DEG = 123.7
SCALE = 1.48  # compenseert te weinig afgelegde afstand vanaf de marker
Z_MM = 80.0          # zelfde vaste pick-hoogte als in transorm_camxy_robot_xy
Z_ROTATIE_DEG = 135.0  # zelfde offset als controller.py -> gripper recht t.o.v. de marker

# --- Testpunten: marker-relatieve (x_mm, y_mm) --------------------------
# Marker is 48x48mm -> rand zit op 24mm van het midden.
# +Y = richting robot (dus minder reikwijdte nodig), -Y = van robot af.
TEST_PUNTEN = [
    ("slecht punt (linksonder)", -50.0, 38.0),
    ("tegenoverliggende hoek (rechtsboven)", 49.0, 137.0),
]


def camxy_naar_robotxy(x_mm, y_mm):
    theta = math.radians(THETA_DEG)
    cos_t, sin_t = math.cos(theta), math.sin(theta)
    x_mm, y_mm = x_mm * SCALE, y_mm * SCALE
    x_rot = cos_t * x_mm - sin_t * y_mm
    y_rot = sin_t * x_mm + cos_t * y_mm
    return x_rot + TX, y_rot + TY


class TestPositie(Node):
    def __init__(self):
        super().__init__('test_positie')

        self.joint_names = [f"joint{i}" for i in range(1, 7)]
        self.base_link_name = "link_base"
        self.end_effector_name = "link6"
        self.group_name = "lite6"
        self.package_name = "my_uf_moveit_config"
        self.srdf_file_name = "config/uf_robot.srdf"

        self.group_states = srdfGroupStates(
            self.package_name, self.srdf_file_name, self.group_name)
        self.move_group = MovegroupHelper(
            self, self.joint_names, self.base_link_name,
            self.end_effector_name, self.group_name)

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Laag houden voor veiligheid tijdens testen
        self.move_group.moveit2.max_velocity = 0.15
        self.move_group.moveit2.max_acceleration = 0.15

    def move_naar_home(self):
        ok, joint_values = self.group_states.get_joint_values("home")
        if not ok:
            self.get_logger().error("Kon 'home' group state niet vinden in SRDF.")
            return
        self.get_logger().info("Bewegen naar 'home' (veilige startpositie)...")
        self.move_group.move_to_configuration(joint_values)

    def move_naar_mm(self, label, x_mm, y_mm):
        x_robot, y_robot = camxy_naar_robotxy(x_mm, y_mm)
        translation = [x_robot / 1000.0, y_robot / 1000.0, Z_MM / 1000.0]
        q = tf_transformations.quaternion_from_euler(
            math.radians(180), 0, math.radians(Z_ROTATIE_DEG))

        self.get_logger().info(
            f"[{label}] marker-relatief ({x_mm}, {y_mm}) mm  ->  "
            f"robot ({x_robot:.1f}, {y_robot:.1f}, {Z_MM:.1f}) mm")

        self.move_group.move_to_pose(translation, list(q))

    def huidige_pose(self, timeout_sec=5.0):
        deadline = time.time() + timeout_sec
        while not self.tf_buffer.can_transform(
                self.base_link_name, self.end_effector_name, rclpy.time.Time()):
            if time.time() > deadline:
                self.get_logger().error(
                    "Kon geen TF vinden tussen link_base en end-effector.")
                return None
            time.sleep(0.1)
        try:
            return self.tf_buffer.lookup_transform(
                self.base_link_name, self.end_effector_name, rclpy.time.Time())
        except TransformException as ex:
            self.get_logger().error(f"TF lookup mislukt: {ex}")
            return None

    def move_relatief(self, label, dx_mm=0.0, dy_mm=0.0, dz_mm=0.0):
        t = self.huidige_pose()
        if t is None:
            return
        translation = [
            t.transform.translation.x + dx_mm / 1000.0,
            t.transform.translation.y + dy_mm / 1000.0,
            t.transform.translation.z + dz_mm / 1000.0,
        ]
        rotation = [
            t.transform.rotation.x, t.transform.rotation.y,
            t.transform.rotation.z, t.transform.rotation.w,
        ]
        self.get_logger().info(
            f"[{label}] relatieve beweging: dx={dx_mm}mm dy={dy_mm}mm "
            f"dz={dz_mm}mm (robot-frame) -> nieuwe positie {translation}")
        self.move_group.move_to_pose(translation, rotation)


# Zuivere robot-nauwkeurigheidstest: beweegt in de EIGEN X/Y-as van de robot,
# zonder marker/rotatie/schaal-rekenwerk. Meet met een liniaal of de robot
# echt exact 100mm aflegt.
RELATIEVE_TESTEN = [
    ("100mm in robot-X", 100.0, 0.0),
    ("100mm in robot-Y", 0.0, 100.0),
]


def main():
    rclpy.init()
    node = TestPositie()

    # Belangrijk: pymoveit2 werkt via action-callbacks (goal accepted/result).
    # Die worden alleen verwerkt als de node daadwerkelijk gespind wordt.
    # Zonder dit blijft wait_until_executed() voor altijd hangen, ook als
    # de robot fysiek prima beweegt.
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.add_node(node.group_states)
    executor.add_node(node.move_group)
    spin_thread = threading.Thread(target=executor.spin, daemon=True)
    spin_thread.start()

    node.move_group.wait_for_moveit_services()

    input("Robot klaar en vrij van obstakels? Druk op Enter om naar 'home' te gaan...")
    node.move_naar_home()

    # --- Zuivere robot-nauwkeurigheidstest (geen marker/transform erbij) ---
    for label, dx_mm, dy_mm in RELATIEVE_TESTEN:
        input(f"Druk op Enter: markeer de HUIDIGE TCP-positie (bv. met tape/potlood), "
              f"dan beweegt hij '{label}' vanaf hier...")
        node.move_relatief(label, dx_mm=dx_mm, dy_mm=dy_mm)
        input(
            f"[{label}] Meet de WERKELIJKE afgelegde afstand tussen je markering "
            f"en de huidige TCP-positie (liniaal) en vergelijk met de bedoelde "
            f"{max(abs(dx_mm), abs(dy_mm)):.0f}mm. Druk op Enter om terug te bewegen..."
        )
        node.move_relatief(f"{label} (terug)", dx_mm=-dx_mm, dy_mm=-dy_mm)

    input("Relatieve tests klaar. Druk op Enter om de marker-hoekpunten te testen "
          "(of Ctrl+C om hier te stoppen)...")

    for label, x_mm, y_mm in TEST_PUNTEN:
        input(f"Druk op Enter om naar testpunt '{label}' te bewegen...")
        node.move_naar_mm(label, x_mm, y_mm)
        input(
            f"[{label}] Robot staat op doelpositie. Meet de WERKELIJKE "
            f"TCP-positie t.o.v. de marker op (liniaal) en noteer het "
            f"verschil. Druk op Enter om terug naar 'home' te gaan..."
        )
        node.move_naar_home()

    executor.shutdown()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
