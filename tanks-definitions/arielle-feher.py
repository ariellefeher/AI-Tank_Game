from tkinter.tix import Tree

from tanks import TankController, MOVE_FORWARD, MOVE_BACKWARD, TURN_LEFT, TURN_RIGHT, SHOOT, TANK_SIZE, GameState, Tank, normalize_angle, Bullet
from math import degrees, atan2, sqrt
import random


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
                bullet_angle = degrees(atan2(-dy, dx))
                if abs(bullet_angle - my_tank.angle) < 90:
                    return random.choice([MOVE_FORWARD, TURN_LEFT])
                else:
                    return random.choice([TURN_LEFT, TURN_RIGHT])
            return None

    def find_closest_enemy_tank(self, gameState: GameState) -> Tank:
        my_tank = next(tank for tank in gameState.tanks if tank.id == self.id)
        alive_enemy_tanks = [tank for tank in gameState.tanks if tank.id != self.id and tank.health > 0]

        def calculate_distance(tank1: Tank, tank2: Tank) -> float:
            dx = tank1.position[0] - tank2.position[0]
            dy = tank1.position[1] - tank2.position[1]
            return sqrt(dx * dx + dy * dy)

        closest_enemy_tank = min(alive_enemy_tanks, key=lambda enemy_tank: calculate_distance(my_tank, enemy_tank))
        return closest_enemy_tank

    def find_closest_tree(self, gameState: GameState, my_tank: Tank) -> Tree:
        if not gameState.trees:  # Assuming there is a list of trees in the game state
            return None

        def calculate_distance(tank: Tank, tree: Tree) -> float:
            dx = tank.position[0] - tree.position[0]  # Using tree.position instead of tree
            dy = tank.position[1] - tree.position[1]
            return sqrt(dx * dx + dy * dy)

        closest_tree = min(gameState.trees, key=lambda tree: calculate_distance(my_tank, tree))
        return closest_tree

    def retreat_from_enemy(self, gamestate: GameState, my_tank: Tank, previous_position: tuple = None,
                           stuck_time: int = 0) -> str:
        closest_enemy_tank = self.find_closest_enemy_tank(gamestate)
        dx_enemy = closest_enemy_tank.position[0] - my_tank.position[0]
        dy_enemy = closest_enemy_tank.position[1] - my_tank.position[1]
        distance_to_enemy = sqrt(dx_enemy * dx_enemy + dy_enemy * dy_enemy)

        if distance_to_enemy <= TANK_SIZE[0] * 3:
            # If enemy is too close, retreat
            # Check if the tank is stuck
            if previous_position == my_tank.position:
                stuck_time += 1
            else:
                stuck_time = 0

            previous_position = my_tank.position

            # If the tank is stuck for more than a certain amount of time, try to steer clear of the obstacle
            if stuck_time > 3:  # you can adjust this value
                return random.choice([TURN_LEFT, TURN_RIGHT])

            # Find closest tree
            closest_tree = self.find_closest_tree(gamestate, my_tank)

            # Calculate the distance to the closest tree
            dx_tree = closest_tree.position[0] - my_tank.position[0]
            dy_tree = closest_tree.position[1] - my_tank.position[1]
            distance_to_tree = sqrt(dx_tree * dx_tree + dy_tree * dy_tree)

            # If the tree is in the path of retreat, navigate around it
            if distance_to_tree <= TANK_SIZE[0] * 3:
                target_angle = degrees(atan2(-dy_tree, dx_tree))
                angle_diff = normalize_angle(target_angle - my_tank.angle)
                if angle_diff < 180:
                    return TURN_RIGHT
                else:
                    return TURN_LEFT

            # If there is no obstacle, retreat in a straight line
            return MOVE_BACKWARD

        # If the enemy is not too close, no need to retreat
        return None

    def decide_what_to_do_next(self, gamestate: GameState) -> str:

        my_tank = next(tank for tank in gamestate.tanks if tank.id == self.id)

        dodge_action = self.dodge_bullets(gamestate, my_tank)
        if dodge_action:
            return dodge_action

        retreat_action = self.retreat_from_enemy(gamestate, my_tank, self.previous_position, self.stuck_time)
        if retreat_action:
            return retreat_action

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
        distance_to_enemy = sqrt(dx * dx + dy * dy)

        # if distance_to_enemy <= TANK_SIZE[0] * 3 :
        #     return MOVE_BACKWARD


        if 1 <= angle_diff <= 2 or 357 <= angle_diff <= 359:
            return SHOOT
        else:
            if angle_diff < 90:
                return TURN_LEFT
            else:
                return TURN_RIGHT

        # # Find closest tree
        # closest_tree = self.find_closest_tree(gamestate, my_tank)
        #
        # # Calculate the distance to the closest tree
        # dx = closest_tree.position[0] - my_tank.position[0]  # Using tree.position instead of tree
        # dy = closest_tree.position[1] - my_tank.position[1]
        # distance_to_tree = sqrt(dx * dx + dy * dy)
        #
        # closest_enemy_tank = self.find_closest_enemy_tank(gamestate)
        # dx_enemy = closest_enemy_tank.position[0] - my_tank.position[0]
        # dy_enemy = closest_enemy_tank.position[1] - my_tank.position[1]
        # distance_to_enemy = sqrt(dx_enemy * dx_enemy + dy_enemy * dy_enemy)
        #
        # # if not hiding behind a tree, advance towards the nearest one
        # if distance_to_tree > TANK_SIZE[0] * 3:
        #     return MOVE_FORWARD
        #
        # # If Already hiding behind a tree, find enemy tanks and shoot to them
        # else:
        #
        #     if distance_to_tree <= TANK_SIZE[0] * 3:
        #         if distance_to_enemy <= TANK_SIZE[0] * 3:
        #             # If enemy is too close, retreat back to tree
        #             return MOVE_BACKWARD
        #         else:
        #             # Rotate around the tree to attack enemy tank
        #             target_angle = degrees(atan2(-dy_enemy, dx_enemy))
        #             angle_diff = normalize_angle(target_angle - my_tank.angle)
        #             if 5 <= angle_diff <= 10 or 340 <= angle_diff <= 359:
        #                 return SHOOT
        #             else:
        #                 if angle_diff < 180:
        #                     return TURN_LEFT
        #                 else:
        #                     return TURN_RIGHT
