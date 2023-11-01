from copy import deepcopy
import numpy as np

BOARD_SIZE = 5
ONGOING = -1
DRAW = 0
X_WIN = 1
O_WIN = 2


class Board:

    def __init__(self, state=None, show_board=False, show_results=False):
        if state is None:
            self.state = np.zeros((5,5), dtype=np.int)
        else:
            self.state = state.copy()

        self.game_result = ONGOING
        self.show_board = show_board
        self.show_results = show_results
        self.previous_board = deepcopy(self.state)
        self.died_pieces = []

    def set_show_board(self, show_board):
        self.show_board = show_board

    def encode_state(self):
        return ''.join([str(self.state[i][j]) for i in range(BOARD_SIZE) for j in range(BOARD_SIZE)])

    def reset(self):
        self.state.fill(0)
        self.game_result = ONGOING
        self.previous_board = deepcopy(self.state)

    def is_valid_move(self, row, col, piece_type):
        board = self.state

        if not 0 <= row < len(board):
            return False
        if not 0 <= col < len(board):
            return False

        if (row, col) in self.died_pieces:
            return False

        if board[row][col] != 0:
            return False

        test_go = self.copy_board()
        test_board = test_go.state

        test_board[row][col] = piece_type
        test_go.update_board(test_board)
        if test_go.find_liberty(row, col):
            return True

        test_go.remove_died_pieces(3 - piece_type)
        if not test_go.find_liberty(row, col):
            return False
        else:
            if self.died_pieces and self.compare_board(self.previous_board, test_go.state):
                return False
        return True

    # region Auxiliary Methods for is_valid_move
    def copy_board(self):
        return deepcopy(self)

    def update_board(self, board):
        self.state = board

    def find_liberty(self, row, col):
        board = self.state
        ally_members = self.ally_dfs(row, col)
        for member in ally_members:
            neighbors = self.detect_neighbor(member[0], member[1])
            for piece in neighbors:
                if board[piece[0]][piece[1]] == 0:
                    return True
        return False

    def ally_dfs(self, row, col):
        stack = [(row, col)]  # stack for DFS search
        ally_members = []  # record allies positions during the search
        while stack:
            piece = stack.pop()
            ally_members.append(piece)
            neighbor_allies = self.detect_neighbor_ally(piece[0], piece[1])
            for ally in neighbor_allies:
                if ally not in stack and ally not in ally_members:
                    stack.append(ally)
        return ally_members

    def detect_neighbor_ally(self, row, col):
        board = self.state
        neighbors = self.detect_neighbor(row, col)
        group_allies = []
        for piece in neighbors:
            if board[piece[0]][piece[1]] == board[row][col]:
                group_allies.append(piece)
        return group_allies

    def detect_neighbor(self, i, j):
        board = self.state
        neighbors = []
        if i > 0:
            neighbors.append((i - 1, j))
        if i < len(board) - 1:
            neighbors.append((i + 1, j))
        if j > 0:
            neighbors.append((i, j - 1))
        if j < len(board) - 1:
            neighbors.append((i, j + 1))
        return neighbors

    def compare_board(self, board1, board2):
        comparison = board1 == board2
        return comparison.all()

    def remove_died_pieces(self, piece_type):
        died_pieces = self.find_died_pieces(piece_type)
        if not died_pieces:
            return []
        self.remove_certain_pieces(died_pieces)
        return died_pieces

    def remove_certain_pieces(self, positions):
        board = self.state
        for piece in positions:
            board[piece[0]][piece[1]] = -1
        self.update_board(board)

    def find_died_pieces(self, piece_type):
        board = self.state
        died_pieces = []
        for i in range(len(board)):
            for j in range(len(board)):
                if board[i][j] == piece_type:
                    if not self.find_liberty(i, j):
                        died_pieces.append((i, j))
        return died_pieces

    # endregion

    # only plays the valid move and returns the board
    def move(self, row, col, player):
        board = self.state
        self.previous_board = deepcopy(board)
        board[row][col] = player
        self.update_board(board)
        # we are not incrementing the number of moves here so do it in the game file
        # self.n_moves +=1

        # we are also not returning the game result or state
        return True

    def score(self, piece_type):
        board = self.state
        count = 0
        for i in range(5):
            for j in range(5):
                if board[i][j] == piece_type:
                    count += 1
        return count

    def check_winner(self):
        cnt1 = self.score(1)
        cnt2 = self.score(2)
        # print("WInner calculation:", cnt1, cnt2)
        if cnt1 > cnt2 + 2.5:
            return 1
        elif cnt1 < cnt2 + 2.5:
            return 2
        else:
            return DRAW