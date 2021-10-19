import pygame
from math import cos, sin, pi

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

RAY_AMOUNT = 20

wallcolors = {
    '1': RED,
    '2': GREEN,
    '3': BLUE}


class Raycaster(object):
    def __init__(self, screen):
        self.screen = screen
        _, _, self.width, self.height = screen.get_rect()

        self.map = []
        self.blocksize = 50
        self.wallheight = 50

        self.stepSize = 5
        self.turnSize = 5

        self.player = {
            'x': 100,
            'y': 100,
            'fov': 60,
            'angle': 0}

    def load_map(self, filename):
        with open(filename) as file:
            for line in file.readlines():
                self.map.append(list(line))

    def drawPlayerIcon(self, color):
        if self.player['x'] < self.width / 2:
            rect = (self.player['x'] - 2, self.player['y'] - 2, 5, 5)
            self.screen.fill(color, rect)

    def drawBlock(self, x, y, id):
        self.screen.fill(
            wallcolors[id], (x, y, self.blocksize, self.blocksize))

    def castRay(self, angle):
        rads = angle * pi / 180
        dist = 0
        while True:
            x = int(self.player['x'] + dist * cos(rads))
            y = int(self.player['y'] + dist * sin(rads))

            i = int(x/self.blocksize)
            j = int(y/self.blocksize)

            if j < len(self.map):
                if i < len(self.map[j]):
                    if self.map[j][i] != ' ':
                        return dist, self.map[j][i]

            if x < self.width / 2:
                self.screen.set_at((x, y), WHITE)

            dist += 1

    def render(self):
        halfWidth = int(self.width / 2)
        halfHeight = int(self.height / 2)

        for x in range(0, halfWidth, self.blocksize):
            for y in range(0, self.height, self.blocksize):

                i = int(x/self.blocksize)
                j = int(y/self.blocksize)

                if j < len(self.map):
                    if i < len(self.map[j]):
                        if self.map[j][i] != ' ':
                            self.drawBlock(x, y, self.map[j][i])

        self.drawPlayerIcon(pygame.Color('black'))

        for column in range(RAY_AMOUNT):
            angle = self.player['angle'] - (self.player['fov'] / 2) + \
                (self.player['fov'] * column / RAY_AMOUNT)
            dist, id = self.castRay(angle)
            rayWidth = int(((column+1) / RAY_AMOUNT) * halfWidth)
            x = halfWidth + int(((column / RAY_AMOUNT) * halfWidth))
            self.screen.fill(wallcolors[id], (x, halfHeight, rayWidth, 20))

        # Columna divisora
        for i in range(self.height):
            self.screen.set_at((halfWidth, i), BLACK)
            self.screen.set_at((halfWidth+1, i), BLACK)
            self.screen.set_at((halfWidth-1, i), BLACK)


width = 1000
height = 500

pygame.init()

screen = pygame.display.set_mode(
    (width, height), pygame.DOUBLEBUF | pygame.HWACCEL)
screen.set_alpha(None)

rCaster = Raycaster(screen)
rCaster.load_map('map1.txt')


clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 25)


def updateFPS():
    fps = str(int(clock.get_fps()))
    fps = font.render(fps, 1, pygame.Color('white'))
    return fps


isRunning = True
while isRunning:

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            isRunning = False

        elif ev.type == pygame.KEYDOWN:
            newX = rCaster.player['x']
            newY = rCaster.player['y']
            forward = rCaster.player['angle'] * pi / 180
            right = (rCaster.player['angle'] + 90) * pi / 180
            if ev.key == pygame.K_ESCAPE:
                isRunning = False
            elif ev.key == pygame.K_w:
                newX += cos(forward) * rCaster.stepSize
                newY += sin(forward) * rCaster.stepSize
            elif ev.key == pygame.K_s:
                newX -= cos(forward) * rCaster.stepSize
                newY -= sin(forward) * rCaster.stepSize
            elif ev.key == pygame.K_a:
                newX -= cos(right) * rCaster.stepSize
                newY -= sin(right) * rCaster.stepSize
            elif ev.key == pygame.K_d:
                newX += cos(right) * rCaster.stepSize
                newY += sin(right) * rCaster.stepSize
            elif ev.key == pygame.K_q:
                rCaster.player['angle'] -= rCaster.turnSize
            elif ev.key == pygame.K_e:
                rCaster.player['angle'] += rCaster.turnSize

            i = int(newX/rCaster.blocksize)
            j = int(newY/rCaster.blocksize)

            if rCaster.map[j][i] == ' ':
                rCaster.player['x'] = newX
                rCaster.player['y'] = newY

    screen.fill(pygame.Color('gray'))

    rCaster.render()

    # FPS
    screen.fill(pygame.Color('black'), (0, 0, 30, 30))
    text = font.render('3', 1, pygame.Color('white'))
    screen.blit(updateFPS(), (0, 0))

    clock.tick(60)

    pygame.display.update()


pygame.quit()
