# -*- coding: utf-8 -*-
import glfw
import imgui
import OpenGL.GL as gl
import sys
from ewmh import EWMH
from imgui.integrations.glfw import GlfwRenderer

class Backend:
    windowlist = []
    def init():
        imgui.create_context()

    def run_backend(create_window, shellwindow, window_coord):
        window = Backend.impl_glfw_init(
            shellwindow.window_title,
            shellwindow.min_size[0],
            shellwindow.min_size[1],
        )
        impl = GlfwRenderer(window)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        for window in Backend.windowlist:
            window = window # WindowBase
            pass
        while not glfw.window_should_close(window):
            glfw.poll_events()
            impl.process_inputs()
            imgui.new_frame()
            window_size = glfw.get_window_size(window)
            create_window()  # type: tuple
            shellwindow.apply_bounds()
            returned_size = shellwindow.window_size
            # imgui.show_test_window()
            # imgui.show_metrics_window()
            if returned_size and tuple(returned_size) != tuple(window_size):
                window_size = returned_size
                glfw.set_window_size(window, returned_size[0], returned_size[1])

            if tuple(shellwindow.pos) != (-1, -1):
                x, y = glfw.get_window_pos(window)
                req_x, req_y = shellwindow.pos
                if req_x == -1:
                    req_x = x
                if req_y == -1:
                    req_y = y
                if (req_x, req_y) != (x, y):
                    glfw.set_window_pos(window, req_x, req_y)

            gl.glClearColor(0, 0, 0, 0)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            glfw.swap_interval(1)
            imgui.render()
            impl.render(imgui.get_draw_data())
            glfw.swap_buffers(window)

        impl.shutdown()
        glfw.terminate()


    def impl_glfw_init(window_name, width, height):
        CLASS_NAME = "uxceptional"
        if not glfw.init():
            sys.exit("Could not initialize GLFW")

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint_string(glfw.X11_CLASS_NAME, CLASS_NAME)
        glfw.window_hint_string(glfw.X11_INSTANCE_NAME, CLASS_NAME)
        glfw.window_hint(glfw.FLOATING, glfw.TRUE)
        glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, glfw.TRUE)
        glfw.window_hint(glfw.FOCUS_ON_SHOW, glfw.TRUE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)
        
        # Create a windowed mode window and its OpenGL context
        window = glfw.create_window(
            int(width), int(height), window_name, None, None
        )
        glfw.make_context_current(window)

        if not window:
            glfw.terminate()
            print("Could not initialize Window")
            exit(1)

        return window
