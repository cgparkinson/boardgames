from typing import List, Tuple
from abc import ABC
import numpy as np
import pygame
from enum import Enum
import random

COLORS = {
    'black':"\033[0;30m",
    'red': "\033[0;31m",
    'green': "\033[0;32m",
    'brown': "\033[0;33m",
    'blue': "\033[0;34m",
    'purple': "\033[0;35m",
    'cyan': "\033[0;36m",
    'light_gray': "\033[0;37m",
    'dark_gray': "\033[1;30m",
    'light_red': "\033[1;31m",
    'light_green': "\033[1;32m",
    'yellow': "\033[1;33m",
    'light_blue': "\033[1;34m",
    'light_purple': "\033[1;35m",
    'light_cyan': "\033[1;36m",
    'light_white': "\033[1;37m",
    'end': "\033[0m",
    ###
    'white': "\033[1;37m",
}

class Item():
    # all cards, pieces, etc inherit from this
    def __init__(self, letter='?', color='white', size=(1,1), player=None, location=None) -> None:
        self.size = size
        self.letter = letter
        self.player=player
        self.location=None
        self.color=color
    
    def __repr__(self) -> str:
        return COLORS[self.color] + self.letter + COLORS['end']

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
        s = ''
        for y in range(self.y):
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
    def __init__(self, name: str, id: str, public_inventory: List = [], private_inventory: List = []) -> None:
        self.name = name
        self.id = id
        self.public_inventory = public_inventory
        self.private_inventory = private_inventory
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

class ItemWithCost(Item):
    # has obtain cost, play cost, expressed as e.g. obtain_cost = [(3, Gold), (2, Sheep)] where Gold is a class
    # e.g. for Wingspan, can express as [(3, Food)] where Fish is a class inheriting from Food
    def __init__(self, obtain_cost: List[Item], play_cost: List[Item]) -> None:
        super.__init__(self)
        self.obtain_cost = obtain_cost
        self.play_cost = play_cost

class TextCard(Item):
    # item with additional text
    def __init__(self, text) -> None:
        self.text = text
        super().__init__()

class Suits(Enum):
    CLUB = 0
    SPADE = 1
    HEART = 2
    DIAMOND = 3

class StandardCard(Item):
    # TODO card in a standard 52 card deck
    def __init__(self, suit, value) -> None:
        self.suit = suit
        self.value = value
        self.image = pygame.image.load('images/' + self.suit.name + '-' + str(self.value) + '.svg')
        super().__init__()

class Stack():
    def __init__(self) -> None:
        self.items = []
    
    def add(self, item):
        self.items.append(item)

    def peek(self):
        if (len(self.items) > 0):
            return self.items[-1]
        else:
            return None
    
    def clear(self):
        self.items = []


class FaceUpDeck():
    # TODO deck where you can see the top card?
    def __init__(self) -> None:
        pass


class StandardDeck(Stack):
    # stack of 52 StandardCards
    def __init__(self):
        super.__init__()
        for suit in Suits:
            for value in range(1,14):
                self.items.append(StandardCard(suit, value))

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        return self.cards.pop()

    def length(self):
        return len(self.cards)


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

class TurnPhase(Enum):
    PASS_THE_LAPTOP = 'pass the laptop'
    MAIN_PHASE = 'main turn phase'

class GamePhase(Enum):
    SETUP = 'setup phase'
    MAIN_PHASE = 'main game phase'
    COMPLETE = 'game over'

class BoardGameState():
    # can be updated
    # usually consists of board, with its state, players, their state
    # TODO: not all games have one board, but all games have public elements (eg boards, decks), 
    # public player-owned elements (played cards, resources), and private player-owned elements (hand)
    # This class can be subclassed to accomodate this?
    def __init__(self, board: Board, players: List[Player]) -> None:
        self.board = board
        self.players = players
        self.initialise_players()
        self.player_turn = self.players[0]  # whose go is it?
        self.turn_phase = TurnPhase.PASS_THE_LAPTOP  # which part of this person's go is it?
        self.game_phase = GamePhase.SETUP  # which section of the game is it?
    
    def __repr__(self) -> str:
        return str(self.board) + str(self.players) + str(self.player_turn) + str(self.turn_phase) + str(self.game_phase)
    
    def done(self):
        done = self.board.win_condition_met() or any([p.win_condition_met() for p in self.players])
        if done:
            self.game_phase = GamePhase.COMPLETE
        return done
    
    def initialise_players(self):
        for i in range(len(self.players) - 1):
            self.players[i].player_to_left = self.players[i+1]
            i = i + 1
            self.players[i].player_to_right = self.players[i-1]
        self.players[-1].player_to_left = self.players[0]
        self.players[0].player_to_right = self.players[-1]
    
    def next_player(self):
        self.player_turn = self.player_turn.player_to_left

class BoardGame():
    def __init__(self, state: BoardGameState) -> None:
        self.state = state

    def play(self):
        print(self.state)