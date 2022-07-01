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
    windowqueue = []
    fonts = {
        "default": None
    }
    def add_window(windowbase: WindowBase):
        """Add a window

        Args:
            windowbase (WindowBase): Window to add
        """
        Backend.windowqueue.append(windowbase)

    def _add_window(windowbase: WindowBase, fontfiles = []):
        """
        Must be called on the main thread.
        """
        shellwindow = windowbase.state
        shellwindow.context = imgui.create_context()
        imgui.set_current_context(shellwindow.context)
        io = imgui.get_io()
        for font in fontfiles:
            io.fonts.add_font_from_file_ttf(font)

        window = Backend.glfw_init_window(
            shellwindow
        )
        renderer = GlfwImpl(window)
        shellwindow.window_id = window
        shellwindow.renderer = renderer
        Backend.windowlist.append(windowbase)
        shellwindow.apply_monitor_preference()

    def add_windows_from_queue():
        """
        Process and clear the window creation queue
        """        
        for windowbase in Backend.windowqueue:
            Backend._add_window(windowbase)
        if Backend.windowlist:
            Backend.windowqueue.clear()

    def run_backend():
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        while Backend.windowlist or Backend.windowqueue:
            ## Create windows from queue
            Backend.add_windows_from_queue()
            for app_window in Backend.windowlist.copy():
                app_window = app_window  # type: WindowBase
                window_state = app_window.state
                gl_window = window_state.window_id
                impl = window_state.renderer # type: GlfwImpl
                #region context grabbing
                glfw.make_context_current(gl_window)
                imgui.set_current_context(window_state.context)
                #endregion
                
                glfw.poll_events()
                if glfw.window_should_close(gl_window):
                    Backend.windowlist.remove(app_window)
                    impl.shutdown()
                    glfw.destroy_window(gl_window)
                    # TODO: AN IMGUI CONTEXT LEAKS HERE?
                    continue


                impl.process_inputs()
                old_size = window_state.size
                window_state.init() # Reset state for drawing
                imgui.new_frame()
                window_size = glfw.get_window_size(gl_window)
                app_window.set_theme()
                app_window.run_create_window()
                app_window.unset_theme()
                window_state.apply_bounds() # Recalculate window size

                #region repositioning and resizing
                if (tuple(window_state.size) != tuple(old_size) or 
                        tuple(window_state.size) != tuple(window_size)):
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
                #endregion

                gl.glClearColor(0, 0, 0, 0)
                gl.glClear(gl.GL_COLOR_BUFFER_BIT)
                
                imgui.render()
                impl.render(imgui.get_draw_data())
                glfw.swap_buffers(gl_window)

        glfw.terminate()

    def glfw_init_window(shellwindow: ShellWindow):
        CLASS_NAME = "uxceptional"
        if not glfw.init():
            sys.exit("Could not initialize GLFW")

        width, height = shellwindow.min_size
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint_string(glfw.X11_CLASS_NAME, CLASS_NAME)
        glfw.window_hint_string(glfw.X11_INSTANCE_NAME, CLASS_NAME)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)
        
        # Tell our WM we don't want to tile
        glfw.window_hint(glfw.FLOATING, glfw.TRUE)
        # Enable transparency
        glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, glfw.TRUE)
        if shellwindow.focus_on_show:
            glfw.window_hint(glfw.FOCUS_ON_SHOW, glfw.TRUE)
        

        # Create a windowed mode window and its OpenGL context
        window = glfw.create_window(
            int(width), int(height), shellwindow.window_title, None, None
        )
        glfw.make_context_current(window)
        glfw.swap_interval(1) # enable vsync

        if not window:
            glfw.terminate()
            print(f"Could not initialize Window {shellwindow.window_title}")
            exit(1)

        return window
