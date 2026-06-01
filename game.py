import math
import random
import constant

def create_ghast():
    return {
        "x": (constant.CAM_W - constant.GHAST_W) // 2,
        "y": constant.GHAST_Y,
        "vx": constant.GHAST_SPEED,
        "cooldown": constant.FIREBALL_COOLDOWN,
        "state": "idle",
        "shoot_timer": 0,
        "burst_left": 0,
        "burst_timer": 0,
    }


def spawn_deflect_effect(deflect_effects, x, y):
    sparks = []

    for _ in range(constant.DEFLECT_SPARK_COUNT):
        angle = random.uniform(-math.pi, 0)
        speed = random.uniform(3, constant.DEFLECT_SPARK_SPEED)

        sparks.append({
            "x": x,
            "y": y,
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
        })

    deflect_effects.append({
        "x": x,
        "y": y,
        "life": constant.DEFLECT_EFFECT_LIFE,
        "max_life": constant.DEFLECT_EFFECT_LIFE,
        "sparks": sparks,
    })


def update_ghast(ghast, fireballs):
    
    if ghast["state"] == "idle":
        ghast["x"] += ghast["vx"]

        if ghast["x"] <= 0 or ghast["x"] + constant.GHAST_W >= constant.CAM_W:
            ghast["vx"] *= -1
            ghast["x"] = max(0, min(ghast["x"], constant.CAM_W - constant.GHAST_W))

        ghast["cooldown"] -= 1

        if ghast["cooldown"] <= 0:
            ghast["state"] = "shooting"
            ghast["shoot_timer"] = constant.GHAST_SHOOT_DURATION
            ghast["burst_left"] = constant.GHAST_BURST_COUNT
            ghast["burst_timer"] = constant.GHAST_SHOOT_START_DELAY

    elif ghast["state"] == "shooting":
        ghast["shoot_timer"] -= 1
        ghast["burst_timer"] -= 1

        if ghast["burst_left"] > 0 and ghast["burst_timer"] <= 0 and len(fireballs) < constant.MAX_FIREBALLS:
            mouth_x = int(ghast["x"]) + constant.GHAST_MOUTH_OFFSET_X
            mouth_y = ghast["y"] + constant.GHAST_MOUTH_OFFSET_Y

            spread_index = ghast["burst_left"] - 1
            spread_values = [-constant.GHAST_FIREBALL_SPREAD_X, 0, constant.GHAST_FIREBALL_SPREAD_X]
            vx = spread_values[spread_index % len(spread_values)]

            fireballs.append({
                "x": mouth_x,
                "y": mouth_y,
                "vx": vx,
                "vy": constant.ENEMY_SPEED,
            })

            ghast["burst_left"] -= 1
            ghast["burst_timer"] = constant.GHAST_BURST_INTERVAL

        if ghast["shoot_timer"] <= 0:
            ghast["state"] = "idle"
            ghast["cooldown"] = constant.FIREBALL_COOLDOWN


def update_fireballs(fireballs, hand_detected, cx, cy, hp, deflect_effects):
    game_over = False

    for fireball in fireballs[:]:
        if not game_over:
            fireball["x"] += fireball["vx"]
            fireball["y"] += fireball["vy"]

        fx = fireball["x"]
        fy = fireball["y"]

        if hand_detected and not game_over:
            distance = math.sqrt(pow((cx - fx), 2) + pow((cy - fy), 2))

            if distance < (constant.SHIELD_RAD + constant.ENEMY_RAD):
                fireballs.remove(fireball)
                spawn_deflect_effect(deflect_effects, int(fx), int(fy))
                continue

        if fy > constant.CAM_H or fx < 0 or fx > constant.CAM_W:
            fireballs.remove(fireball)
            hp -= 1

            if hp <= 0:
                hp = 0
                game_over = True
    
    return hp, game_over