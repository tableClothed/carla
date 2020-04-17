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


im_width, im_height = 640, 480


def process_img(image):
    i = np.array(image.raw_data)
    i2 = i.reshape((im_height, im_width, 4))
    i3 = i2[:, :, :3]
    cv2.imshow("", i3)
    cv2.waitKey(1)
    return i3/255.0

actor_list = []

try:
    client = carla.Client('localhost', 2000)
    client.set_timeout(5.0)

    world = client.get_world()

    blueprint_library = world.get_blueprint_library()
    bp = blueprint_library.filter('model3')[0]
    print(bp)

    spawn_point = random.choice(world.get_map().get_spawn_points())

    vehicle = world.spawn_actor(bp, spawn_point)
    vehicle.apply_control(carla.VehicleControl(throttle=1.0, steer=0.0))
    # vehicle.set_autopilot(True)

    actor_list.append(vehicle)

    # sleep for 5 sec, then finish:
    # time.sleep(5)

    blueprint = blueprint_library.find('sensor.camera.rgb')
    # changing dimensions

    blueprint.set_attribute('image_size_x', str(im_width))
    blueprint.set_attribute('image_size_y', str(im_height))
    blueprint.set_attribute('fov', '110')

    # adjust sensor and attach to vehicle
    spawn_point = carla.Transform(carla.Location(x=2.5, z=0.7))

    # spawn sensor and attach to vehicle
    sensor = world.spawn_actor(blueprint, spawn_point, attach_to=vehicle)

    # add sensor to list of actors
    actor_list.append(sensor)

    sensor.listen(lambda data: process_img(data))

    time.sleep(5)

finally:
    print('destroying actors')
    for actor in actor_list:
        actor.destroy()
    print('done.')