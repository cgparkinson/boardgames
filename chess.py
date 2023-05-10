from typing import List
from boardgame import BoardGame, BoardGameState, Player
from board import Board, BoardGrid
from items import Item
from actions import Action, Turn
from string import ascii_lowercase

class ChessPiece(Item):
    def __init__(self, letter, player) -> None:
        super().__init__(letter, color=player.id, player=player)

    def validate_move(self, board, to_location):
        piece_in_to_location = board.get_item(to_location)
        if piece_in_to_location:
            if piece_in_to_location.color == self.player.id:
                # raise Exception(str(board) + '\n can\'t take your own piece, from ' + str(self.location) + ' to ' + str(to_location))
                return False
        return True
    
    def move(self, board, to_location, player):
        if not self.validate_move(board, to_location):
            raise Exception('invalid move from ' + str(self.location) + ' ' + str(to_location))
        piece_in_to_location = board.get_item(to_location)
        if piece_in_to_location:
            if piece_in_to_location.color == player.id:
                raise Exception(str(board) + '\n can\'t take your own piece, from ' + str(self.location) + ' to ' + str(to_location))
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
        if not super().validate_move(board, to_location):
            return False
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
        if not super().validate_move(board, to_location):
            return False
        from_location = self.location
        moving_diagonally = board.moving_diagonally_only(from_location, to_location)
        moving_horizontally = board.moving_horizontally_only(from_location, to_location)
        moving_vertically = board.moving_vertically_only(from_location, to_location)
        if not moving_horizontally and not moving_diagonally and not moving_vertically:
            return False
        items_on_path = board.items_on_path(from_location, to_location)
        valid = (moving_diagonally or moving_horizontally or moving_vertically) and not items_on_path
        return valid

class King(ChessPiece):
    def __init__(self, player) -> None:
        super().__init__(letter='K', player=player)

    def validate_move(self, board, to_location):
        if not super().validate_move(board, to_location):
            return False
        # TODO: castling
        from_location = self.location
        if board.spaces_moving_manhattan(from_location, to_location) > 2:
            return False
        spaces_moving = board.spaces_moving_linear(from_location, to_location)
        valid = spaces_moving == 1
        return valid

class Rook(ChessPiece):
    def __init__(self, player) -> None:
        super().__init__(letter='R', player=player)

    def validate_move(self, board, to_location):
        if not super().validate_move(board, to_location):
            return False
        from_location = self.location
        moving_horizontally = board.moving_horizontally_only(from_location, to_location)
        moving_vertically = board.moving_vertically_only(from_location, to_location)
        if not moving_horizontally and not moving_vertically:
            return False
        items_on_path = board.items_on_path(from_location, to_location)
        valid = (moving_horizontally or moving_vertically) and not items_on_path
        return valid

class Bishop(ChessPiece):
    def __init__(self, player) -> None:
        super().__init__(letter='B', player=player)

    def validate_move(self, board, to_location):
        if not super().validate_move(board, to_location):
            return False
        from_location = self.location
        moving_diagonally = board.moving_diagonally_only(from_location, to_location)
        if not moving_diagonally:
            return False
        items_on_path = board.items_on_path(from_location, to_location)
        valid = moving_diagonally and not items_on_path
        return valid

class Pawn(ChessPiece):
    def __init__(self, player) -> None:
        super().__init__(letter='P', player=player)

    def validate_move(self, board, to_location):
        if not super().validate_move(board, to_location):
            return False
        from_location = self.location
        moving_diagonally = board.moving_diagonally_only(from_location, to_location)
        moving_vertically = board.moving_vertically_only(from_location, to_location)
        if not moving_diagonally and not moving_vertically:
            return False
        items_on_path = board.items_on_path(from_location, to_location)
        spaces_moving = board.spaces_moving_linear(from_location, to_location)
        piece_in_to_location = board.get_item(to_location)
        enemy_piece_in_to_location = piece_in_to_location and piece_in_to_location.color != self.color
        not_moved_yet = self.color == 'black' and from_location[1] == 6 or self.color == 'white' and from_location[1] == 1

        taking_piece = moving_diagonally and enemy_piece_in_to_location and spaces_moving == 1
        normal_move = moving_vertically and spaces_moving == 1
        double_first_move = moving_vertically and spaces_moving == 2 and not_moved_yet
        en_passant = False  # TODO

        valid = (taking_piece or normal_move or double_first_move or en_passant) and not items_on_path
        return valid

class ChessBoard(BoardGrid):
    def __init__(self) -> None:
        super().__init__(x=8, y=8)

    # def in_check(self, owner):
    #     king = [item for item in self.items if item.player == owner and isinstance(item, King)][0]
    #     enemy_pieces = [item for item in self.items if item.player != owner]
    #     can_take = [item.validate_move(self, king.location) for item in enemy_pieces]
    #     check = any(can_take)
    #     return check


class ChessState(BoardGameState):
    def __init__(self, board: Board, players: List[Player]) -> None:
        super().__init__(board, players)
    
    def in_check(self, owner):
        king = [item for item in self.board.items if item.player == owner and isinstance(item, King)][0]
        enemy_pieces = [item for item in self.board.items if item.player != owner]
        can_take = [item.validate_move(self.board, king.location) for item in enemy_pieces]
        check = any(can_take)
        return check
    
    def win_condition_met(self):
        kings = [item for item in self.board.items if isinstance(item, King)]
        if self.hypothetical:
            # print('WE ARE IN THE MATRIX')
            return False
        for king in kings:
            owner = king.player

            check = self.in_check(owner)
            if check:
                # print('#######################\ncheck detected')
                # print(self)
                # if the person who has just moved is in check, this is an illegal state and we're in a hypothetical loop
                if owner != self.player_turn:
                    return False

                can_save = False
                own_pieces = [item for item in self.board.items if item.player == owner]
                # for each of your own pieces, try every move, and find if you can stop being in check
                for item in own_pieces:
                    for location in self.board.locations:
                        if item.validate_move(self.board, location):
                            # print('!!!!!!!!!!!!!!!!!!!!!!!!!\nbefore:', self)
                            new_state = self.after(Turn([Move(item.location, location)], player=item.player))
                            # print('?????????????????????????\nhypothetical:', new_state)
                            # print('_________________________\nafter:', self)
                            if not new_state.in_check(owner):
                                can_save = True
                            # import time
                            # time.sleep(1)
            
                if not can_save:
                    # print('checkmate')
                    return True
                # print('check but not mate')
        return False

class Chess(BoardGame):
    def __init__(self) -> None:
        board = ChessBoard()
        black = Player(name='Alice', id='black')
        white = Player(name='Bob', id='white')

        self.white = white
        self.black = black

        board.add_item(item=Rook(player=white), location=(0,0))
        board.add_item(item=Knight(player=white), location=(1,0))
        board.add_item(item=Bishop(player=white), location=(2,0))
        board.add_item(item=Queen(player=white), location=(3,0))
        board.add_item(item=King(player=white), location=(4,0))
        board.add_item(item=Bishop(player=white), location=(5,0))
        board.add_item(item=Knight(player=white), location=(6,0))
        board.add_item(item=Rook(player=white), location=(7,0))

        board.add_item(item=Rook(player=black), location=(0,7))
        board.add_item(item=Knight(player=black), location=(1,7))
        board.add_item(item=Bishop(player=black), location=(2,7))
        board.add_item(item=Queen(player=black), location=(3,7))
        board.add_item(item=King(player=black), location=(4,7))
        board.add_item(item=Bishop(player=black), location=(5,7))
        board.add_item(item=Knight(player=black), location=(6,7))
        board.add_item(item=Rook(player=black), location=(7,7))
        for i in range(8):
            board.add_item(item=Pawn(player=white), location=(i,1))
            board.add_item(item=Pawn(player=black), location=(i,6))
        state = ChessState(board=board, players=[white, black])
        super().__init__(state)
    
    def play_demo_game(self):
        [move.perform(board_game_state=self.state) for move in moves_from_notation(notation='e4 e5', state=self.state)]
        [move.perform(board_game_state=self.state) for move in moves_from_notation(notation='Nf3 f6', state=self.state)]
        [move.perform(board_game_state=self.state) for move in moves_from_notation(notation='Nxe5 e5', state=self.state)]
        [move.perform(board_game_state=self.state) for move in moves_from_notation(notation='Qh5+ Ke7', state=self.state)]
        [move.perform(board_game_state=self.state) for move in moves_from_notation(notation='Qxe5+ Kf7', state=self.state)]
        [move.perform(board_game_state=self.state) for move in moves_from_notation(notation='Bc4+ d5', state=self.state)]
        [move.perform(board_game_state=self.state) for move in moves_from_notation(notation='Bxd5+ Kg6', state=self.state)]
        [move.perform(board_game_state=self.state) for move in moves_from_notation(notation='h4 h5', state=self.state)]
        [move.perform(board_game_state=self.state) for move in moves_from_notation(notation='Bxb7 Bxb7', state=self.state)]
        [move.perform(board_game_state=self.state) for move in moves_from_notation(notation='Qf5+ Kh6', state=self.state)]
        [move.perform(board_game_state=self.state) for move in moves_from_notation(notation='d4+ g5', state=self.state)]
        [move.perform(board_game_state=self.state) for move in moves_from_notation(notation='Qf7 Qe7', state=self.state)]
        [move.perform(board_game_state=self.state) for move in moves_from_notation(notation='xg5+ Qxg5', state=self.state)]
        [move.perform(board_game_state=self.state) for move in moves_from_notation(notation='Rxh5 ', state=self.state)]

        # print(self.state)


def move(board_game_state, player, move_from, move_to):
    board = board_game_state.board
    piece = board.get_item(move_from)
    if not piece:
        raise Exception('nothing found at location ', move_from)
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

def moves_from_notation(state, notation='e3 e5'):
    # does not support full range of PGN or chess notation
    # this is just to make it easier for me to test
    def get_piece(letter) -> ChessPiece:
        d = {
            'K': King,
            'B': Bishop,
            'P': Pawn,
            'Q': Queen,
            'R': Rook,
            'N': Knight
        }
        return d[letter]
    
    def get_location(coord):
        assert len(coord) == 2
        letter = coord[0]
        number = coord[1]
        row = ascii_lowercase.index(letter)
        column = int(number) - 1
        return (row, column)
    
    board = state.board
    white = state.players[0]
    black = state.players[1]

    notation = notation.replace('x', '').replace('+', '')
    white_move = notation.split(' ')[0]
    black_move = notation.split(' ')[1]

    if len(white_move) == 2:
        white_piece = Pawn
    else:
        white_piece = get_piece(white_move[0])

    white_location = get_location(white_move[-2:])

    piece_to_move = [item for item in board.items if item.player.id=='white' and isinstance(item, white_piece) and item.validate_move(board, white_location)]
    assert len(piece_to_move) == 1
    current_white_location = piece_to_move[0].location

    white_turn = Turn([Move(current_white_location, white_location)], player=white)

    bgs = state.after(white_turn)
    board = bgs.board
    if len(black_move) == 0:
        return ([white_turn])
    
    if len(black_move) == 2:
        black_piece = Pawn
    else:
        black_piece = get_piece(black_move[0])
    black_location = get_location(black_move[-2:])
    piece_to_move = [item for item in board.items if item.player.id=='black' and isinstance(item, black_piece) and item.validate_move(board, black_location)]
    assert len(piece_to_move) == 1
    current_black_location = piece_to_move[0].location

    black_turn = Turn([Move(current_black_location, black_location)], player=black)
    return (white_turn, black_turn)


# def game_from_pgn(pgn):
#     """
#     [Event ""]
#     [Site ""]
#     [Date "????.??.??"]
#     [Round ""]
#     [White "White"]
#     [Black "Black"]
#     [TimeControl "-"]
#     [Result "1-0"]

#     1.e4 e5 2.Nf3 f6 3.Nxe5 fxe5 4.Qh5+ Ke7 5.Qxe5+ Kf7 6.Bc4+ d5 7.Bxd5+ 
#     Kg6 8.h4 h5 9.Bxb7 Bxb7 10.Qf5+ Kh6 11.d4+ g5 12.Qf7 Qe7 13.hxg5+ Qxg5 
#     14.Rxh5# 1-0
#     """
#     pass


if __name__ == '__main__':
    chess = Chess()
    chess.play_demo_game()
    print(chess.state)