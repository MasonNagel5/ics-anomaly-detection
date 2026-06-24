class MyClass:
    """Starter class example."""

    def __init__(self, value=None):
        self.value = value

    def __repr__(self):
        return f"{self.__class__.__name__}(value={self.value!r})"

    def get_value(self):
        return self.value

    def set_value(self, value):
        self.value = value
