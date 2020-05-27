import pygame as pg
import sys
from settings import *
from sprites import *
import random
import numpy as np


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500, 100)
        self.map = [[]]

    def init_q_table(self):
        self.left = 0
        self.right = 1
        self.down = 2
        self.up = 3

        # alpha is the learning rate. It is the extent that q values are updated every iteration
        self.alpha = 0.1

        # gamma is the discount factor. Determines how much importance we want to give to future rewards
        # high value means capture the best long-term effective reward. Low value means immediate reward (greedy)
        self.gamma = 0.6

        # epsilon is the "exploration" parameter. Allowing for more exploration means this will prevent "overfitting",
        # where the algorithm finds a local maximum instead of the global one and optimizes that local maximum very
        # heavily, never finding the global. Lower epsilon means more exploration
        self.epsilon = 0.1

        # Q_new = (1 - alpha) * Q_old + alpha * (reward + gamma * max(Q_next_state_all_actions))

        state_space = self.map_height * self.map_width  # number of possible positions
        action_space = 4    # four possible directions to move
        self.q_table = np.zeros([state_space, action_space])

        # Initialize edges case states
        for row in range(0, self.map_height):
            if row == 0:
                for col in range(0, self.map_width):
                    state = row * self.map_width + col
                    self.q_table[state][self.up] = -9999.99
            elif row == self.map_height - 1:
                for col in range(0, self.map_width):
                    state = row * self.map_width + col
                    self.q_table[state][self.down] = -9999.99
            else:
                state = row * self.map_width
                self.q_table[state][self.left] = -9999.99
                state = row * self.map_width + self.map_width - 1
                self.q_table[state][self.right] = -9999.99

    def init_map(self, map_file):
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.goals = pg.sprite.Group()
        # Read map data in
        line = map_file.readline()
        self.map_width = int(line[2])
        self.map_height = int(line[0])

        row = 0
        col = 0

        # TODO: Add in numbers in each tile representing Q value
        # pg.font.init()
        #
        # for x in range(0, self.map_width):
        #     for y in range(0, self.map_height):

        for line in map_file:
            for char in line:
                tile = Tile(ground)
                if char == '.':
                    tile = Tile(ground)
                elif char == '\n':
                    col = 0
                    break
                elif char == '#':
                    tile = Tile(wall)
                    Wall(self, col, row)
                elif char == 'X':
                    tile = Tile(goal)
                    Goal(self, col, row)
                elif char == "$":
                    tile = Tile(start)
                    self.startY = row
                    self.startX = col
                else:
                    print("Error: Character in map not recognized.")
                    exit(1)
                self.map[row].append(tile)
                col += 1
            self.map.append([])
            row += 1
        map_file.close()

    def new(self, filename):
        # initialize all variables and do all the setup for a new game
        try:
            map_file = open(filename, mode='r')
        except IOError:
            print("Error opening map file.")
            exit(1)

        self.init_map(map_file)
        self.init_q_table()
        self.player = Player(self, self.startX, self.startY)

    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True
        episode = 0
        total_episodes = 10000
        while self.playing and episode < total_episodes: # 10000 is the number of episodes
            self.dt = self.clock.tick(FPS) / 1000
            self.events(episode, total_episodes)
            self.update()
            self.draw()
            if episode < total_episodes:
                episode += 1

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        # update portion of the game loop
        self.all_sprites.update()

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, DARKGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, DARKGREY, (0, y), (WIDTH, y))

    def draw(self):
        self.screen.fill(BGCOLOR)
        self.draw_grid()
        self.all_sprites.draw(self.screen)
        pg.display.flip()

    def random_direction(self):
        # bound checking for random movements
        col, row = self.player.get_pos()
        direction = int(random.randint(0, 3))
        if direction == 0:
            if col == 0:
                return self.random_direction()
            else:
                return 0
        elif direction == 1:
            if col == self.map_width - 1:
                return self.random_direction()
            else:
                return 1
        elif direction == 2:
            if row == self.map_height - 1:
                return self.random_direction()
            else:
                return 2
        elif direction == 3:
            if row == 0:
                return self.random_direction()
            else:
                return 3

    def move(self, direction):
        if direction == self.left:
            return self.player.move(self, dx=-1)
        if direction == self.right:
            return self.player.move(self, dx=1)
        if direction == self.down:
            return self.player.move(self, dy=-1)
        if direction == self.up:
            return self.player.move(self, dy=1)

    def step(self, action):
        # Episode will end when mouse reaches cheese or hits cat. done returns True
        move_success = self.move(action)
        col, row = self.player.get_pos()
        state = row * self.map_width + col
        terrain = self.map[row][col].terrain
        if not move_success:
            return state, -9999.99, False
        # Negative reward
        if terrain == wall:
            self.player.reset(self.startX, self.startY)
            return state, -9999.99, True
        # Positive reward
        if terrain == goal:
            self.player.reset(self.startX, self.startY)
            return state, 9999.99, True
        # TODO: Maybe tweak the 0 to a positive number?
        return state, 0, False

    def events(self, episode, total_episodes=10000):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                # if event.key == pg.K_LEFT:
                #     self.player.move(self, dx=-1)
                # if event.key == pg.K_RIGHT:
                #     self.player.move(self, dx=1)
                # if event.key == pg.K_UP:
                #     self.player.move(self, dy=-1)
                # if event.key == pg.K_DOWN:
                #     self.player.move(self, dy=1)

        if episode < total_episodes:
            # reset the mouse
            self.player.reset(self.startX, self.startY)

            done = False

            col, row = self.player.get_pos()
            state = row * self.map_width + col

            while not done:
                temp = random.uniform(0, 1)
                if temp < self.epsilon:
                    action = self.random_direction()
                else:
                    # move in direction that leads to max q value
                    action = np.argmax(self.q_table[state])

                next_state, reward, done = self.step(action)

                old_val = self.q_table[state][action]
                next_max = max(self.q_table[next_state])

                new_value = (1 - self.alpha) * old_val + self.alpha * (reward + self.gamma * next_max)

                self.q_table[state][action] = new_value

                self.update()
                self.draw()

    def show_start_screen(self):
        pass

    def show_go_screen(self):
        pass


# create the game object
if __name__ == "__main__":
    g = Game()
    g.show_start_screen()
    filename = sys.argv[1]
    while True:
        g.new(filename)
        g.run()
        g.show_go_screen()
