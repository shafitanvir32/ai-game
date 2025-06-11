import pygame, math
from core.board import ROWS, COLS, RED, BLUE, CRITS

GAP = 4          # gap between cells
CELL = 70        # cell size
PAD  = 32
RADIUS = CELL//2 - 10

class PygameView:
    def __init__(self, title="Chain Reaction"):
        pygame.init()
        self.size = (COLS*CELL + 2*PAD, ROWS*CELL + 2*PAD + 40)
        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption(title)
        self.font = pygame.font.SysFont("arial", 16, bold=True)
        self.clock = pygame.time.Clock()

    def draw_board(self, board, turn_player, msg=""):
        self.screen.fill((30,30,30))
        # grid background
        for r in range(ROWS):
            for c in range(COLS):
                x = PAD + c*CELL
                y = PAD + r*CELL
                rect = pygame.Rect(x,y,CELL,CELL)
                pygame.draw.rect(self.screen, (50,50,50), rect, border_radius=10)
        # orbs
        for r,row in enumerate(board.grid):
            for c,cell in enumerate(row):
                if cell.owner == -1:
                    continue
                color = (200,50,50) if cell.owner==RED else (50,110,255)
                for k in range(cell.count):
                    ang = k*2*math.pi / CRITS[r][c]
                    cx = PAD+c*CELL + CELL/2 + (RADIUS-12)*math.cos(ang)
                    cy = PAD+r*CELL + CELL/2 + (RADIUS-12)*math.sin(ang)
                    pygame.draw.circle(self.screen, color, (cx,cy), 12)
        # header
        header = f"Turn: {'Red' if turn_player==RED else 'Blue'}    {msg}"
        txt = self.font.render(header, True, (240,240,240))
        self.screen.blit(txt, (10, self.size[1]-32))
        pygame.display.flip()
        self.clock.tick(60)

    def wait_click(self):
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    raise SystemExit
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    mx,my = e.pos
                    if PAD <= mx < PAD+COLS*CELL and PAD <= my < PAD+ROWS*CELL:
                        c = (mx-PAD)//CELL
                        r = (my-PAD)//CELL
                        return r,c
