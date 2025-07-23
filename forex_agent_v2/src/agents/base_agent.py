class Agent:
    def __init__(self, name):
        self.name = name

    def execute(self, data):
        raise NotImplementedError("This method should be overridden by subclasses.")
