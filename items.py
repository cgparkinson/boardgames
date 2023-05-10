from typing import List, Tuple
from enum import Enum
import random
import numpy as np

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
        self.image = None
        super().__init__()
    
    def initialise_rendering(self):
        import pygame
        self.image = pygame.image.load('images/' + self.suit.name + '-' + str(self.value) + '.svg')

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
