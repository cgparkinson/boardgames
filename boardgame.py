from typing import List, Tuple
from abc import ABC
from enum import Enum
import random
from board import Board
from copy import deepcopy, copy
from actions import Turn


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
        return self.name + ' playing as ' + self.id
    
    def __eq__(self, player):
        # compare by ID to allow deep copy in hypothetical game states
        return player.id == self.id
    
    def __ne__(self, player):
        # compare by ID to allow deep copy in hypothetical game states
        return player.id != self.id
    
    def win_condition_met(self):
        return False
    
    def set_player_to_left(self, player):
        self.player_to_left = player
    
    def set_player_to_right(self, player):
        self.player_to_right = player


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
        self.turn_phase = TurnPhase.PASS_THE_LAPTOP  # which part of this person's go is it?  # TODO implement
        self.game_phase = GamePhase.SETUP  # which section of the game is it?  # TODO implement
        self.turns = []
        self.hypothetical = False
    
    def __repr__(self) -> str:
        return str(self.hypothetical) + '\nboard:' + str(self.board) + '\n players:' + str(self.players) + '\nturn:' + str(self.player_turn) + '\nturn phase:' + str(self.turn_phase) + '\ngame phase:' + str(self.game_phase) + '\nlast turn was:' + str(self.turns[-1])
    
    @staticmethod
    def win_condition_met():
        return False

    def done(self):
        done = self.win_condition_met() or self.board.win_condition_met() or any([p.win_condition_met() for p in self.players])
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
        self.turn_phase = TurnPhase.PASS_THE_LAPTOP
    
    def after(self, turn: Turn):
        hypothetical_state = deepcopy(self)
        hypothetical_state.hypothetical = True
        turn.perform(hypothetical_state)
        return hypothetical_state

class BoardGame():
    def __init__(self, state: BoardGameState) -> None:
        self.state = state

    def play(self):
        print(self.state)