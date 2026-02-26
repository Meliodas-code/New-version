import pygame
import sys
import math

pygame.init()  # Inicia todos los módulos de pygame

# ===============================
# CONFIG
# ===============================

WIDTH, HEIGHT = 960, 640  
FPS = 60  
TILE_W = 64   # Ancho en pixeles de cada tile 
TILE_H = 32   # Alto en pixeles de cada tile
MAP_W = 20  # Ancho del mapa
MAP_H = 20  # Alto del mapa

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Isometria Game")
clock = pygame.time.Clock()  # Controla la velocidad del juego

sheet = pygame.image.load("assets/player.png").convert_alpha()
FRAME = 64  # Tamaño de cada frame del sprite

# Función para dividir el sprite sheet en imágenes individuales
def load_frames(sheet, size):
    frames = []
    rows = sheet.get_height() // size  # Cuántas filas tiene
    cols = sheet.get_width() // size   # Cuántas columnas tiene

    for y in range(rows):
        row = []
        for x in range(cols):
            rect = pygame.Rect(x*size, y*size, size, size)
            img = pygame.Surface((size, size), pygame.SRCALPHA)
            img.blit(sheet, (0, 0), rect)  # Recorta la parte correspondiente
            row.append(img)
        frames.append(row)

    return frames

frames = load_frames(sheet, FRAME)

# ia

# Convierte coordenadas normales a coordenadas isométricas
def world_to_iso(x, y):
    iso_x = (x - y) * (TILE_W // 2)
    iso_y = (x + y) * (TILE_H // 2)
    return iso_x, iso_y
#==============================

# clase jugador


class Player:
    def __init__(self):
        # Posición inicial (centro del mapa)
        self.x = MAP_W / 2
        self.y = MAP_H / 2

        self.speed = 0.1  # Velocidad de movimiento

        self.dir = 0      # Dirección actual (0: abajo, 1: izquierda, 2: derecha, 3: arriba)
        self.frame = 0    # Frame actual de animación
        self.anim_timer = 0  # Temporizador para animacion

        self.falling = False
        self.fall_offset = 0
        self.fall_speed = 200

        self.last_key = None  # Guarda la última tecla pulsada

    def update(self, dt, keys, events):

        # si cae = anim de caida
        if self.falling:
            self.fall_offset += self.fall_speed * dt
            return

        move_x = 0
        move_y = 0

        # Detecta cual fue la ultima tecla presionada porque para las animaciones use que mire hacia la ultima tecla presionada porque hay varias combinaciones de teclas 
        # y no se cual es la mejor forma de detectar hacia donde se esta moviendo el jugador, entonces lo que hice fue guardar la ultima tecla presionada y usar eso para determinar hacia donde mira el jugador, aunque no se si es la mejor forma de hacerlo
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d):
                    self.last_key = event.key

        # Movimiento adaptado al sistema isometrico
        if keys[pygame.K_w]:
            move_x -= 1
            move_y -= 1
        if keys[pygame.K_s]:
            move_x += 1
            move_y += 1
        if keys[pygame.K_a]:
            move_x -= 1
            move_y += 1
        if keys[pygame.K_d]:
            move_x += 1
            move_y -= 1

        # si esta quieto = frame inicial
        if move_x == 0 and move_y == 0:
            self.frame = 0
            return

        # Normaliza el movimiento para que no vaya más rápido en diagonal
        length = math.hypot(move_x, move_y)
        move_x /= length
        move_y /= length

        # Actualiza posición
        self.x += move_x * self.speed
        self.y += move_y * self.speed

        # Cambia la dirección según la última tecla pulsada
        if self.last_key == pygame.K_w:
            self.dir = 3
        elif self.last_key == pygame.K_s:
            self.dir = 0
        elif self.last_key == pygame.K_a:
            self.dir = 1
        elif self.last_key == pygame.K_d:
            self.dir = 2

        # Controla la animación
        self.anim_timer += dt
        if self.anim_timer > 0.12:
            self.frame = (self.frame + 1) % 4
            self.anim_timer = 0

        # Si sale del mapa, empieza a caer
        if self.x < 0 or self.y < 0 or self.x > MAP_W or self.y > MAP_H:
            self.falling = True



# CAMARA

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0

    # La camara sigue al jugador o eso deberia hacer :/
    def update(self, target):
        iso_x, iso_y = world_to_iso(target.x, target.y)
        self.x = iso_x
        self.y = iso_y




# Dibuja un tile en forma de rombo
def draw_tile(surface, x, y):
    points = [
        (x, y - TILE_H//2),
        (x + TILE_W//2, y),
        (x, y + TILE_H//2),
        (x - TILE_W//2, y)
    ]
    pygame.draw.polygon(surface, (70,120,70), points)
    pygame.draw.polygon(surface, (40,80,40), points, 1)




player = Player()
camera = Camera()
font = pygame.font.SysFont(None, 72)


# while principal del juego


while True:
    dt = clock.tick(FPS) / 1000  # Tiempo entre frames

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    player.update(dt, keys, events)
    camera.update(player)

    screen.fill((20,20,25))  # Fondo

    # Dibujar mapa completo
    for x in range(MAP_W):
        for y in range(MAP_H):
            iso_x, iso_y = world_to_iso(x, y)
            sx = iso_x - camera.x + WIDTH//2
            sy = iso_y - camera.y + HEIGHT//2
            draw_tile(screen, sx, sy)

    # Dibujar jugador
    iso_x, iso_y = world_to_iso(player.x, player.y)
    sx = iso_x - camera.x + WIDTH//2
    sy = iso_y - camera.y + HEIGHT//2

    sprite = frames[player.dir][player.frame]

    screen.blit(
        sprite,
        (sx - sprite.get_width()//2,
         sy - sprite.get_height() + TILE_H//2 + player.fall_offset)
    )

    # Mensaje si se cae
    if player.falling and player.fall_offset > 150:
        text = font.render("Te caiste", True, (255,60,60))
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 40))

    pygame.display.flip()