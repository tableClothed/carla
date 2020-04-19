import glob
import os
import sys

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass


# --------------------------------------------------------
# --------------------------------------------------------


import carla
import random
import time
import cv2
import numpy as np
import math


SHOW_PREV = False
IM_WIDTH, IM_HEIGHT = 640, 480


class CarEnvironment:
    SHOW_CAM = SHOW_PREV
    STEER_ATM = 1.0
    actor_list = []
    front_camera = None
    collision_hist = []


    def __init__(self):

        try:
            self.client = carla.Client('localhost', 2000)
            self.client.set_timeout(5.0)

            self.world = self.client.get_world()

            blueprint_library = self.world.get_blueprint_library()
            self.model_3 = blueprint_library.filter('model3')[0]


        def reset(self):
            self.collision_hist = []
            self.actor_list = []


            self.transform = random.choice(self.world.get_map().get_spawn_points())

            self.vehicle = world.spawn_actor(self.model_3, self.transform)

            self.actor_list.append(self.vehicle)

            self.rgb_cam = self.world.blueprint_library.find('sensor.camera.rgb')

            self.rgb_cam.set_attribute('image_size_x', str(IM_WIDTH))
            self.rgb_cam.set_attribute('image_size_y', str(IM_HEIGHT))
            self.rgb_cam.set_attribute('fov', '110')

            transform = carla.Transform(carla.Location(x=2.5, z=0.7))

            self.sensor = self.world.spawn_actor(self.rgb_cam, transform, attach_to=self.vehicle)

            self.actor_list.append(self.sensor)
            self.sensor.listen(lambda data: self.process_img(data))

            self.vehicle.apply_control(carla.VehicleControl(throttle=1.0, steer=0.0))

            time.sleep(4)


        def process_img(self, image):
            i = np.array(image.raw_data)
            i2 = i.reshape((IM_HEIGHT, IM_WIDTH, 4))
            i3 = i2[:, :, :3]
            cv2.imshow("", i3)
            cv2.waitKey(1)
            return i3/255.0


        def collision_data(self, event):
            self.collision_hist.append(event)
        

        def step(self, action):

            # 0 - left
            # 1 - center
            # 2 - right

            if action == 0:
                self.vehicle.apply_control(carla.VehicleControl(throttle=1.0, steer=0))
            if action == 1:
                self.vehicle.apply_control(carla.VehicleControl(throttle=1.0, steer=-1*self.STEER_AMT))
            if action == 2:
                self.vehicle.apply_control(carla.VehicleControl(throttle=1.0, steer=1*self.STEER_AMT))

            v = self.vehicle.get_velocity()
            kmh = int(3.6 * math.sqrt(v.x**2, v.y**2 + v.z**2))

            if len(self.collision_hist) != 0:
                done = True
                reward = -200
            elif kmh < 50:
                done = False
                reward = -1
            else:
                done = False
                reward = 1

            # SECONDS_PER_EPISODE = 1000
            
            if self.episode_start + SEC_PER_EPISODE < time.time():
                done = True

            return self.front_camera, reward, done, None