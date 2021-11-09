import pygame
import pygame.gfxdraw
import numpy as np
from numba import njit

from math import cos, sin, pi, atan2

RAY_AMOUNT = 100

SPRITE_BACKGROUND = (152, 0, 136, 255)

wallcolors = {
    '1': pygame.Color('red'),
    '2': pygame.Color('green'),
    '3': pygame.Color('blue'),
    '4': pygame.Color('yellow'),
    '5': pygame.Color('purple')
}

wallTextures = {
    '1': pygame.image.load('wall1.png'),
    '2': pygame.image.load('wall2.png'),
    '3': pygame.image.load('wall3.png'),
    '4': pygame.image.load('wall4.png'),
    '5': pygame.image.load('wall5.png')
}

enemies = [{"x": 150,
            "y": 225,
            "sprite": pygame.image.load('Assets/sprite1.png')},

           {"x": 350,
            "y": 125,
            "sprite": pygame.image.load('Assets/sprite7.png')},

           {"x": 300,
            "y": 400,
            "sprite": pygame.image.load('Assets/sprite3.png')}

           ]


class Raycaster(object):
    def __init__(self, screen):
        self.screen = screen
        _, _, self.width, self.height = screen.get_rect()

        self.map = []
        self.zbuffer = [float('inf') for z in range(int(self.width))]

        self.blocksize = 50
        self.wallheight = 50

        self.maxdistance = 300

        self.stepSize = 5
        self.turnSize = 5

        self.player = {
            'x': 80,
            'y': 100,
            'fov': 60,
            'angle': 0}

    def load_map(self, filename):
        with open(filename) as file:
            for line in file.readlines():
                self.map.append(list(line.rstrip()))

    def drawMinimap(self):
        minimapWidth = 100
        minimapHeight = 100

        minimapSurface = pygame.Surface((500, 500))
        minimapSurface.fill(pygame.Color("gray"))

        for x in range(0, 500, self.blocksize):
            for y in range(0, 500, self.blocksize):

                i = int(x/self.blocksize)
                j = int(y/self.blocksize)

                if j < len(self.map):
                    if i < len(self.map[j]):
                        if self.map[j][i] != ' ':
                            tex = wallTextures[self.map[j][i]]
                            tex = pygame.transform.scale(
                                tex, (self.blocksize, self.blocksize))
                            rect = tex.get_rect()
                            rect = rect.move((x, y))
                            minimapSurface.blit(tex, rect)

        rect = (int(self.player['x'] - 4), int(self.player['y']) - 4, 10, 10)
        minimapSurface.fill(pygame.Color('black'), rect)

        for enemy in enemies:
            rect = (enemy['x'] - 4, enemy['y'] - 4, 10, 10)
            minimapSurface.fill(pygame.Color('red'), rect)

        minimapSurface = pygame.transform.scale(
            minimapSurface, (minimapWidth, minimapHeight))
        self.screen.blit(minimapSurface, (self.width -
                         minimapWidth, self.height - minimapHeight))

    def drawSprite(self, obj, size):
        # Pitagoras
        spriteDist = ((self.player['x'] - obj['x']) **
                      2 + (self.player['y'] - obj['y']) ** 2) ** 0.5

        # Angulo
        spriteAngle = atan2(obj['y'] - self.player['y'],
                            obj['x'] - self.player['x']) * 180 / pi

        # Tamaño del sprite
        aspectRatio = obj['sprite'].get_width() / obj['sprite'].get_height()
        spriteHeight = (self.height / spriteDist) * size
        spriteWidth = spriteHeight * aspectRatio

        # Buscar el punto inicial para dibujar el sprite
        angleDif = (spriteAngle - self.player['angle']) % 360
        angleDif = (angleDif - 360) if angleDif > 180 else angleDif
        startX = angleDif * self.width / self.player['fov']
        startX += (self.width / 2) - (spriteWidth / 2)
        startY = (self.height / 2) - (spriteHeight / 2)
        startX = int(startX)
        startY = int(startY)

        for x in range(startX, startX + int(spriteWidth)):
            if (0 < x < self.width) and self.zbuffer[x] >= spriteDist:
                for y in range(startY, startY + int(spriteHeight)):
                    tx = int((x - startX) *
                             obj['sprite'].get_width() / spriteWidth)
                    ty = int((y - startY) *
                             obj['sprite'].get_height() / spriteHeight)
                    texColor = obj['sprite'].get_at((tx, ty))
                    if texColor != SPRITE_BACKGROUND and texColor[3] > 128:
                        self.screen.set_at((x, y), texColor)
                        if y == self.height / 2:
                            self.zbuffer[x] = spriteDist

    def castRay(self, angle):
        rads = angle * pi / 180
        dist = 0
        stepSize = 1
        stepX = stepSize * cos(rads)
        stepY = stepSize * sin(rads)

        playerPos = (self.player['x'], self.player['y'])

        x = playerPos[0]
        y = playerPos[1]

        while True:
            dist += stepSize

            x += stepX
            y += stepY

            i = int(x/self.blocksize)
            j = int(y/self.blocksize)

            if j < len(self.map):
                if i < len(self.map[j]):
                    if self.map[j][i] != ' ':

                        hitX = x - i*self.blocksize
                        hitY = y - j*self.blocksize

                        hit = 0

                        if 1 < hitX < self.blocksize-1:
                            if hitY < 1:
                                hit = self.blocksize - hitX
                            elif hitY >= self.blocksize-1:
                                hit = hitX
                        elif 1 < hitY < self.blocksize-1:
                            if hitX < 1:
                                hit = hitY
                            elif hitX >= self.blocksize-1:
                                hit = self.blocksize - hitY

                        tx = hit / self.blocksize

                        # pygame.draw.line(self.screen, pygame.Color(
                        #    'white'), playerPos, (x, y))
                        return dist, self.map[j][i], tx

    def render(self):
        halfHeight = int(self.height / 2)

        for column in range(RAY_AMOUNT):
            angle = self.player['angle'] - (self.player['fov'] / 2) + \
                (self.player['fov'] * column / RAY_AMOUNT)
            dist, id, tx = self.castRay(angle)

            rayWidth = int((1 / RAY_AMOUNT) * self.width)

            for i in range(rayWidth):
                self.zbuffer[column * rayWidth + i] = dist

            startX = int(((column / RAY_AMOUNT) * self.width))

            h = self.height / \
                (dist *
                 cos((angle - self.player["angle"]) * pi / 180)) * self.wallheight
            startY = int(halfHeight - h/2)

            tex = wallTextures[id]
            tex = pygame.transform.scale(
                tex, (tex.get_width() * rayWidth, int(h)))
            tx = int(tx * tex.get_width())
            self.screen.blit(tex, (startX, startY),
                             (tx, 0, rayWidth, tex.get_height()))

        for enemy in enemies:
            self.drawSprite(enemy, 35)

        self.drawMinimap()


buttons = pygame.sprite.Group()


class Button(pygame.sprite.Sprite):
    def __init__(self, position, text, size, colorB=pygame.Color('white'), colorT=pygame.Color('black'), hoverColor=pygame.Color('red'), borderc=(255, 255, 255), command=lambda: print("No command activated for this button")):
        super().__init__()
        self.text = text
        self.colorB = colorB
        self.colorT = colorT
        self.colorOrig = colorB
        self.hoverColor = hoverColor
        self.borderc = borderc
        self.font = pygame.font.SysFont("Arial", size)
        self.render()
        self.x, self.y, self.w, self.h = self.text_render.get_rect()
        self.x, self.y = position
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.position = position
        buttons.add(self)
        self.pressed = 1
        self.command = command

    def render(self):
        self.text_render = self.font.render(self.text, 1, self.colorT)
        self.image = self.text_render

    def update(self):
        self.draw_button()
        self.hover()
        self.click()

    def draw_button(self):
        pygame.draw.rect(screen, self.colorB,
                         (self.x, self.y, self.w, self.h))
        pygame.gfxdraw.rectangle(
            screen, (self.x, self.y, self.w, self.h), self.borderc)

    def hover(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.colorB = self.hoverColor
        else:
            self.colorB = self.colorOrig

        self.render()

    def click(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0] and self.pressed == 1:
                self.command()
                self.pressed = 0
            if pygame.mouse.get_pressed() == (0, 0, 0):
                self.pressed = 1


def displayMessage(message, color, position, size):
    font2 = pygame.font.SysFont("Arial", size)
    texto = font2.render(message, 1, color)
    screen.blit(texto, position)


width = 500
height = 500

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode(
    (width, height), pygame.DOUBLEBUF | pygame.HWACCEL)
screen.set_alpha(None)

rCaster = Raycaster(screen)
rCaster.load_map("map2.txt")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 25)


def updateFPS():
    fps = str(int(clock.get_fps()))
    fps = font.render(fps, 1, pygame.Color("white"))
    return fps


introMenu = True
isRunning = True
isPaused = False


def start():
    global introMenu
    introMenu = False
    pygame.mixer.music.stop()
    return introMenu


def end():
    global introMenu
    global isRunning
    global isPaused
    isRunning = False
    introMenu = False
    isPaused = False
    return isRunning, introMenu


def resume():
    global isPaused
    isPaused = False


def pause():
    global introMenu
    global isRunning
    global isPaused
    buttons.empty()
    b0 = Button((165, 200), 'Continue', 50,
                hoverColor=pygame.Color('green'), command=resume)
    b1 = Button((210, 300), 'Quit', 50,
                hoverColor=pygame.Color('red'), command=end)
    while isPaused:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                isRunning = False
                introMenu = False
                isPaused = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    isRunning = True
                    isPaused = False
                elif ev.key == pygame.K_RETURN:
                    introMenu = False

        screen.fill(pygame.Color("black"))

        displayMessage("Game Paused", pygame.Color(
            'white'), (55, 30), 72)

        buttons.update()
        buttons.draw(screen)

        screen.fill(pygame.Color("black"), (0, 0, 30, 30))
        screen.blit(updateFPS(), (0, 0))
        clock.tick(60)

        pygame.display.flip()
        pygame.display.update()


music = pygame.mixer.music.load("Sounds/track02.ogg")

# Menu introduccion
picture = pygame.image.load('./Assets/QuakeB.jpg').convert()
picture = pygame.transform.scale(picture, (width, height))


b0 = Button((190, 350), 'Start Game', 30,
            hoverColor=pygame.Color('brown'), command=start)
b1 = Button((230, 400), 'Quit', 30,
            hoverColor=pygame.Color('brown'), command=end)

pygame.mixer.music.play(-1)
while introMenu:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            isRunning = False
            introMenu = False
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                isRunning = False
                introMenu = False
            elif ev.key == pygame.K_RETURN:
                introMenu = False

    screen.blit(picture, [0, 0])

    displayMessage("Quake Pygame Version", pygame.Color(
        'white'), (15, 100), 54)
    displayMessage("Bienvenido a la recrecion del primer Quake", pygame.Color(
        'white'), (30, 250), 28)
    displayMessage("Presiona la tecla ENTER para iniciar o", pygame.Color(
        'white'), (70, 300), 25)

    buttons.update()
    buttons.draw(screen)

    screen.fill(pygame.Color("black"), (0, 0, 30, 30))
    screen.blit(updateFPS(), (0, 0))
    clock.tick(60)

    pygame.display.flip()
    pygame.display.update()


hRes = 60
halfVRes = 50
mod = hRes/rCaster.player['fov']
posx, posy, rot = rCaster.player['x'], rCaster.player['y'], rCaster.player['angle']

frame = np.random.uniform(0, 1, (hRes, halfVRes*2, 3))
sky = pygame.image.load('./Assets/skybox.jpg')
sky = pygame.surfarray.array3d(pygame.transform.scale(sky, (360, halfVRes*2)))
floor = pygame.surfarray.array3d(pygame.image.load('./Assets/floor.jpg'))/255


@njit()
def new_frame(posx, posy, rot, frame, sky, floor, hres, halfvres, mod):
    for i in range(hres):
        rot_i = rot + np.deg2rad(i/mod - 30)
        sin, cos, cos2 = np.sin(rot_i), np.cos(
            rot_i), np.cos(np.deg2rad(i/mod - 30))
        frame[i][:] = sky[int(np.rad2deg(rot_i) % 360)][:]/255
        for j in range(halfvres):
            n = (halfvres/(halfvres-j))/cos2
            x, y = posx + cos*n, posy + sin*n
            xx, yy = int(x*2 % 1*99), int(y*2 % 1*99)

            shade = 0.2 + 0.8*(1-j/halfvres)

            frame[i][halfvres*2-j-1] = shade*floor[xx][yy]

    return frame


# Juego
lastTime = 0

while isRunning:

    screen.fill(pygame.Color("gray"))
    keys = pygame.key.get_pressed()

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            isRunning = False

        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                isPaused = True
                pause()

    t = pygame.time.get_ticks()
    deltaTime = (t - lastTime) / 1000
    lastTime = t

    newX = rCaster.player['x']
    newY = rCaster.player['y']
    forward = rCaster.player['angle'] * pi / 180
    right = (rCaster.player['angle'] + 90) * pi / 180

    if keys[pygame.K_w]:
        newX += cos(forward) * rCaster.stepSize * deltaTime * 10
        newY += sin(forward) * rCaster.stepSize * deltaTime * 10
    elif keys[pygame.K_s]:
        newX -= cos(forward) * rCaster.stepSize * deltaTime * 10
        newY -= sin(forward) * rCaster.stepSize * deltaTime * 10
    elif keys[pygame.K_a]:
        newX -= cos(right) * rCaster.stepSize * deltaTime * 10
        newY -= sin(right) * rCaster.stepSize * deltaTime * 10
    elif keys[pygame.K_d]:
        newX += cos(right) * rCaster.stepSize * deltaTime * 10
        newY += sin(right) * rCaster.stepSize * deltaTime * 10
    elif keys[pygame.K_q]:
        rCaster.player['angle'] -= rCaster.turnSize * deltaTime * 10
    elif keys[pygame.K_e]:
        rCaster.player['angle'] += rCaster.turnSize * deltaTime * 10

    i = int(newX/rCaster.blocksize)
    j = int(newY/rCaster.blocksize)

    if rCaster.map[j][i] == ' ':
        rCaster.player['x'] = newX
        rCaster.player['y'] = newY

    frame = new_frame(rCaster.player['x'], rCaster.player['y'],
                      rCaster.player['angle'], frame, sky, floor, hRes, halfVRes, mod)

    surf = pygame.surfarray.make_surface(frame*255)
    surf = pygame.transform.scale(surf, (width, height))

    screen.blit(surf, (0, 0))

    # # Techo
    # screen.fill(pygame.Color("saddlebrown"), (0, 0,  width, int(height / 2)))

    # # Piso
    # screen.fill(pygame.Color("dimgray"),
    #             (0, int(height / 2),  width, int(height / 2)))

    rCaster.render()

    # FPS
    screen.fill(pygame.Color("black"), (0, 0, 30, 30))
    screen.blit(updateFPS(), (0, 0))
    clock.tick(200)

    pygame.display.flip()


pygame.quit()
