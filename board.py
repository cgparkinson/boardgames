from typing import List, Tuple
from items import Item

class Board():
    def __init__(self) -> None:
        pass

    def add_item(self):
        pass

    def get_items(self):
        pass

    def win_condition_met(self):
        return False

class BoardGrid(Board):
    # for chess, Go, tic-tac-toe, Food Chain Magnate...
    # has items on it (e.g. Piece), which cover one or more squares
    # may be divided into one or more areas
    # needs to detect what is on top
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y
        self.items = []
        self.locations = [(a, b) for a in range(x) for b in range(y)]
    
    def add_item(self, item: Item, location):
        top_left_x, top_left_y = location
        item.location = location
        if top_left_x + item.size[0] <= self.x and top_left_y + item.size[1] <= self.y:
            self.items.append(item)
        else:
            raise Exception('Cannot play this piece here.')
        
    def get_items(self, location: Tuple, size=(1,1)):
        top_left_x, top_left_y = location
        def overlap(box1_size, box1_location, box2_size, box2_location):
            def overlap_1d(x1_start, x1_size, x2_start, x2_size):
                if len(list(range(x1_start, x1_start + x1_size)) + list(range(x2_start,x2_start+ x2_size))) > len(set(list(range(x1_start, x1_start + x1_size)) + list(range(x2_start,x2_start+ x2_size)))):
                    return True
                else:
                    return False
            if overlap_1d(box1_location[0], box1_size[0], box2_location[0], box2_size[0]) and overlap_1d(box1_location[1], box1_size[1], box2_location[1], box2_size[1]):
                return True
            else:
                return False

        return [item for item in self.items if overlap(
            box1_size=size, box1_location=(top_left_x, top_left_y),
            box2_location=item.location, box2_size=item.size
        )]
    
    def get_item(self, location):
        x,y = location
        # assumes exactly one item at this location
        items = self.get_items(location=(x,y))
        if len(items) > 1:
            raise Exception('more than one item found in ' + str(location) + ': ' + str(items))
        if len(items) == 0:
            return None
        return items[0]
    
    def remove_item(self, item):
        self.items.remove(item)

    def remove_items_from_location(self, location):
        items = self.get_items(location)
        for item in items:
            self.remove_item(item)

    def __repr__(self) -> str:
        s = '\n'
        for y in range(self.y):
            y = self.y - y - 1
            for x in range(self.x): 
                item = self.get_item((x,y))
                if item:
                    letter = item.__repr__()
                else:
                    letter = ' '
                s = s + letter
            s = s + '\n'
        return s

    @staticmethod
    def spaces_moving_manhattan(from_location, to_location):
        return abs(from_location[0] - to_location[0]) + abs(from_location[1] - to_location[1])
    
    def spaces_moving_linear(self, from_location, to_location):
        assert self.moving_horizontally_only(from_location, to_location) or self.moving_vertically_only(from_location, to_location) or self.moving_diagonally_only(from_location, to_location)
        manhattan_distance = self.spaces_moving_manhattan(from_location, to_location)
        if self.moving_diagonally_only(from_location, to_location):
            return manhattan_distance / 2
        else:
            return manhattan_distance

    @staticmethod
    def moving_horizontally_only(from_location, to_location):
        return from_location[0] != to_location[0] and from_location[1] == to_location[1]

    @staticmethod
    def moving_vertically_only(from_location, to_location):
        return from_location[1] != to_location[1] and from_location[0] == to_location[0]

    @staticmethod
    def moving_diagonally_only(from_location, to_location):
        return abs(from_location[1] - to_location[1]) == abs(from_location[0] - to_location[0])

    def moving_inbounds(self, to_location):
        return to_location[0] >= 0 and to_location[1] >= 0 and to_location[0] < self.x and to_location[1] < self.y

    def items_on_path(self, from_location, to_location):
        # does not look at the end of the path.
        diag = self.moving_diagonally_only(from_location, to_location)
        horiz = self.moving_horizontally_only(from_location, to_location)
        vert = self.moving_vertically_only(from_location, to_location)
        if not (diag or horiz or vert):
            raise Exception('not a straight line path')
        items = []
        if diag or vert:
            spaces_moving = abs(from_location[1] - to_location[1])
        if horiz:
            spaces_moving = abs(from_location[0] - to_location[0])
        
        for i in range(spaces_moving-1):
            distance = i + 1
            x_sign = int((to_location[0] - from_location[0]) / spaces_moving)
            y_sign = int((to_location[1] - from_location[1]) / spaces_moving)
            x_move = x_sign * distance
            y_move = y_sign * distance
            items.extend(self.get_items((from_location[0] + x_move, from_location[1] + y_move)))
        return items

class BoardNetwork(Board):
    # for Power Grid, Ticket to Ride, ...
    # edges have weights
    # nodes have items on them
    def __init__(self) -> None:
        self.network = None
        self.items = []
