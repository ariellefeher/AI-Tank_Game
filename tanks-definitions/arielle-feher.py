from tanks import TankController, MOVE_FORWARD, MOVE_BACKWARD, TURN_LEFT, TURN_RIGHT, SHOOT,TANK_SIZE,GameState,Tank,normalize_angle
from math import degrees,atan2,sqrt
import random


class ArielleFeherTankController(TankController):
    def __init__(self, tank_id: str):
        self.tank_id = tank_id

    @property
    def id(self) -> str:
        return "arielle-feher"

    def decide_what_to_do_next(self, gamestate: GameState) -> str:
        my_tank = next(tank for tank in gamestate.tanks if tank.id == self.id)

        # Find the closest enemy tank
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

        # If no enemy tanks found, move randomly
        if closest_enemy_tank is None:
            return random.choice([TURN_LEFT, TURN_RIGHT, MOVE_FORWARD, MOVE_BACKWARD])

        # Calculate angle to the closest enemy tank
        dx = closest_enemy_tank.position[0] - my_tank.position[0]
        dy = closest_enemy_tank.position[1] - my_tank.position[1]
        target_angle = degrees(atan2(-dy, dx))
        angle_diff = normalize_angle(target_angle - my_tank.angle)

        # If angle difference is within a threshold, shoot
        if 1 <= angle_diff <= 10 or 350 <= angle_diff <= 359:
            return SHOOT
        else:
            # Choose between turning and moving based on a probability
            action = random.choices(
                population=[TURN_LEFT, TURN_RIGHT, MOVE_FORWARD, MOVE_BACKWARD],
                weights=[0.25, 0.25, 0.25, 0.25],
                k=1
            )[0]

            # If the angle difference is more significant, turn towards the enemy
            if angle_diff < 180 and (action == TURN_LEFT or action == TURN_RIGHT):
                return TURN_LEFT
            elif angle_diff >= 180 and (action == TURN_LEFT or action == TURN_RIGHT):
                return TURN_RIGHT
            else:
                return action

