import torch.nn.functional as F
import numpy as np
import pygame
pygame.font.init()
import torch
from math import floor

FPS = 60 # frames per seconds
CELL_SIZE = 1 # minimum 1, bigger goes zoomer
CHANCES = 0.5 #starting on/off chances
LIFE_CYCLE_DURATION = 1 # max life/death time in second
LIFE_CYCLE = False # will die after max life cycle duration
ZOMBIE = False # resurrect after life cycle duration?
ZOMBIE_CHANCES = 1 / 64 # chances of resurrection per life cycle
x, y = 1920, 1080 # your screen resolution

x, y = floor(x / CELL_SIZE), floor(y / CELL_SIZE)
k = torch.ones(3, 3, device="cuda")
k[1][1] = 0
k = k.view(1, 1, 3, 3)

def new_m(c):
    m = (torch.rand((y, x), device="cuda").abs() <= c).to(dtype=torch.float32)
    m = m.unsqueeze(0).unsqueeze(0)
    return m

m = new_m(CHANCES)
d = torch.zeros_like(m)
z = torch.zeros_like(m)
one = torch.tensor(1)

stays = [2]
lives = [3]

def refresh_gol(m):
    g = F.conv2d(m, k, padding=1)
    r = torch.zeros_like(m)
    stay = torch.isin(g, torch.tensor(stays, device=g.device))
    live = torch.isin(g, torch.tensor(lives, device=g.device))
    dead = ~(stay | live)
    r[stay] = m[stay]
    r[live] = 1
    r[dead] = 0
    return r

text_indent = 10
def text_to_screen(screen, text, x=32, y=0, size = 24,
            color = (0, 255, 0)):
    global text_indent
    font = pygame.font.Font(pygame.font.get_default_font(), size)
    text = font.render(text, True, color)
    screen.blit(text, (x, text_indent))
    text_indent += size + 4

CHECK_WS = 10
VISIBLE_CELL_SIZE = CELL_SIZE
screen = pygame.display.set_mode((x * VISIBLE_CELL_SIZE, y * VISIBLE_CELL_SIZE))

clock = pygame.time.Clock()
runner = 0
running = True
paused  = False
edit    = False
hide    = False
AUTO_RESTART = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mc = m.clone()
                edit = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                edit = False

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if pygame.K_KP1 <= event.key <= pygame.K_KP9:
                val = 10 + event.key - pygame.K_KP0
                if val in stays:
                    stays.remove(val)
                else:
                    stays.append(val)
                stays = sorted(stays)
            if event.key == pygame.K_KP0:
                if 0 in stays:
                    stays.remove(0)
                else:
                    stays.append(0)
                stays = sorted(stays)
            if pygame.K_1 <= event.key <= pygame.K_9:
                val = event.key - pygame.K_0
                if val in lives:
                    lives.remove(val)
                else:
                    lives.append(val)
                lives = sorted(lives)
            if event.key == pygame.K_0:
                if 0 in lives:
                    lives.remove(0)
                else:
                    lives.append(0)
                lives = sorted(lives)
            if event.key == pygame.K_ESCAPE:
                exit()
            if event.key == pygame.K_e:
                m = torch.zeros_like(m)
            if event.key == pygame.K_r:
                m = new_m(CHANCES)
            if event.key == pygame.K_f:
                LIFE_CYCLE = not LIFE_CYCLE
                print(f"LIFE CYCLE: {'ON' if LIFE_CYCLE else 'OFF'}")
                if LIFE_CYCLE:
                    d = torch.zeros_like(m)
                    z = torch.zeros_like(m)
            if event.key == pygame.K_z:
                ZOMBIE = not ZOMBIE
                if ZOMBIE:
                    z = torch.zeros_like(m)
            if event.key == pygame.K_KP_PLUS:
                CHANCES = round(min(1, CHANCES + 0.1),2)
                m = new_m(CHANCES)
            if event.key == pygame.K_KP_MINUS:
                CHANCES = round(max(0, CHANCES - 0.1),2)
                m = new_m(CHANCES)
            if event.key == pygame.K_SPACE:
                paused = not paused
            if event.key == pygame.K_h:
                hide = not hide
            if event.key == pygame.K_a:
                AUTO_RESTART = not AUTO_RESTART
    if edit:
        pos = pygame.mouse.get_pos()
        c = mc[0][0][floor(pos[1]/VISIBLE_CELL_SIZE)][floor(pos[0]/VISIBLE_CELL_SIZE)]
        m[0][0][floor(pos[1]/VISIBLE_CELL_SIZE)][floor(pos[0]/VISIBLE_CELL_SIZE)] = 1 if c == 0 else 0

    if not paused:
        m = refresh_gol(m)
        if LIFE_CYCLE:
            d = d.add(m).mul(m)
        if ZOMBIE:
            v = one.sub(m)
            z = z.add(v).mul(v)

    arr = torch.zeros_like(m)
    arr[m == 1] = 255

    arr = (arr.squeeze().detach().cpu().numpy()).astype(np.uint8)

    if runner == 0 and not paused:
        if AUTO_RESTART:
            if m.sum() == 0:
                m = new_m(CHANCES)
        if LIFE_CYCLE:
            m[d > FPS * LIFE_CYCLE_DURATION] = 0
        if ZOMBIE:
            m[z > FPS * LIFE_CYCLE_DURATION] = new_m(ZOMBIE_CHANCES / floor(FPS / CHECK_WS))[z > FPS * LIFE_CYCLE_DURATION]

    surface = pygame.surfarray.make_surface(np.stack([arr]*3, axis=-1).swapaxes(0, 1))
    surface = pygame.transform.scale(surface, (x * VISIBLE_CELL_SIZE, y * VISIBLE_CELL_SIZE))
    if not hide:
        text_to_screen(surface, f"Will live (alpha):")
        text_to_screen(surface, f"{' '.join([str(l) for l in lives])}")
        text_to_screen(surface, f"Will stay (numpad):")
        text_to_screen(surface, f"{' '.join([str(s) for s in stays])}")
        text_to_screen(surface, f"Life Cycle death (F): {'ON' if LIFE_CYCLE else 'OFF'}")
        text_to_screen(surface, f"Life Cycle resurrection (Z): {'ON' if ZOMBIE else 'OFF'}")
        text_to_screen(surface, f"Auto-restart on empty (A): {'ON' if AUTO_RESTART else 'OFF'}")
        text_to_screen(surface, f"Pause (Space): {'ON' if paused else 'OFF'}")
        text_to_screen(surface, "Random (R)")
        text_to_screen(surface, "Empty (E)")
        text_to_screen(surface, "Hide UI (H)")
        text_indent = 10
    screen.blit(surface, (0, 0))
    pygame.display.flip()
    runner = (runner + 1)%floor(FPS / CHECK_WS)
    clock.tick(FPS)

pygame.quit()