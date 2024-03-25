from copy import deepcopy


########
# STATES
########
class State:
    """store the state of stage/tab"""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.default = deepcopy(kwargs)

    def reset(self):
        self.__dict__.update(self.default)
