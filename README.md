# uxceptional-shell
An exceptional framework for building Linux desktop shells including statusbars, notification trays, and other things.

uxceptional uses:
* glfw
* imgui through `pyimgui`
* asyncio for passive data grabbing

Users of this library are intended to define their own imgui windows by implementing `WindowBase`

A basic example
```python
from uxceptional import WindowBase, Direction, MonitorPreference, ShellWindow, DataFetcher
import uxceptional.apputils as utils

async def date_time(data):
    """
    Get time from bash command "date"
    """
    result = await utils.run_async("date", shell=True)
    return result.stdout.strip()

class ExampleWindow(WindowBase):
    def __init__(self) -> None:
        super().__init__()
        self.state = ShellWindow(dock_direction=Direction.Center, monitor_preference=MonitorPreference.Primary)
        self.attach_data(
            DataFetcher(
                key="date", function=date_time, delay_ms=1000
            )
        )

    def create_window(self):
        """
        UI implementation function. 
        All drawing logic is done in this abstract method which is run once per 
        frame.
        """
        with self.imgui_window("Simple Window"):
            imgui.text("Simple window with simple text")
            imgui.set_window_size(200,200)
            dt = self.data.get("date", None)
            if dt:
                imgui.text(f"The time is {dt}")
```


More detailed examples are provided in `examples/`