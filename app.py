import pyxel

from game.audio import play_bgm, setup_audio
from game.constants import SCREEN_W, SCREEN_H, FPS, TITLE
from game.game import Game


class App:
    def __init__(self) -> None:
        pyxel.init(SCREEN_W, SCREEN_H, title=TITLE, fps=FPS)
        setup_audio()
        play_bgm()
        self._game = Game()

    def run(self) -> None:
        pyxel.run(self.update, self.draw)

    def update(self) -> None:
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
        self._game.update()

    def draw(self) -> None:
        self._game.draw()
