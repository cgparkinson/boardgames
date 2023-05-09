from boardgame import BoardGame, BoardGameState, BoardGrid, Item, Action, Player, Turn

class TicTacToeBoard(BoardGrid):
    def __init__(self) -> None:
        super().__init__(x=3, y=3)

    def win_condition_met(self):
        for i in range(3):
            if all([isinstance(self.get_item((i,j)), X) for j in range(3)]) or \
                all([isinstance(self.get_item((j,i)), X) for j in range(3)]) or \
                    all([isinstance(self.get_item((j,j)), X) for j in range(3)]) or \
                        all([isinstance(self.get_item((j,2-j)), X) for j in range(3)]):
                   return X
            elif all([isinstance(self.get_item((i,j)), O) for j in range(3)]) or \
                all([isinstance(self.get_item((j,i)), O) for j in range(3)]) or \
                    all([isinstance(self.get_item((j,j)), O) for j in range(3)]) or \
                        all([isinstance(self.get_item((j,2-j)), O) for j in range(3)]):
                   return O
        return None

class O(Item):
    def __init__(self) -> None:
        super().__init__(letter='O')

class X(Item):
    def __init__(self) -> None:
        super().__init__(letter='X')

def place_o(board_game_state, player, location):
    board = board_game_state.board
    if board.get_items(location):
        raise Exception('can\'t place O')
    elif player.id != 'O':
        raise Exception('player not O')
    else:
        board.add_item(O(), location)

class Place_O(Action):
    def __init__(self, location) -> None:
        params = {'location': location}
        fn = place_o
        super().__init__(fn, params)

def place_x(board_game_state, player, location):
    board = board_game_state.board
    if board.get_items(location):
        raise Exception('can\'t place X')
    elif player.id != 'X':
        raise Exception('player not X')
    else:
        board.add_item(X(), location)

class Place_X(Action):
    def __init__(self, location) -> None:
        params = {'location': location}
        fn = place_x
        super().__init__(fn, params)

class TicTacToe(BoardGame):
    def __init__(self) -> None:
        tictactoe_grid = TicTacToeBoard()
        self.adam = Player(name='X', id='X')
        self.jess = Player(name='O', id='O')
        bgs = BoardGameState(board=tictactoe_grid, players=[self.adam, self.jess])
        super().__init__(state=bgs)

    def play_demo_game(self):
        Turn(actions=[Place_X((0,2))], player=self.adam).perform(board_game_state=self.state)
        print(self.state)
        Turn(actions=[Place_O((1,1))], player=self.jess).perform(board_game_state=self.state)
        print(self.state)
        Turn(actions=[Place_X((0,1))], player=self.adam).perform(board_game_state=self.state)
        print(self.state)
        Turn(actions=[Place_O((2,2))], player=self.jess).perform(board_game_state=self.state)
        print(self.state)
        Turn(actions=[Place_X((1,2))], player=self.adam).perform(board_game_state=self.state)
        print(self.state)
        Turn(actions=[Place_O((0,0))], player=self.jess).perform(board_game_state=self.state)
        print(self.state)

        if self.state.done():
            winner = self.state.done()
            print('winner', winner)
        else:
            raise Exception('ERROR')

    def play(self):
        print('player 1 name:')
        self.adam.name = input()
        print('player 2 name:')
        self.jess.name = input()
        done = False
        while done==False:
            print(self.adam.name, 'turn. column?')
            x = int(input())
            print('row?')
            y = int(input())
            Turn(actions=[Place_X((x,y))], player=self.adam).perform(board_game_state=self.state)
            print(self.state)
            if self.state.done():
                winner = self.state.done()
                break

            print(self.jess.name, 'turn. column?')
            x = int(input())
            print('row?')
            y = int(input())
            Turn(actions=[Place_O((x,y))], player=self.jess).perform(board_game_state=self.state)
            print(self.state)

            if self.state.done():
                winner = self.state.done()
                break
        print('winner', winner)

TicTacToe().play_demo_game()
TicTacToe().play()