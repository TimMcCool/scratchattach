from __future__ import annotations

class MultiEventHandler:

    def __init__(self, *handlers):
        self.handlers = handlers

    def request(self, function, *args, **kwargs):
        for handler in self.handlers:
            handler.request(function, *args, **kwargs)

    def event(self, function, *args, **kwargs):
        for handler in self.handlers:
            handler.request(function, *args, **kwargs)

    def start(self, *args, **kwargs):
        for handler in self.handlers:
            handler.start(*args, **kwargs)

    def stop(self, *args, **kwargs):
        for handler in self.handlers:
            handler.stop(*args, **kwargs)

    def pause(self, *args, **kwargs):
        for handler in self.handlers:
            handler.pause(*args, **kwargs)

    def resume(self, *args, **kwargs):
        for handler in self.handlers:
            handler.resume(*args, **kwargs)