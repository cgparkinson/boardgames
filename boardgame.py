import numpy as np
from typing import List, Tuple, NamedTuple
from abc import ABC

class Item():
    # all cards, pieces, etc inherit from this
    def __init__(self, letter='?', size=(1,1), player=None, location=None) -> None:
        self.size = size
        self.letter = letter
        self.player=player
        self.location=None

class Board():
    def __init__(self) -> None:
        pass

    def add_item(self):
        pass

    def get_items(self):
        pass

class BoardGrid(Board):
    # for chess, Go, tic-tac-toe, Food Chain Magnate...
    # has items on it (e.g. Piece), which cover one or more squares
    # may be divided into one or more areas
    # needs to detect what is on top
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y
        self.items = []
    
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
    
    def get_item(self, x,y):
        # assumes exactly one item at this location
        item = self.get_item_with_location(x,y)
        if item:
            return item
        else:
            return None
    
    def get_item_with_location(self, x,y):
        # assumes exactly one item at this location
        items = self.get_items(location=(x,y))
        if len(items) > 1:
            raise Exception('more than one item found')
        if len(items) == 0:
            return None
        return items[0]
    
    def __repr__(self) -> str:
        s = ''
        for y in range(self.y):
            for x in range(self.x): 
                item = self.get_item(x,y)
                if item:
                    letter = item.letter
                else:
                    letter = ' '
                s = s + letter
            s = s + '\n'
        return s

class BoardNetwork(Board):
    # for Power Grid, Ticket to Ride, ...
    # edges have weights
    # nodes have items on them
    def __init__(self) -> None:
        self.network = None
        self.items = []

class Action():
    def __init__(self, fn, params) -> None:
        self.fn = fn
        self.params = params

    def perform(self, board_game_state, player):
        self.fn(board_game_state, player=player, **self.params)

class Turn():
    # contains one or more actions
    # decide all your actions, validate them, then commit it as a Turn
    # in some games, a turn is one action - in some, it's a lot more
    # some games have multiple phases per turn
    def __init__(self, actions: List[Action], player) -> None:
        self.actions = actions
        self.player = player

    def validate(self):
        return True
    
    def perform(self, board_game_state):
        if not self.validate():
            raise Exception('invalid turn')
        for action in self.actions:
            action.perform(board_game_state=board_game_state, player=self.player)

class Player():
    # has Inventory (of cards/resources in hand)
    # may have a board, e.g. Agricola / Wingspan
    # 
    def __init__(self, name: str, id: str, inventory: List = []) -> None:
        self.name = name
        self.id = id
        self.inventory = inventory
        self.player_to_right = None
        self.player_to_left = None

    def __repr__(self) -> str:
        return self.name + ' ' + self.id
    
    def win_condition_met(self):
        return False
    
    def set_player_to_left(self, player):
        self.player_to_left = player
    
    def set_player_to_right(self, player):
        self.player_to_right = player

class Card(Item):
    # has obtain cost, play cost, expressed as e.g. obtain_cost = [(3, Gold), (2, Sheep)] where Gold is a class
    # e.g. for Wingspan, can express as [(3, Food)] where Fish is a class inheriting from Food
    def __init__(self) -> None:
        super.__init__(self)
        pass

class Die(Item):
    # can be rolled, not necessarily numbers on it (Wingspan)
    # can be owned (Perudo)
    def __init__(self) -> None:
        super.__init__(self)
        self.roll()
        pass

    def roll(self):
        self.value = np.random.randint(0,6)
        return self.value

class BoardGameState():
    # can be updated
    # usually consists of board, with its state, players, their state
    def __init__(self, board: Board, players: List[Player]) -> None:
        self.board = board
        self.players = players
        self.initialise_players
    
    def __repr__(self) -> str:
        return str(self.board) + str(self.players)
    
    def done(self):
        return self.board.win_condition_met() or any([p.win_condition_met() for p in self.players])
    
    def initialise_players(self):
        for i in range(len(self.players) - 1):
            self.players[i].player_to_left = self.players[i+1]
            i = i + 1
            self.players[i].player_to_right = self.players[i-1]
        self.players[-1].player_to_left = self.players[0]
        self.players[0].player_to_right = self.players[-1]

class BoardGame():
    def __init__(self, state: BoardGameState) -> None:
        self.state = state

    def play(self):
        print(self.state)