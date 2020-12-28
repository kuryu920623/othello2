from django.core.management.base import BaseCommand
from othello2.views import Board, PlayerCharacter as PlayerCharacterBase
from ...models import PlayerCharacters
import itertools
import random
import json

class PlayerCharacter(PlayerCharacterBase):
    def __init__(self, color, borad_scores=None, weingts=None, recursive_depth=2):
        super().__init__(color, borad_scores, weingts, recursive_depth)
        self.read_last_turn = 50


class Command(BaseCommand):
    def handle(self, *args, **options):
        player_objs = self.create_player(10)
        for i, j in itertools.permutations(range(10), 2):
            p1 = 
        return
        while True:
            p1 = PlayerCharacter(1, recursive_depth=2)
            p2 = PlayerCharacter(-1, recursive_depth=2)
            board = Board(0x0000000810000000, 0x0000001008000000)
            while True:
                self.manual_turn(1)
                if self.board.is_game_over():
                    self.board.print_board()
                    break

                self.board.print_board()
                self.pc_turn(-1)
                if self.board.is_game_over():
                    self.board.print_board()
                    break

    def add_arguments(self, parser):
        return
        parser.add_argument('params', nargs='+', type=str)

    def create_player(self, count):
        player_objs = []
        for i in range(count):
            borad_scores = [random.randrange(-99, 100) for i in range(10)]
            weights = [random.randrange(1, 11) for i in range(3)]
            player = PlayerCharacter(1, borad_scores, weights)
            dic = {
                'borad_scores': ','.join(map(str, borad_scores)),
                'borad_score_dict': json.dumps(player.score_index),
                'weight1': weights[0],
                'weight2': weights[1],
                'weight3': weights[2],
            }
            for num in range(1,11):
                key = f'score{str(num).zfill(2)}'
                dic[key] = borad_scores[num - 1]
            obj = PlayerCharacters.objects.create(**dic)
            player_objs.append(obj)
        return player_objs

class OneMatch(object):
    def __init__(self):
        self.board = Board(0x0000000810000000, 0x0000001008000000)
        self.player_black = PlayerCharacter(1, recursive_depth=6)
        self.player_white = PlayerCharacter(-1, recursive_depth=5)

    def start(self):
        while True:
            self.board.print_board()
            self.manual_turn(1)
            if self.board.is_game_over():
                self.board.print_board()
                break

            self.board.print_board()
            self.pc_turn(-1)
            if self.board.is_game_over():
                self.board.print_board()
                break

    def manual_turn(self, color):
        if not self.board.has_legal(color):
            print('no available positions')
            return
        while True:
            message = {1: 'black', -1: 'white'}[color]
            pos = input(f'{message} pos >>> ')
            pos = 2 ** int(pos)
            if not (self.board.get_legal_bit(color) & pos):
                print('not legal')
                continue
            self.board = self.board.put_stone(pos, color)
            break

    def pc_turn(self, color):
        if not self.board.has_legal(color):
            print('no available positions')
            return
        player = {1: self.player_black, -1: self.player_white}[color]
        put = player.get_best_move_bit(self.board)
        if put:
            print(self.bit_to_number(put))
            self.board = self.board.put_stone(put, color)

    # デバッグ用
    def print_bit(self, bit):
        tmp = format(bit, 'b').zfill(64)
        for i in range(8):
            print(tmp[i*8:i*8+8])
        print()

    def bit_to_number(self, bit):
        return len(format(bit, 'b')) - 1
