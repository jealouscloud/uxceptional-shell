"""
Example statusbar
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "uxceptional"))
from pathlib import Path

import glfw
import imgui

import uxceptional.apputils as utils
from uxceptional import (Backend, DataFetcher, Direction, MonitorPreference,
                         ShellWindow, WindowBase)


class DataSource:
    """
    Async data sources
    """
    async def time(data):
        result = await utils.run_async("date")
        return result.stdout.strip()
    
    async def spotify(data):
        playerctl_status = await utils.run_async("playerctl status -p spotify", shell=True)
        if playerctl_status.returncode != 0:
            return {
                "state": "Stopped",
                "title": "spotify not running",
            }

        playing = await utils.run_async(
            "playerctl metadata -p spotify --format '{{ artist }} - {{ title }}'",
            shell=True,
        )

        return {
            "state": playerctl_status.stdout.strip(),  # Playing or Paused
            "title": playing.stdout.strip(),
        }


class TestPopupWindow(WindowBase):
    def __init__(self) -> None:
        super().__init__()
        self.state = ShellWindow(dock_direction=Direction.Center, monitor_preference=MonitorPreference.Primary)

    def create_window(self):
        state = self.state
        with self.imgui_window("Task window"):
            imgui.text("This is a popup confirming ya clicked the bar")
            state.width_candidate()
            imgui.button("I understand")
            state.width_candidate()
            imgui.same_line()
            imgui.button("Cancel")
            state.height_candidate()
            state.apply_bounds()
            imgui.set_window_size(*state.size)


class BottomStatusBar(WindowBase):
    """
    Simple implementation of what a statusbar could look like
    """
    def __init__(self) -> None:
        super().__init__()
        self.state = ShellWindow(dock_direction=Direction.Bottom, is_statusbar=True)

        self.data["bar_size"] = 32
        # Pay attention to the datafetcher key names here
        # that is how their data is accessed later.
        self.attach_data(
            DataFetcher(
                key="time", function=DataSource.time, delay_ms=100
            )
        )
        self.attach_data(
            DataFetcher(
                key="spotify", function=DataSource.spotify, delay_ms=1000
            )
        )
        self.textures = {}

    def init_hook(self):
        self.textures = {
            "spotify": utils.load_icon("spotify", 16),
        }
        

    def widget_button(self):
        if imgui.button("Charm"):
            Backend.add_window(TestPopupWindow())

    def widget_spotify(self):
        data = self.data.get("spotify", None)
        if not data:
            return  # Don't render anything
        
        column_width = imgui.get_column_width()
        cursor = imgui.get_cursor_pos()
        text = ""
        color = None
        if data["state"] == "Stopped":
            text = "[spotify not open]"
        elif data["state"] == "Playing":
            color = "#50fa7b"
            text = (data["title"])
        elif data["state"] == "Paused":
            text = data["title"]

        text_size = imgui.calc_text_size(text)
    
        ICON_PADDING = 2
        ICON_SIZE = 16
        centered_x = (column_width / 2) -  int(round(text_size.x / 2))
        imgui.set_cursor_pos((cursor.x + centered_x - (ICON_SIZE + ICON_PADDING), cursor.y - ICON_PADDING))
        self.imgui_icon("spotify", ICON_SIZE)
        imgui.set_cursor_pos((cursor.x + centered_x, cursor.y))
        if color:
            imgui.text_colored(text, *utils.vec_color(color))
        else:
            imgui.text(text)
        color = None
        return (text_size.x + 16, text_size.y)

        
    def left_controls(self):
        self.widget_button()
        imgui.same_line()

    def center_controls(self):
        self.widget_spotify()

    def right_controls(self):
        time = self.data.get("time", None)
        if not time:
            return

        imgui.text(time)

    def setup_bar(self):
        state = self.state
        data = self.data
        primary_monitor = glfw.get_primary_monitor()
        x, y, workarea_width, height = glfw.get_monitor_workarea(
            primary_monitor
        )
        state.min_size = [workarea_width, data["bar_size"]]
        state.max_size = state.min_size
        state.pos = [x, y + height - data["bar_size"]]
        state.apply_bounds()
        imgui.set_next_window_size(*state.size)

    def create_window(self):
        self.setup_bar()
        with self.imgui_window("bottom bar"):
            imgui.columns(3, "bar")
            self.left_controls()
            imgui.next_column()
            self.center_controls()
            imgui.next_column()
            self.right_controls()
            imgui.columns(1)


bar = BottomStatusBar()
bar.blocking = False
Backend.add_window(bar)
try:
    Backend.run_backend()
except KeyboardInterrupt:
    pass
