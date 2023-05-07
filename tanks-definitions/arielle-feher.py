from tanks import TankController, MOVE_FORWARD, MOVE_BACKWARD, TURN_LEFT, TURN_RIGHT, SHOOT, TANK_SIZE, GameState, Tank, normalize_angle, Bullet
from math import degrees, atan2, sqrt

class ArielleFeherTankController(TankController):
    def __init__(self, tank_id: str):
        self.tank_id = tank_id

    @property
    def id(self) -> str:
        return "arielle-feher"

    def dodge_bullets(self, gamestate: GameState, my_tank: Tank) -> str:
        for bullet in gamestate.bullets:
            dx = bullet.position[0] - my_tank.position[0]
            dy = bullet.position[1] - my_tank.position[1]
            distance = sqrt(dx * dx + dy * dy)
            if distance <= TANK_SIZE[0] * 3:
                return MOVE_FORWARD if dy > 0 else None
        return None

    def decide_what_to_do_next(self, gamestate: GameState) -> str:
        my_tank = next(tank for tank in gamestate.tanks if tank.id == self.id)

        dodge_action = self.dodge_bullets(gamestate, my_tank)
        if dodge_action:
            return dodge_action

        closest_enemy_tank = None
        min_distance = float("inf")
        for tank in gamestate.tanks:
            if tank.id != self.id and tank.health > 0:
                dx = tank.position[0] - my_tank.position[0]
                dy = tank.position[1] - my_tank.position[1]
                distance = sqrt(dx * dx + dy * dy)
                if distance < min_distance:
                    min_distance = distance
                    closest_enemy_tank = tank

        if closest_enemy_tank is None:
            return MOVE_FORWARD

        dx = closest_enemy_tank.position[0] - my_tank.position[0]
        dy = closest_enemy_tank.position[1] - my_tank.position[1]
        target_angle = degrees(atan2(-dy, dx))
        angle_diff = normalize_angle(target_angle - my_tank.angle)

        if 5 <= angle_diff <= 10 or 340 <= angle_diff <= 359:
            return SHOOT
        else:
            if angle_diff < 180:
                return TURN_LEFT
            else:
                return TURN_RIGHT
