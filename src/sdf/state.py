from sdf.util import Enum 

ExecutionState = Enum('Unknown', 'Running', 'Completed')

class State:
    def __init__(self):
        self.ejecution_state = ExecutionState.Unknown
    
#    def __getstate__(self):
#        dict = self.__dict__.copy()
#        dict['ejecution_state'] = self.ejecution_state
#        return dict
#
#    def __setstate__(self, dict):
#        dict['ejecution_state'] = ExecutionState[dict['ejecution_state']]
#        self.__dict__.update(dict)

        