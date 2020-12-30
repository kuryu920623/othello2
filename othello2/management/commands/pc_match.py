from django.core.management.base import BaseCommand
from othello2.views import Board, PlayerCharacter as PlayerCharacterBase
from ...models import PlayerCharacters
import itertools
import random
import json
from django.conf import settings


class PlayerCharacter(PlayerCharacterBase):
    def __init__(self, color, borad_scores=None, weingts=None, recursive_depth=2):
        super().__init__(color, borad_scores, weingts, recursive_depth)
        self.read_last_turn = 55


class Command(BaseCommand):
    def handle(self, *args, **options):
        winner_black = PlayerCharacter(1, [100, -40, 20, 20, -60, 10, 10, 10, 10, 10], [5, 15, 0])
        gen = 1
        while True:
            obj = Tournament(winner_black)
            winner = obj.match_n()
            winner_black = winner[0]
            winner_white = winner[1]
            dic = {
                'borad_scores': ','.join(map(str, winner_black.borad_scores)),
                'borad_score_black': json.dumps(winner_black.score_index),
                'borad_score_white': json.dumps(winner_white.score_index),
                'weight1': winner_black.weights[0],
                'weight2': winner_black.weights[1],
                'weight3': winner_black.weights[2],
                'generation': gen,
            }
            for num in range(1, 11):
                key = f'score{str(num).zfill(2)}'
                dic[key] = winner_black.borad_scores[num - 1]
            PlayerCharacters.objects.create(**dic)
            # print(f'generation{str(gen).zfill(4)}', winner_black.borad_scores, winner_black.weights)
            gen += 1

    def add_arguments(self, parser):
        return
        parser.add_argument('params', nargs='+', type=str)


class Tournament(object):
    def __init__(self, base_player=None):
        self.players = [self.create_player(base_player) for i in range(16)]
        self.remain = self.players

    def create_player(self, base_player=None):
        if not base_player:
            borad_scores = [random.randrange(-99, 100) for i in range(10)]
            weights = [random.randrange(1, 11) for i in range(3)]
        else:
            base_scores = base_player.borad_scores
            borad_scores = [i + random.randrange(-5, 6) for i in base_scores]
            base_weights = base_player.weights
            weights = [i + random.randrange(-1, 2) for i in base_weights]
        p_black = PlayerCharacter(1, borad_scores, weights)
        p_white = PlayerCharacter(-1, borad_scores, weights)
        print(borad_scores, weights)
        return [p_black, p_white]

    def match_n(self):
        if len(self.remain) == 1:
            return self.remain[0]
        winners = []
        for i in range(0, len(self.remain), 2):
            black = self.remain[i][0]
            white = self.remain[i + 1][1]
            match_obj = PCOneMatch(black, white)
            win = match_obj.match()
            winners.append(self.remain[i + win])
        self.remain = winners
        return self.match_n()


class PCOneMatch(object):
    def __init__(self, black, white):
        self.board = Board(0x0000000810000000, 0x0000001008000000)
        self.players = {1: black, -1: white}

    def match(self):
        for color in itertools.cycle([1, -1]):
            self.pc_turn(color)
            if self.board.is_game_over():
                break
        black_count = self.board.count_bit(self.board.black)
        white_count = self.board.count_bit(self.board.white)
        if black_count > white_count:
            return 0
        else:
            return 1

    def pc_turn(self, color):
        if not self.board.has_legal(color):
            return
        player = self.players[color]
        put = player.get_best_move_bit(self.board)
        if put:
            self.board = self.board.put_stone(put, color)
