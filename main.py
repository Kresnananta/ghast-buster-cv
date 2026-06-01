import cv2
import constant
from preset_manager import import_preset
from renderer import overlay_transparent, draw_hp, draw_deflect_effects
from vision import detect_hand
from assets_loader import load_assets
from game import create_ghast, update_ghast, update_fireballs

cap = cv2.VideoCapture(0)

# load assets
assets = load_assets()

shield_img = assets["shield"]
fireball_img = assets["fireball"]
ghast_idle_frames = assets["ghast_idle_frames"]
ghast_shooting_img = assets["ghast_shooting"]

# default value
lower_skin = constant.DEFAULT_LOWER_SKIN
upper_skin = constant.DEFAULT_UPPER_SKIN

ghast = create_ghast()
fireballs = []
deflect_effects = []

hp = constant.MAX_HP
game_over = False

frame_count = 0
ghast_idle_index = 0

while True:
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
        shield_x = cx - constant.SHIELD_SIZE // 2
        shield_y = cy - constant.SHIELD_SIZE // 2
        overlay_transparent(frame, shield_img, shield_x, shield_y)

        if largest_contour is not None:
            cv2.drawContours(frame, [largest_contour], -1, (0, 255, 0), 2)

    # ghast movemenent + shooting
    frame_count += 1

    if not game_over:
        update_ghast(ghast, fireballs)

    # render ghast
    if ghast["state"] == "idle":
        if frame_count % 4 == 0:
            ghast_idle_index = (ghast_idle_index + 1) % len(ghast_idle_frames)

        current_ghast_img = ghast_idle_frames[ghast_idle_index]
    else:
        current_ghast_img = ghast_shooting_img

    overlay_transparent(frame, current_ghast_img, int(ghast["x"]), ghast["y"])

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
    for fireball in fireballs:
        fx = fireball["x"]
        fy = fireball["y"]

        fireball_x = int(fx) - constant.FIREBALL_SIZE // 2
        fireball_y = int(fy) - constant.FIREBALL_SIZE // 2
        overlay_transparent(frame, fireball_img, fireball_x, fireball_y)

    draw_deflect_effects(frame, deflect_effects)
    draw_hp(frame, hp)

    if game_over:
        dim = frame.copy()
        cv2.rectangle(dim, (0, 0), (constant.CAM_W, constant.CAM_H), (0, 0, 0), -1)
        frame = cv2.addWeighted(frame, 0.45, dim, 0.55, 0)

        cv2.putText(frame, "GAME OVER", (145, 220),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 0, 255), 4)
        cv2.putText(frame, "Press R to Restart or Q to Quit", (95, 265),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

    cv2.putText(frame, "Press 'i' to Import Preset", (20, 30), 
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
        ghast = create_ghast()
        fireballs.clear()
        deflect_effects.clear()
        hp = constant.MAX_HP
        game_over = False
        frame_count = 0
        ghast_idle_index = 0

    # quit game
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()