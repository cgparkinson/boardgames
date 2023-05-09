import unittest

from chess import Chess, ChessBoard, ChessPiece, King, Knight, Queen, Pawn, Turn, Move

class TestChess(unittest.TestCase):
    def setUp(self) -> None:
        self.chess = Chess()
        self.board = self.chess.state.board
    
    def test_pawn_move_2(self):
        Turn(actions=[Move((0,6), (0,4))], player=self.chess.white).perform(board_game_state=self.chess.state)
        assert isinstance(self.board.get_item(location=(0,4)), Pawn)
    
    def test_pawn_move_1(self):
        Turn(actions=[Move((0,6), (0,5))], player=self.chess.white).perform(board_game_state=self.chess.state)
        assert isinstance(self.board.get_item(location=(0,5)), Pawn)
    
    @unittest.expectedFailure
    def test_pawn_move_3(self):
        Turn(actions=[Move((0,6), (0,3))], player=self.chess.white).perform(board_game_state=self.chess.state)
        assert isinstance(self.board.get_item(location=(0,3)), Pawn)

if __name__ == '__main__':
    unittest.main()