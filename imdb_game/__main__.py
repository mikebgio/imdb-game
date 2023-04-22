from imdb_game.gameshow import game
import database._dataclasses


def main():
    player = database._dataclasses.Player('mike')
    gameshow = game.GameShowHost(player)
    gameshow.game_loop()


if __name__ == '__main__':
    main()