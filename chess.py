from boardgame import BoardGame, BoardGameState, Player
from board import BoardGrid
from items import Item
from actions import Action, Turn

class ChessPiece(Item):
    def __init__(self, letter, player) -> None:
        super().__init__(letter, color=player.id, player=player)

    def validate_move(self, board, to_location):
        pass
    
    def move(self, board, to_location, player):
        if not self.validate_move(board, to_location):
            raise Exception('invalid move!')
        piece_in_to_location = board.get_item(to_location)
        if piece_in_to_location:
            if piece_in_to_location.color == player.id:
                raise Exception('can\'t take your own piece!')
            print('removing ', piece_in_to_location)
            board.remove_item(piece_in_to_location)
        moving_inbounds = board.moving_inbounds(to_location)
        if not moving_inbounds:
            raise Exception('out of bounds')
        self.location = to_location
        board.get_item(to_location)  # designed to fail if there is more than one item

class Knight(ChessPiece):
    def __init__(self, player) -> None:
        super().__init__(letter='N', player=player)

    def validate_move(self, board, to_location):
        from_location = self.location
        moving_horizontally = board.moving_horizontally_only(from_location, to_location)
        moving_vertically = board.moving_vertically_only(from_location, to_location)
        spaces_moving = board.spaces_moving_manhattan(from_location, to_location)
        valid = spaces_moving == 3 and not (moving_horizontally or moving_vertically)
        return valid

class Queen(ChessPiece):
    def __init__(self, player) -> None:
        super().__init__(letter='Q', player=player)

    def validate_move(self, board, to_location):
        from_location = self.location
        moving_diagonally = board.moving_diagonally_only(from_location, to_location)
        moving_horizontally = board.moving_horizontally_only(from_location, to_location)
        moving_vertically = board.moving_vertically_only(from_location, to_location)
        items_on_path = board.items_on_path(from_location, to_location)
        valid = (moving_diagonally or moving_horizontally or moving_vertically) and not items_on_path
        return valid

class King(ChessPiece):
    def __init__(self, player) -> None:
        super().__init__(letter='K', player=player)

    def validate_move(self, board, to_location):
        # TODO: castling
        from_location = self.location
        spaces_moving = board.spaces_moving_linear(from_location, to_location)
        valid = spaces_moving == 1
        return valid

class Rook(ChessPiece):
    def __init__(self, player) -> None:
        super().__init__(letter='R', player=player)

    def validate_move(self, board, to_location):
        from_location = self.location
        moving_horizontally = board.moving_horizontally_only(from_location, to_location)
        moving_vertically = board.moving_vertically_only(from_location, to_location)
        items_on_path = board.items_on_path(from_location, to_location)
        valid = (moving_horizontally or moving_vertically) and not items_on_path
        return valid

class Bishop(ChessPiece):
    def __init__(self, player) -> None:
        super().__init__(letter='B', player=player)

    def validate_move(self, board, to_location):
        from_location = self.location
        moving_diagonally = board.moving_diagonally_only(from_location, to_location)
        items_on_path = board.items_on_path(from_location, to_location)
        valid = moving_diagonally and not items_on_path
        return valid

class Pawn(ChessPiece):
    def __init__(self, player) -> None:
        super().__init__(letter='P', player=player)

    def validate_move(self, board, to_location):
        from_location = self.location
        moving_diagonally = board.moving_diagonally_only(from_location, to_location)
        moving_vertically = board.moving_vertically_only(from_location, to_location)
        items_on_path = board.items_on_path(from_location, to_location)
        spaces_moving = board.spaces_moving_linear(from_location, to_location)
        piece_in_to_location = board.get_item(to_location)
        enemy_piece_in_to_location = piece_in_to_location and piece_in_to_location.color != self.color
        not_moved_yet = self.color == 'black' and from_location[1] == 1 or self.color == 'white' and from_location[1] == 8-1-1

        taking_piece = moving_diagonally and enemy_piece_in_to_location and spaces_moving == 1
        normal_move = moving_vertically and spaces_moving == 1
        double_first_move = spaces_moving == 2 and not_moved_yet
        en_passant = False  # TODO

        valid = (taking_piece or normal_move or double_first_move or en_passant) and not items_on_path
        return valid

class ChessBoard(BoardGrid):
    def __init__(self) -> None:
        super().__init__(x=8, y=8)

    def win_condition_met(self):
        def in_check(owner):
            enemy_pieces = [item for item in self.items if item.player != owner]
            can_take = [item.validate_move(self.board, king.location) for item in enemy_pieces]
            check = any(can_take)
            return check
        kings = [item for item in self.items if isinstance(item, King)]

        for king in kings:
            owner = king.player

            check = in_check(owner)
            if check:
                own_pieces = [item for item in self.items if item.player == owner]
                can_save = True # TODO: this requires hypothetical board game states
            
            if not can_save:
                return True

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
        Turn(actions=[Move((3,0), (3,2))], player=self.black).perform(board_game_state=self.state)
        print(self.state)

def move(board_game_state, player, move_from, move_to):
    board = board_game_state.board
    piece = board.get_item(move_from)
    current_player = board_game_state.player_turn
    if current_player == piece.player:
        piece.move(board, move_to, current_player)
    else:
        raise Exception('don\'t move your opponent\'s piece!')

class Move(Action):
    def __init__(self, move_from, move_to) -> None:
        fn = move
        params = {'move_from': move_from, 'move_to': move_to}
        super().__init__(fn, params)
if __name__ == '__main__':
    Chess().play_demo_game()

def moves_from_notation(board, notation='Bxd5+ Kg6'):
    notation = notation.replace('x', '').replace('+', '')
    white_move = notation.split(' ')[0]
    black_move = notation.split(' ')[1]

    white_piece = Bishop
    white_location = (3,4)

    black_piece = King
    black_location = (6,5)

    # find a bishop that can move to (3,4)

def game_from_pgn(pgn):
    """
    [Event ""]
    [Site ""]
    [Date "????.??.??"]
    [Round ""]
    [White "White"]
    [Black "Black"]
    [TimeControl "-"]
    [Result "1-0"]

    1.e4 e5 2.Nf3 f6 3.Nxe5 fxe5 4.Qh5+ Ke7 5.Qxe5+ Kf7 6.Bc4+ d5 7.Bxd5+ 
    Kg6 8.h4 h5 9.Bxb7 Bxb7 10.Qf5+ Kh6 11.d4+ g5 12.Qf7 Qe7 13.hxg5+ Qxg5 
    14.Rxh5# 1-0
    """
    pass