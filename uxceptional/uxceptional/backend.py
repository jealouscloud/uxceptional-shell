# -*- coding: utf-8 -*-
import glfw
import imgui
import OpenGL.GL as gl
import sys
from ewmh import EWMH
from .glfwimpl import GlfwImpl
from .shellwindow import ShellWindow
from .windowbase import WindowBase


class Backend:
    windowlist = []
    fonts = {
        "default": None
    }

    def add_window(windowbase: WindowBase):
        """
        Must be called on the main thread.
        """
        shellwindow = windowbase.state
        default_font = Backend.fonts["default"]
        if default_font == None:
            shellwindow.context = imgui.create_context()
            imgui.set_current_context(shellwindow.context)
            io = imgui.get_io()
            Backend.fonts["default"] = io.fonts
        else:
            shellwindow.context = imgui.create_context(default_font)
            imgui.set_current_context(shellwindow.context)

        window = Backend.impl_glfw_init(
            shellwindow.window_title, *shellwindow.min_size
        )
        renderer = GlfwImpl(window)
        shellwindow.window_id = window
        shellwindow.renderer = renderer
        Backend.windowlist.append(windowbase)
        shellwindow.apply_monitor_preference()

    def run_backend():
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        while Backend.windowlist:
            for app_window in Backend.windowlist.copy():
                app_window = app_window  # type: WindowBase
                window_state = app_window.state
                gl_window = window_state.window_id
                impl = window_state.renderer # type: GlfwImpl
                glfw.make_context_current(gl_window)
                imgui.set_current_context(window_state.context)
                
                glfw.poll_events()
                if glfw.window_should_close(gl_window):
                    Backend.windowlist.remove(app_window)
                    # impl.shutdown() # Normally we would do this, but it just kills our shared font texture
                    glfw.destroy_window(gl_window)
                    # TODO: AN IMGUI CONTEXT LEAKS HERE?
                    continue


                impl.process_inputs()
                window_state.init() # Reset state for drawing
                imgui.new_frame()
                old_size = glfw.get_window_size(gl_window)
                app_window.run_create_window()
                window_state.apply_bounds() # Recalculate window size
                if tuple(window_state.size) != tuple(old_size):
                    new_size = window_state.size
                    glfw.set_window_size(gl_window, new_size[0], new_size[1])

                if tuple(window_state.pos) != (-1, -1):
                    x, y = glfw.get_window_pos(gl_window)
                    req_x, req_y = window_state.pos
                    if req_x == -1:
                        req_x = x
                    if req_y == -1:
                        req_y = y
                    if (req_x, req_y) != (x, y):
                        glfw.set_window_pos(gl_window, req_x, req_y)

                gl.glClearColor(0, 0, 0, 0)
                gl.glClear(gl.GL_COLOR_BUFFER_BIT)
                # glfw.swap_interval(1)
                imgui.render()
                impl.render(imgui.get_draw_data())
                glfw.swap_buffers(gl_window)

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
