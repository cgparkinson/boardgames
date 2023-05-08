from boardgame import BoardGame, BoardGameState, BoardGrid, Item, Action, Player, Turn

class Knight(Item):
    def __init__(self, player) -> None:
        super().__init__(letter='N', player=player)

class Queen(Item):
    def __init__(self, player) -> None:
        super().__init__(letter='Q', player=player)

class King(Item):
    def __init__(self, player) -> None:
        super().__init__(letter='K', player=player)

class Rook(Item):
    def __init__(self, player) -> None:
        super().__init__(letter='R', player=player)

class Bishop(Item):
    def __init__(self, player) -> None:
        super().__init__(letter='B', player=player)

class Pawn(Item):
    def __init__(self, player) -> None:
        super().__init__(letter='P', player=player)

class ChessBoard(BoardGrid):
    def __init__(self) -> None:
        super().__init__(x=8, y=8)

    def win_condition_met(self):
        return False

class Chess(BoardGame):
    def __init__(self) -> None:
        board = ChessBoard()
        black = Player(name='black', id='black')
        white = Player(name='white', id='white')

        self.white = white
        self.black = black

        board.add_item(item=Rook(player=black), location=(0,0))
        board.add_item(item=Knight(player=black), location=(1,0))
        board.add_item(item=Bishop(player=black), location=(2,0))
        board.add_item(item=Queen(player=black), location=(3,0))
        board.add_item(item=King(player=black), location=(4,0))
        board.add_item(item=Bishop(player=black), location=(5,0))
        board.add_item(item=Knight(player=black), location=(6,0))
        board.add_item(item=Rook(player=black), location=(7,0))

        board.add_item(item=Rook(player=white), location=(0,7))
        board.add_item(item=Knight(player=white), location=(1,7))
        board.add_item(item=Bishop(player=white), location=(2,7))
        board.add_item(item=Queen(player=white), location=(3,7))
        board.add_item(item=King(player=white), location=(4,7))
        board.add_item(item=Bishop(player=white), location=(5,7))
        board.add_item(item=Knight(player=white), location=(6,7))
        board.add_item(item=Rook(player=white), location=(7,7))
        for i in range(8):
            board.add_item(item=Pawn(player=black), location=(i,1))
            board.add_item(item=Pawn(player=white), location=(i,6))
        state = BoardGameState(board=board, players=[white, black])
        super().__init__(state)
    
    def play_demo_game(self):
        Turn(actions=[Move((0,0), (0,2))], player=self.white).perform(board_game_state=self.state)
        print(self.state)

def move(board_game_state, player, move_from, move_to):
    board = board_game_state.board
    piece = board.get_item_with_location(*move_from)
    print(piece)
    piece.location = move_to

class Move(Action):
    def __init__(self, move_from, move_to) -> None:
        fn = move
        params = {'move_from': move_from, 'move_to': move_to}
        super().__init__(fn, params)

Chess().play_demo_game()