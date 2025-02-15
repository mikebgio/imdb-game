from game import GameShowHost
from game_classes import Player


def main():
    player = Player('mike')
    gameshow = GameShowHost(player)
    gameshow.game_loop()


if __name__ == '__main__':
    main()
