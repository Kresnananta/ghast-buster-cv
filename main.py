import cv2
import constant
from preset_manager import import_preset
from renderer import (
    draw_shield,
    draw_ghast,
    draw_fireballs,
    draw_hp,
    draw_deflect_effects,
    draw_game_over,
)
from vision import detect_hand
from assets_loader import load_assets
from game import reset_game_state, update_ghast, update_fireballs
from menu import draw_main_menu, handle_menu_input
from calibrateCam import run_calibration


cap = cv2.VideoCapture(0)

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

# initial state
state = reset_game_state()

ghast = state["ghast"]
fireballs = state["fireballs"]
deflect_effects = state["deflect_effects"]
hp = state["hp"]
game_over = state["game_over"]
frame_count = state["frame_count"]
ghast_idle_index = state["ghast_idle_index"]

app_state = constant.APP_STATE_MENU
menu_selected_index = 0

while True:
    # handle menu
    if app_state == constant.APP_STATE_MENU:
        frame = draw_main_menu(menu_background, menu_selected_index)
        cv2.imshow("Shield Defense", frame)

        key = cv2.waitKey(1) & 0xFF
        menu_selected_index, action = handle_menu_input(key, menu_selected_index)

        if action == "Play Game":
            state = reset_game_state()

            ghast = state["ghast"]
            fireballs = state["fireballs"]
            deflect_effects = state["deflect_effects"]
            hp = state["hp"]
            game_over = state["game_over"]
            frame_count = state["frame_count"]
            ghast_idle_index = state["ghast_idle_index"]

            app_state = constant.APP_STATE_PLAYING

        elif action == "Calibrate Camera":
            cap.release()
            cv2.destroyAllWindows()

            run_calibration()

            cap = cv2.VideoCapture(0)
            app_state = constant.APP_STATE_MENU

        elif action == "Quit Game":
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

    # ghast movemenent + shooting
    frame_count += 1

    if not game_over:
        update_ghast(ghast, fireballs)

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
    if not game_over:
        hp, lost = update_fireballs(
            fireballs,
            hand_detected,
            cx,
            cy,
            hp,
            deflect_effects
        )

        if lost:
            game_over = True

    # render fireballs
    draw_fireballs(frame, fireballs, fireball_img)

    # render efek
    draw_deflect_effects(frame, deflect_effects)
    # render heart
    draw_hp(frame, hp)

    if game_over:
        frame = draw_game_over(frame)

    cv2.putText(frame, "I: Import Preset | M: Menu", (20, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    cv2.imshow("Shield Defense", frame)
    cv2.imshow("Clean Mask", mask)

    key = cv2.waitKey(1) & 0xFF

    # import preset
    if key == ord('i'):
        new_lower, new_upper = import_preset()
        if new_lower is not None:
            lower_skin = new_lower
            upper_skin = new_upper
            print('Preset berhasil di import')
    
    # restart game
    elif key == ord('r'):
        state = reset_game_state()

        ghast = state["ghast"]
        fireballs = state["fireballs"]
        deflect_effects = state["deflect_effects"]
        hp = state["hp"]
        game_over = state["game_over"]
        frame_count = state["frame_count"]
        ghast_idle_index = state["ghast_idle_index"]

    # back to menu
    elif key == ord('m'):
        app_state = constant.APP_STATE_MENU

    # quit game
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()