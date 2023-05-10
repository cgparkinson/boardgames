from typing import List

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

    def validate(self, board_game_state):
        return board_game_state.player_turn == self.player
    
    def perform(self, board_game_state):
        if not self.validate(board_game_state):
            raise Exception('invalid turn')
        for action in self.actions:
            action.perform(board_game_state=board_game_state, player=self.player)
        board_game_state.turns.append(self)
        board_game_state.next_player()
