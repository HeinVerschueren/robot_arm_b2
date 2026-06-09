#!/usr/bin/env python3

# Naam Student:
# Studentnummer:
# Datum:
# Verklaring: Door het inleveren van dit bestand verklaar ik dat ik deze opdracht zelfstandig heb uitgevoerd en 
# dat ik geen code van anderen heb gebruikt. Tevens ga ik akkoord met de beoordeling van deze opdracht.

import time
import rclpy

from rclpy.node import Node
from xarm_msgs.srv import VacuumGripperCtrl


class VacuumGripper(Node):
    def __init__(self):
        super().__init__('vacuum_gripper')

        self.client = self.create_client(
            VacuumGripperCtrl,
            '/xarm/set_vacuum_gripper'
        )

        while not self.client.wait_for_service(timeout_sec=2.0):
            self.get_logger().info(
                'Waiting for vacuum gripper service...'
            )

    def pull(self):
        request = VacuumGripperCtrl.Request()
        request.on = True
        #request.wait = True

        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future)

        return future.result()

    def release(self):
        request = VacuumGripperCtrl.Request()
        request.on = False
        #request.wait = True
s
        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future)

        return future.result()


def main(args=None):
    rclpy.init(args=args)

    gripper = VacuumGripper()

    gripper.pull()
    time.sleep(1.0)
    gripper.release()

    gripper.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()