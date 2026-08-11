import pyray as rl
from pyray import (Rectangle as Rect, Vector2 as Vec2, Vector3 as Vec3, BoundingBox)

rl.init_window(800, 450, "Hello")

cam_pos = Vec3(0, 10, 10)
look_target = Vec3(0, 0, 0)
camera_up = Vec3(0, 1, 0)
camera = rl.Camera3D(cam_pos, look_target, camera_up, 45, rl.CAMERA_PERSPECTIVE)


while not rl.window_should_close():
    rl.begin_drawing()
    rl.clear_background(rl.WHITE)
    rl.draw_text("Hello world", 190, 200, 20, rl.VIOLET)

    rl.begin_mode_3d(camera)

    rl.draw_grid(100, 1)

    rl.end_mode_3d()

    rl.end_drawing()

rl.close_window()
