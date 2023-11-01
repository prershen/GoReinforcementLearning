import numpy as np
import copy

BOARD_SIZE = 5

class helper:

    def find_died_pieces(self, board, player):
        died_pieces = []
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if board[i][j] == player:
                    if not self.find_liberty(board, i, j):
                        died_pieces.append((i, j))
        return died_pieces
    
    def remove_pieces(self, board, positions):
        for piece in positions:
            board[piece[0]][piece[1]] = 0
        return board

    def remove_died_pieces(self, board, player):
        died_pieces = self.find_died_pieces(board, player)
        if not died_pieces:
            return board
        new_board = self.remove_pieces(board, died_pieces)
        return new_board # returning the board and not died pieces

    def find_neighbours(self, row, col):
        neighbouring = [(row + 1, col),(row - 1, col),(row, col + 1),(row, col - 1)]
        return ([point for point in neighbouring if 0 <= point[0] < BOARD_SIZE and 0 <= point[1] < BOARD_SIZE])

    def find_neighbours_of_player_type(self, board, row, col):
        allies = []
        for point in self.find_neighbours(row, col):
            if board[point[0]][point[1]] == board[row][col]:
                allies.append(point)
        return allies

    def find_cluster_of_player_type(self, board, row, col):
        queue = [(row, col)]
        cluster = []
        while queue:
            node = queue.pop(0) #trying dfs
            cluster.append(node)
            for neighbour in self.find_neighbours_of_player_type(board, node[0], node[1]):
                if neighbour not in queue and neighbour not in cluster:
                    queue.append(neighbour)
        return cluster

    def find_liberty(self, board, row, col):
        count = 0
        for point in self.find_cluster_of_player_type(board, row, col):
            for neighbour in self.find_neighbours(point[0], point[1]):
                if board[neighbour[0]][neighbour[1]] == 0:
                    count += 1
        return count

    def check_for_ko(self, prev_board, board):
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if board[i][j] != prev_board[i][j]:
                    return False
        return True

    def place_chess(self, board, prev_board, player, row, col):
        if board[row][col] != 0:
            return False
        board_copy = copy.deepcopy(board)
        board_copy[row][col] = player
        dead_pieces = self.find_died_pieces(board_copy, 3 - player)
        board_copy = self.remove_died_pieces(board_copy, 3 - player)
        if not (dead_pieces and self.check_for_ko(prev_board, board_copy)) and self.find_liberty(board_copy, row, col) >= 1:
            return True

    def make_move(self, board, move, player):
        board_copy = copy.deepcopy(board)
        board_copy[move[0]][move[1]] = player
        board_copy = self.remove_died_pieces(board_copy, 3-player)
        return board_copy

    def valid_place_check(self, prev_board, board, player):
        valid_moves = []
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self.place_chess(board, prev_board, player, i, j) == True:
                    valid_moves.append((i,j))
        return valid_moves