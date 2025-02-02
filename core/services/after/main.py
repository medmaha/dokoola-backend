from functools import partial


class _AfterResponseService:

    def __init__(self):
        self.callbacks = []
        self.call_count = 0

    def clear(self):
        self.callbacks = []
        self.call_count = 0

    def register(self, callback, *args, **kwargs):
        self.callbacks.append(partial(callback, *args, **kwargs))


    def execute_callbacks(self):
        import after_response

        @after_response.enable
        def run(callbacks):
            for callback in callbacks:
                callback()

        run(self.callbacks)


    def execute(self):
        if self.call_count > 0:
            return
        self.call_count += 1
        self.execute_callbacks()
        self.clear()


AfterResponseService = _AfterResponseService()