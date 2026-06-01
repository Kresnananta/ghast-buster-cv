import cv2
import constant
from preset_manager import import_preset
from renderer import (
    draw_shield,
    draw_ghast,
    draw_fireballs,
    draw_hp,
    draw_deflect_effects,
    draw_score,
    draw_active_preset,
    draw_countdown,
)
from vision import detect_hand
from assets_loader import load_assets
from game import reset_game_state, update_ghast, update_fireballs
from menu import draw_main_menu, handle_menu_input
from calibrateCam import run_calibration
from death_screen import draw_death_screen, handle_death_input
from audio_manager import (
    init_audio,
    play_menu_music,
    stop_music,
    play_sfx,
    shutdown_audio,
)


cap = cv2.VideoCapture(0)

# init audio
init_audio()
play_menu_music()

# load assets
assets = load_assets()

shield_img = assets["shield"]
fireball_img = assets["fireball"]
ghast_idle_frames = assets["ghast_idle_frames"]
ghast_shooting_img = assets["ghast_shooting"]
menu_background = assets["menu_background"]

# default value
lower_skin = constant.DEFAULT_LOWER_SKIN
upper_skin = constant.DEFAULT_UPPER_SKIN

active_preset_name = "Default"

# initial state
state = reset_game_state()

ghast = state["ghast"]
fireballs = state["fireballs"]
deflect_effects = state["deflect_effects"]
hp = state["hp"]
score = state["score"]
game_over = state["game_over"]
frame_count = state["frame_count"]
ghast_idle_index = state["ghast_idle_index"]

app_state = constant.APP_STATE_MENU
menu_selected_index = 0
death_selected_index = 0
countdown_frames = 0

while True:

    # handle menu
    if app_state == constant.APP_STATE_MENU:
        frame = draw_main_menu(menu_background, menu_selected_index)
        cv2.imshow("Shield Defense", frame)

        key = cv2.waitKey(1) & 0xFF
        menu_selected_index, action = handle_menu_input(key, menu_selected_index)
        # click sound kalo navigasi menu
        if key in [ord('w'), ord('W'), ord('s'), ord('S'), 82, 84]:
            play_sfx("select")

        if action == "Play Game":
            stop_music()
            state = reset_game_state()

            ghast = state["ghast"]
            fireballs = state["fireballs"]
            deflect_effects = state["deflect_effects"]
            hp = state["hp"]
            game_over = state["game_over"]
            frame_count = state["frame_count"]
            ghast_idle_index = state["ghast_idle_index"]

            countdown_frames = constant.COUNTDOWN_FRAMES
            app_state = constant.APP_STATE_COUNTDOWN

        elif action == "Calibrate Camera":
            stop_music()
            cap.release()
            cv2.destroyAllWindows()

            run_calibration()

            cap = cv2.VideoCapture(0)
            app_state = constant.APP_STATE_MENU
            play_menu_music()

        elif action == "Import Preset":
            play_sfx("select")

            new_lower, new_upper, preset_name = import_preset()
            if new_lower is not None:
                lower_skin = new_lower
                upper_skin = new_upper
                active_preset_name = preset_name
                print(f'Preset berhasil di import: {active_preset_name}')

        elif action == "Quit Game":
            play_sfx("select")
            break

        continue
    
    # handle game
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    mask, hand_detected, cx, cy, largest_contour = detect_hand(
        frame,
        lower_skin,
        upper_skin
    )

    if hand_detected:
        # render shield
        draw_shield(frame, shield_img, cx, cy)

        if largest_contour is not None:
            cv2.drawContours(frame, [largest_contour], -1, (0, 255, 0), 2)

    # handle countdown
    if app_state == constant.APP_STATE_COUNTDOWN:
        countdown_frames -= 1

        frame = draw_countdown(frame, countdown_frames)

        if countdown_frames <= 0:
            app_state = constant.APP_STATE_PLAYING

        cv2.imshow("Shield Defense", frame)
        cv2.imshow("Clean Mask", mask)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break

        elif key == ord('m'):
            play_menu_music()
            app_state = constant.APP_STATE_MENU

        continue

    # ghast movemenent + shooting
    frame_count += 1

    if app_state == constant.APP_STATE_PLAYING and not game_over:
        events = update_ghast(ghast, fireballs)

        for event in events:
            play_sfx(event)

    # render ghast
    ghast_idle_index = draw_ghast(
        frame,
        ghast,
        ghast_idle_frames,
        ghast_shooting_img,
        frame_count,
        ghast_idle_index
    )

    # update fireballs
    if app_state == constant.APP_STATE_PLAYING and not game_over:
        hp, score, lost, events = update_fireballs(
            fireballs,
            hand_detected,
            cx,
            cy,
            hp,
            score,
            deflect_effects
        )

        for event in events:
            play_sfx(event)

        if lost:
            game_over = True
            play_sfx(event)

    # render fireballs
    draw_fireballs(frame, fireballs, fireball_img)

    # render efek
    draw_deflect_effects(frame, deflect_effects)
    # render heart
    draw_hp(frame, hp)
    # render score
    draw_score(frame, score)
    draw_active_preset(frame, active_preset_name)

    # render death screen
    if game_over:
        frame = draw_death_screen(frame, score, death_selected_index)


    cv2.imshow("Shield Defense", frame)
    cv2.imshow("Clean Mask", mask)

    key = cv2.waitKey(1) & 0xFF

    # handle death screen input
    if game_over:
        death_selected_index, action = handle_death_input(key, death_selected_index)
        if key in [ord('w'), ord('W'), ord('s'), ord('S'), 82, 84]:
            play_sfx("select")

        if action == "Retry":
            play_sfx("select")

            state = reset_game_state()

            countdown_frames = constant.COUNTDOWN_FRAMES
            app_state = constant.APP_STATE_COUNTDOWN

            ghast = state["ghast"]
            fireballs = state["fireballs"]
            deflect_effects = state["deflect_effects"]
            hp = state["hp"]
            score = state["score"]
            game_over = state["game_over"]
            frame_count = state["frame_count"]
            ghast_idle_index = state["ghast_idle_index"]
            death_selected_index = 0

        elif action == "Main Menu":
            play_sfx("select")
            play_menu_music()

            state = reset_game_state()

            ghast = state["ghast"]
            fireballs = state["fireballs"]
            deflect_effects = state["deflect_effects"]
            hp = state["hp"]
            score = state["score"]
            game_over = state["game_over"]
            frame_count = state["frame_count"]
            ghast_idle_index = state["ghast_idle_index"]
            death_selected_index = 0
            app_state = constant.APP_STATE_MENU

        elif key == ord('q'):
            break

        continue

    # quit game
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
shutdown_audio()