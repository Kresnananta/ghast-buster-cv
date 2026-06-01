import os
import pygame
import constant


_sounds = {}
_current_music = None
_audio_enabled = False


def init_audio():
    global _audio_enabled

    try:
        pygame.mixer.init()
        pygame.mixer.music.set_volume(constant.MUSIC_VOLUME)
        _load_sounds()
        _audio_enabled = True
    except pygame.error as error:
        _audio_enabled = False
        print(f"Audio disabled: {error}")


def _load_sound(name, path):
    if not os.path.exists(path):
        print(f"Sound not found: {path}")
        return

    sound = pygame.mixer.Sound(path)
    sound.set_volume(constant.SFX_VOLUME)
    _sounds[name] = sound


def _load_sounds():
    _load_sound("hit", constant.SOUND_HIT)
    _load_sound("death", constant.SOUND_DEATH)
    _load_sound("select", constant.SOUND_SELECT)
    _load_sound("shoot", constant.SOUND_SHOOT)
    _load_sound("deflect", constant.SOUND_DEFLECT)


def play_menu_music():
    global _current_music

    if not _audio_enabled:
        return

    if _current_music == constant.SOUND_MENU_BGM:
        return

    if not os.path.exists(constant.SOUND_MENU_BGM):
        print(f"Music not found: {constant.SOUND_MENU_BGM}")
        return

    pygame.mixer.music.load(constant.SOUND_MENU_BGM)
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(constant.MUSIC_VOLUME)
    _current_music = constant.SOUND_MENU_BGM


def stop_music():
    global _current_music

    if not _audio_enabled:
        return

    pygame.mixer.music.stop()
    _current_music = None


def play_sfx(name):
    if not _audio_enabled:
        return

    sound = _sounds.get(name)
    if sound is not None:
        sound.play()


def shutdown_audio():
    if _audio_enabled:
        pygame.mixer.quit()