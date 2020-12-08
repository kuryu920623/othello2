from django.core.management.base import BaseCommand
from othello2.views import Board, PlayerCharacter

class Command(BaseCommand):

    def handle(self, *args, **options):
        p = PlayerCharacter(1, recursive_depth=5)
        match = OneMatch()
        match.start()

    def add_arguments(self, parser):
        return
        parser.add_argument('params', nargs='+', type=str)

class OneMatch(object):
    def __init__(self):
        self.board = Board(0x0000000810000000, 0x0000001008000000)
        self.player_black = PlayerCharacter(1, recursive_depth=5)
        self.player_white = None

    def start(self):
        while True:
            self.board.print_board()
            put = self.player_black.get_best_move_bit(self.board)
            print(self.bit_to_number(put))
            self.board = self.board.put_stone(put, 1)
            if self.board.is_game_over():
                self.board.print_board()
                break

            self.board.print_board()
            self.manual_turn(-1)
            if self.board.is_game_over():
                self.board.print_board()
                break

    def manual_turn(self, color):
        if not self.board.has_legal(color):
            print('no available positions')
            return
        while True:
            pos = input('white pos >>> ')
            pos = 2 ** int(pos)
            if not (self.board.get_legal_bit(color) & pos):
                print('not legal')
                continue
            self.board = self.board.put_stone(pos, color)
            break

    # デバッグ用
    def print_bit(self, bit):
        tmp = format(bit, 'b').zfill(64)
        for i in range(8):
            print(tmp[i*8:i*8+8])
        print()

    def bit_to_number(self, bit):
        return len(format(bit, 'b')) - 1
