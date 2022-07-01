import imgui
from enum import Enum, Flag, auto


class Direction(Flag):
    Nothing = 0
    Left = auto()
    Right = auto()
    Top = auto()
    Bottom = auto()
    Center = auto()


class MonitorPreference(Enum):
    Unset = 0
    Primary = auto()
    Active = auto()


class ShellWindow:
    """
    Represents the state and settings of an OS window managed by our application
    """

    def __init__(
        self,
        window_title="uxceptional",
        min_size=None,
        max_size=None,
        dock_direction=Direction.Nothing,
        monitor_preference=MonitorPreference.Unset,
        focus_on_show=False,
        user_resizable=False,
        is_statusbar=False

    ):
        if not min_size:
            min_size = [100, 100]

        self.min_size = min_size
        if not max_size:
            # Maybe this could be screen size
            max_size = [2147483647, 2147483647]

        self.max_size = max_size
        self.size = min_size
        self.padding = [0, 0]
        self.data = {}
        self.pos = [-1, -1]
        self.dock = dock_direction
        self.window_title = window_title
        self.monitor_preference = monitor_preference
        self.focus_on_show = focus_on_show
        self.user_resizable = user_resizable
        self.is_statusbar = is_statusbar
        self.renderer = None  # GlfwRenderer
        self.window_id = None
        self.context = None

    def init(self):
        """
        Initialize window for drawing
        Reset size calculations
        """
        self.style = imgui.get_style()
        self.size = self.min_size
        self.pos = [-1, -1] # anything but -1 is a request
        self.padding = [int(self.style.window_padding.x), int(self.style.window_padding.y)]

    def apply_bounds(self):
        """
        Apply min_size and max_size to size
        """
        width, height = self.size
        min_w, min_h = self.min_size
        max_w, max_h = self.max_size
        width = min(max(width, min_w), max_w)
        height = min(max(height, min_h), max_h)
        self.size = [int(width), int(height)]
        # We only add padding once because the cursor auto includes it
        self.window_size = [self.size[0] + self.padding[0], self.size[1] + self.padding[1]]

    def width_candidate(self):
        """
        Log current cursor position as a candidate for the width of the window
        """
        imgui.same_line()
        width = self.size[0]
        current = imgui.get_cursor_pos_x()
        if current > width:
            self.size[0] = current

        imgui.new_line()
        self.apply_bounds()

    def height_candidate(self):
        """
        Log current cursor position as a candidate for the height of the window
        """
        height = self.size[1]
        current = imgui.get_cursor_pos_y()
        if current > height:
            self.size[1] = current

        self.apply_bounds()
