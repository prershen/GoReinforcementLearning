from copy import deepcopy

import numpy as np

from GoBoard import Board
from GoRandom import RandomPlayer
from GoAgent import QLearner

EXP_RATE = 0.3


class Go:

    def __init__(self):
        self.n_moves = 0
        self.max_moves = 24
        self.X_move = True

    def game_end(self, board, action="MOVE"):
        if self.n_moves >= self.max_moves:
            return True
        if board.compare_board(board.previous_board, board.state) and action == "PASS":
            return True
        return False

    def play2(self, board, player1, player2, learn):
        action = "MOVE"
        while not self.game_end(board, action):
            piece_type = 1 if self.X_move else 2

            if piece_type == 1:
                action = player1.move(board)
            else:
                action = player2.move(board)

            if action != "PASS":
                board.died_pieces = board.remove_died_pieces(3 - piece_type)
            else:
                board.previous_board = deepcopy(board.state)
            self.n_moves += 1
            self.X_move = not self.X_move

        reward = board.check_winner()
        print(reward)
        if learn:
            player1.learn(board)
            player2.learn(board)

        return reward

    def play(self, board, player1, player2, learn):
        action = "MOVE"
        while True:
            piece_type = 1 if self.X_move else 2

            if self.game_end(board):
                result = board.check_winner()
                # print(f"Winner is player:{result}")
                # learn the new stuff
                if learn:
                    player1.learn(board)
                    player2.learn(board)
                return result

            # after every move we need to do maintenance
            if piece_type == 1:
                # if self.n_moves == 0:
                #     action = "PASS"
                if np.random.uniform(0,1) <= EXP_RATE:
                    new_random = RandomPlayer()
                    new_random.set_side(1)
                    action = new_random.move(board)
                else:
                    action = player1.move(board)
            else:
                action = player2.move(board)

            if action != "PASS":
                board.died_pieces = board.remove_died_pieces(3 - piece_type)

            else:
                board.previous_board = deepcopy(board.state)

            self.n_moves += 1
            self.X_move = not self.X_move

    def battle(self, player1, player2, games, learn=False, show_result=True):
        player1.set_side(1)
        player2.set_side(2)
        p1_stats = [0, 0, 0]
        for i in range(games):
            if i % 100 == 0:
                print("Rounds {}".format(i))
            board = Board()
            result = self.play(board, player1, player2, learn)
            p1_stats[result] += 1
            self.n_moves = 0

        p1_stats = [round(x / games * 100.0, 1) for x in p1_stats]
        if show_result:
            print('_' * 60)
            print(
                '{:>15}(X) | Wins:{}% Draws:{}% Losses:{}%'.format(player1.__class__.__name__, p1_stats[1], p1_stats[0],
                                                                   p1_stats[2]).center(50))
            print(
                '{:>15}(O) | Wins:{}% Draws:{}% Losses:{}%'.format(player2.__class__.__name__, p1_stats[2], p1_stats[0],
                                                                   p1_stats[1]).center(50))
            print('_' * 60)
            print()

        return p1_stats


if __name__ == '__main__':
    go_game = Go()
    qlearner = QLearner()
    NUM = qlearner.GAME_NUM

    print('Training QLearner against RandomPlayer for {} times......'.format(NUM))
    go_game.battle(qlearner, RandomPlayer(), NUM, learn=True, show_result=False)
    go_game.battle(RandomPlayer(), qlearner, NUM, learn=True, show_result=False)
    qlearner.save_QValues()
    #loaded_table = qlearner.load_QValues()
    #print(qlearner.q_values == loaded_table)
    # for k,v in loaded_table.items():
    #     print(f"{k} : {type(v)}")

    print('Playing QLearner against RandomPlayer for 1000 times......')
    q_rand = go_game.battle(qlearner, RandomPlayer(), 1000)
    rand_q = go_game.battle(RandomPlayer(), qlearner, 1000)

    winning_rate_w_random_player = round(100 - (q_rand[2] + rand_q[1]) / 2, 2)

    print("Summary:")
    print("_" * 60)
    print("QLearner VS  RandomPlayer |  Win/Draw Rate = {}%".format(winning_rate_w_random_player))