from datetime import datetime
from time import sleep
from typing import Any, Type
from uxceptional.shellwindow import ShellWindow
from abc import abstractmethod
from threading import Lock, Thread
from contextlib import contextmanager
import asyncio
import imgui

class DataThreadFailedException(Exception):
    pass

class DataFetcher:
    def __init__(self, key, function : Type[lambda _: Any], delay_ms: int) -> None:
        """
        Create a datafetcher instance with a function e.g.
        async def fn(data):
            return {"calculated_data": 0}

        where fn is called:
            data[fetcher.key] = fn(data)

        called every $delay_ms milliseconds
        """
        self.key = key
        self.function = function
        self.delay = delay_ms

class WindowBase:
    """
    Basis for every shell window implementation
    """
    def __init__(self, state: ShellWindow) -> None:
        self.state = state
        self.thread_lock = Lock()
        
        # The window data store
        self.data = {
            "timestamps": {},
            "refresh_period": 0.1 # Frequency of data update cycle. 
        }
        self.fetchers = []
        self.window_flags = imgui.WINDOW_NO_SAVED_SETTINGS | imgui.WINDOW_NO_MOVE
        self.window_flags |= imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_TITLE_BAR
        self.window_flags |= imgui.WINDOW_NO_SCROLLBAR

        self.initialized = False
        self.data_thread = Thread(target=self._data_thread, daemon=True)
        self.raise_if_no_data_thread = False

    async def _init(self):
        """
        Fetch initial data and start data thread
        """
        for datasource in self.fetchers:
            self.data[datasource.key] = await datasource.function(self.data)

        self.data_thread.start()
        self.init_hook()

    @abstractmethod
    def init_hook(self):
        """
        Any initialization work can be done by the user implementing this function
        """
        pass

    def attach_data(self, datafetcher: DataFetcher):
        """
        Attach a datafetcher to run during update_data
        """
        self.fetchers.append(datafetcher)

    @contextmanager
    def imgui_window(self, title, flags=None):
        """
        wrapper for imgui.begin which also sets some sane defaults.
        if flags is unset self.window_flags will be used
        """
        imgui.set_next_window_position(0, 0)
        window = imgui.begin(title, flags = self.window_flags if flags is None else flags)
        try:
            yield window
        finally:
            imgui.end()

    def _data_thread(self):
        """
        Runner function for data thread
        uses asyncio for single thread concurrency where possible
        """
        while True:
            asyncio.run(self.update_data(self.data))
            sleep(self.data['refresh_period'])

    def run_create_window(self):
        if not self.initialized:
            asyncio.run(self._init())
            self.initialized = True
        if self.raise_if_no_data_thread: # default
            if not self.data_thread.is_alive():
                raise DataThreadFailedException("Data thread unexpectedly vanished")

        self.create_window()

    @abstractmethod
    def create_window(self):
        """
        UI implementation function. 
        All drawing logic is done in this abstract method which is run once per 
        frame.
        """
        pass


    async def update_data(self, data):
        """
        Async data update coroutine
        Building with async means multiple actions can execute at once
        but the function won't return until all of them are complete.
        """
        with self.thread_lock:
            timestamps = self.data["timestamps"]
            for fet in self.fetchers:
                fet = fet # type: DataFetcher
                due = False
                now = datetime.utcnow()
                if fet.key not in timestamps:
                    due = True
                elif (now - timestamps[fet.key]).total_seconds() > (fet.delay / 1000.0):
                    due = True

                if due:
                    timestamps[fet.key] = datetime.utcnow()
                    data[fet.key] = await fet.function(data)


