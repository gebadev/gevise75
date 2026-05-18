import pyxel


_BGM_MUSIC = 0
_SFX_CHANNEL = 3
_SFX_TRAIL_SUCCESS = 4
_SFX_MISS = 5
_SFX_STAGE_CLEAR = 6
_SFX_GAME_OVER = 7
_bgm_playing = False


def setup_audio() -> None:
    """Register simple retro sci-fi action BGM and sound effects."""
    lead = _notes(
        """
        c4 e4 g4 r a4 g4 e4 d4
        e4 g4 c4 r b4 a4 g4 e4
        f4 a4 c4 r d4 c4 a4 g4
        e4 g4 a4 g4 e4 d4 c4 r
        """
    )
    bass = _notes(
        """
        c2 g1 c2 r c2 g1 c2 r
        a1 e2 a1 r a1 e2 a1 r
        f1 c2 f1 r f1 c2 f1 r
        g1 d2 g1 r g1 d2 c2 r
        """
    )
    arpeggio = _notes(
        """
        c3 e3 g3 c4 g3 e3 g3 e3
        a2 e3 a3 c4 a3 e3 a3 e3
        f3 a3 c4 f4 c4 a3 c4 a3
        g2 d3 g3 b3 g3 d3 g3 d3
        """
    )
    pulse = _notes(
        """
        c1 r r c1 g1 r c1 r
        a1 r r a1 e2 r a1 r
        f1 r r f1 c2 r f1 r
        g1 r r g1 d2 g1 c1 r
        """
    )

    pyxel.sounds[0].set(lead, "s", "76766754", "nnnfnnff", 9)
    pyxel.sounds[1].set(bass, "t", "76556554", "nnnnnnnn", 9)
    pyxel.sounds[2].set(arpeggio, "p", "23344332", "nnnnnnnn", 9)
    pyxel.sounds[3].set(pulse, "t", "70506030", "fnffnfff", 9)
    pyxel.musics[_BGM_MUSIC].set([0], [1], [2], [3])

    pyxel.sounds[_SFX_TRAIL_SUCCESS].set(
        _notes("g4 r c4 r g4"), "n", "70707", "fnfnf", 6
    )
    pyxel.sounds[_SFX_MISS].set(
        _notes("c3 g2 c2"), "n", "765", "ffn", 10
    )
    pyxel.sounds[_SFX_STAGE_CLEAR].set(
        _notes("c4 e4 g4 c4 g4 c4"), "s", "765676", "nnnnnn", 14
    )
    pyxel.sounds[_SFX_GAME_OVER].set(
        _notes("c3 a2 f2 c2"), "t", "7654", "fffn", 18
    )


def play_bgm() -> None:
    global _bgm_playing
    if _bgm_playing:
        return

    pyxel.playm(_BGM_MUSIC, loop=True)
    _bgm_playing = True


def stop_bgm() -> None:
    global _bgm_playing
    if not _bgm_playing:
        return

    pyxel.stop()
    _bgm_playing = False


def play_trail_success_sfx() -> None:
    _play_sfx(_SFX_TRAIL_SUCCESS)


def play_miss_sfx() -> None:
    _play_sfx(_SFX_MISS)


def play_stage_clear_sfx() -> None:
    _play_sfx(_SFX_STAGE_CLEAR)


def play_game_over_sfx() -> None:
    _play_sfx(_SFX_GAME_OVER)


def _play_sfx(sound_id: int) -> None:
    pyxel.play(_SFX_CHANNEL, sound_id)


def _notes(pattern: str) -> str:
    return "".join(pattern.split())
