import imgui
from uxceptional import WindowBase, Direction, MonitorPreference, ShellWindow, DataFetcher, Backend
import uxceptional.apputils as utils

class DataSources:
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
                key="date", function=DataSources.date_time, delay_ms=1000
            )
        )

    def create_window(self):
        """
        UI implementation function. 
        All drawing logic is done in this abstract method which is run once per 
        frame.
        """
        state = self.state
        with self.imgui_window("Simple Window"):
            imgui.text("Simple window with simple text")
            state.width_candidate()
            dt = self.data.get("date", None)
            if dt:
                imgui.text(f"The time is {dt}")
                state.width_candidate()
            state.height_candidate()
            state.apply_bounds()
            imgui.set_window_size(*state.size)

if __name__ == "__main__":
    bar = ExampleWindow()
    Backend.add_window(bar)
    try:
        Backend.run_backend()
    except KeyboardInterrupt:
        pass
