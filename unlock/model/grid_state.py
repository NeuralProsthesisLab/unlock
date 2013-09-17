from .model import UnlockModel


class GridStateChange(object):
    XChange = 0
    YChange = 1

    def __init__(self, change, step_value=None):
        super(GridStateChange, self).__init__()
        self.change = change
        self.step_value = step_value
        
        
class GridState(UnlockModel):
    IncrementYCursor = 1
    DecrementYCursor = 2
    DecrementXCursor = 3
    IncrementXCursor = 4

    def __init__(self, controllers):
        super(GridState, self).__init__()
        assert len(controllers) > 0
        
        self.ordering = [(0, 1), (1, 0), (0, -1), (-1, 0),
                         (1, 1), (1, -1), (-1, -1), (-1, 1)]
        self.state = (0, 0)
        self.state_change = None
        self.controllers = {}
        
        for slot in self.ordering:
            self.controllers[slot] = 'deadbeef'
        
        index = 0
        for controller in controllers:
            x_offset, y_offset = self.ordering[index]
            self.controllers[(x_offset, y_offset)] = controller
            index += 1
          
    def process_command(self, command):
        if command.decision is not None:
            self.process_decision(command.decision)
            
        if command.selection:
            if self.state in self.controllers:
                controller = self.controllers[self.state]
                controller.activate()
                
    def process_decision(self, decision):
        current_x, current_y = self.state

        if decision == GridState.IncrementYCursor:
            new_state = (current_x, current_y+1)
            change = GridStateChange.YChange, 1
            
        elif decision == GridState.DecrementYCursor:
            new_state = (current_x, current_y-1)
            change = GridStateChange.YChange, -1
            
        elif decision == GridState.DecrementXCursor:
            new_state = (current_x-1, current_y)            
            change = GridStateChange.XChange, -1
            
        elif decision == GridState.IncrementXCursor:
            new_state = (current_x+1, current_y)
            change = GridStateChange.XChange, 1

        if new_state in self.controllers:
            self.state = new_state
            self.state_change = GridStateChange(*change)
                    
    def get_state(self):
        ret = self.state_change
        self.state_change = None
        return ret


class HierarchyGridState(UnlockModel):
    """
    The Hierarchy Grid is a 2D grid interface for selecting targets arranged
     in a hierarchical fashion. The grid contains 2 or more layers, where
     certain tiles in the grid correspond to descend/ascend actions and the
     rest are target actions. The grid is laid our radially, with (0, 0)
     corresponding to the center.

    1) Create a square grid of tiles
    2) Each tile's state is its label and action
    3) On layer change, set tile states accordingly
    """
    IncrementYCursor = 1
    DecrementYCursor = 2
    DecrementXCursor = 3
    IncrementXCursor = 4

    def __init__(self, radius):
        super(HierarchyGridState, self).__init__()

        self.radius = radius
        self.state = (0, 0)
        self.state_change = None

    def process_command(self, command):
        if command.decision is not None:
            self.process_decision(command.decision)

        if command.selection:
            self.process_selection()

    def process_decision(self, decision):
        current_x, current_y = self.state
        new_state = None
        change = None

        if decision == GridState.IncrementYCursor:
            new_state = (current_x, current_y+1)
            change = (GridStateChange.YChange, 1)

        elif decision == GridState.DecrementYCursor:
            new_state = (current_x, current_y-1)
            change = (GridStateChange.YChange, -1)

        elif decision == GridState.DecrementXCursor:
            new_state = (current_x-1, current_y)
            change = (GridStateChange.XChange, -1)

        elif decision == GridState.IncrementXCursor:
            new_state = (current_x+1, current_y)
            change = (GridStateChange.XChange, 1)

        if new_state is not None and \
           abs(new_state[0]) <= self.radius and \
           abs(new_state[1]) <= self.radius:
            self.state = new_state
            self.state_change = GridStateChange(*change)

    def process_selection(self):
        """
        Determine and execute current tile's associated action
        """
        pass

    def get_state(self):
        ret = self.state_change
        self.state_change = None
        return ret


class GridTileState(UnlockModel):
    def __init__(self, label=None, icon=None, action=None):
        super(GridTileState, self).__init__()
        self.label = label
        self.icon = icon
        self.action = action
        self.state_change = None

    def get_state(self):
        ret = self.state_change
        self.state_change = None
        return ret