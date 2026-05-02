import pygame
import sys
from datetime import datetime
from tools import (
    BRUSH_SIZES,
    draw_pencil, draw_line,
    draw_rectangle, draw_circle,
    draw_square, draw_right_triangle,
    draw_equilateral_triangle, draw_rhombus,
    draw_eraser, flood_fill,
)

SCREEN_W, SCREEN_H = 1100, 700
TOOLBAR_W          = 180
CANVAS_X           = TOOLBAR_W
CANVAS_W           = SCREEN_W - TOOLBAR_W
CANVAS_H           = SCREEN_H

BG_COLOR     = (245, 245, 245)
TOOLBAR_BG   = (30,  30,  40)
WHITE        = (255, 255, 255)
BLACK        = (0,   0,   0)
ACCENT       = (100, 180, 255)
PREVIEW_ALPHA= 120

PALETTE = [
    (0,0,0),(255,255,255),(200,50,50),(50,180,50),
    (50,80,220),(255,200,0),(200,100,0),(160,0,200),
    (0,200,200),(255,120,180),(100,100,100),(200,200,200),
]

TOOLS = [
    "pencil","line","rectangle","circle",
    "square","right_triangle","equil_triangle","rhombus",
    "eraser","fill","text",
]

TOOL_LABELS = {
    "pencil":          "✏ Pencil",
    "line":            "/ Line",
    "rectangle":       "▭ Rect",
    "circle":          "○ Circle",
    "square":          "□ Square",
    "right_triangle":  "◺ R-Tri",
    "equil_triangle":  "△ E-Tri",
    "rhombus":         "◇ Rhombus",
    "eraser":          "◻ Eraser",
    "fill":            "🪣 Fill",
    "text":            "T  Text",
}



def draw_button(surf, rect, label, active, font):
    color  = ACCENT if active else (60, 60, 80)
    border = WHITE  if active else (90, 90, 110)
    pygame.draw.rect(surf, color, rect, border_radius=6)
    pygame.draw.rect(surf, border, rect, 1, border_radius=6)
    txt = font.render(label, True, WHITE)
    surf.blit(txt, txt.get_rect(center=rect.center))


def draw_toolbar(surf, state, font_sm, font_xs):
    surf.fill(TOOLBAR_BG, (0, 0, TOOLBAR_W, SCREEN_H))
    pygame.draw.line(surf, (70, 70, 90), (TOOLBAR_W-1, 0), (TOOLBAR_W-1, SCREEN_H))


    t = font_sm.render("🎨 Paint", True, ACCENT)
    surf.blit(t, (10, 8))


    y = 40
    for tool in TOOLS:
        r = pygame.Rect(8, y, TOOLBAR_W-16, 26)
        draw_button(surf, r, TOOL_LABELS[tool], state["tool"] == tool, font_xs)
        state["tool_rects"][tool] = r
        y += 30

    
    y += 6
    lbl = font_xs.render("Brush size (1/2/3):", True, (180,180,180))
    surf.blit(lbl, (8, y));  y += 16
    for k, px in BRUSH_SIZES.items():
        r = pygame.Rect(8 + (k-1)*54, y, 50, 22)
        draw_button(surf, r, f"{k} ({px}px)", state["brush_key"] == k, font_xs)
        state["size_rects"][k] = r
    y += 28

    
    y += 6
    lbl = font_xs.render("Color:", True, (180,180,180))
    surf.blit(lbl, (8, y));  y += 16
    for i, col in enumerate(PALETTE):
        col_r = pygame.Rect(8 + (i%4)*40, y + (i//4)*34, 34, 28)
        pygame.draw.rect(surf, col, col_r, border_radius=4)
        if col == state["color"]:
            pygame.draw.rect(surf, WHITE, col_r, 2, border_radius=4)
        state["palette_rects"][i] = col_r
    y += (len(PALETTE)//4)*34 + 8

    
    swatch = pygame.Rect(8, y, TOOLBAR_W-16, 28)
    pygame.draw.rect(surf, state["color"], swatch, border_radius=5)
    pygame.draw.rect(surf, WHITE, swatch, 1, border_radius=5)
    y += 34

    
    hint = font_xs.render("Ctrl+S = Save PNG", True, (120,120,140))
    surf.blit(hint, (8, SCREEN_H - 22))



def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("TSIS 2 — Paint")

    font_sm = pygame.font.SysFont("segoeui", 15, bold=True)
    font_xs = pygame.font.SysFont("segoeui", 12)
    font_txt= pygame.font.SysFont("segoeui", 22)  

    
    canvas = pygame.Surface((CANVAS_W, CANVAS_H))
    canvas.fill(WHITE)

    state = {
        "tool":         "pencil",
        "brush_key":    2,
        "color":        BLACK,
        "tool_rects":   {},
        "size_rects":   {},
        "palette_rects":{},
    }

   
    drawing      = False
    prev_pos     = None
    drag_start   = None   
    preview_surf = None   

    
    text_active  = False
    text_pos     = None
    text_buf     = ""

    clock = pygame.time.Clock()

    def canvas_pos(mx, my):
        return (mx - CANVAS_X, my)

    def brush_size():
        return BRUSH_SIZES[state["brush_key"]]

    def commit_shape(tmp_canvas, start, end):
        """Draw the chosen shape onto tmp_canvas."""
        t   = state["tool"]
        col = state["color"]
        sz  = brush_size()
        if   t == "line":           draw_line(tmp_canvas, start, end, col, sz)
        elif t == "rectangle":      draw_rectangle(tmp_canvas, start, end, col, sz)
        elif t == "circle":         draw_circle(tmp_canvas, start, end, col, sz)
        elif t == "square":         draw_square(tmp_canvas, start, end, col, sz)
        elif t == "right_triangle": draw_right_triangle(tmp_canvas, start, end, col, sz)
        elif t == "equil_triangle": draw_equilateral_triangle(tmp_canvas, start, end, col, sz)
        elif t == "rhombus":        draw_rhombus(tmp_canvas, start, end, col, sz)

    SHAPE_TOOLS = {"line","rectangle","circle","square",
                   "right_triangle","equil_triangle","rhombus"}

    running = True
    while running:
        clock.tick(60)

        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            
            elif event.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()

               
                if event.key == pygame.K_s and (mods & pygame.KMOD_CTRL):
                    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
                    name = f"canvas_{ts}.png"
                    pygame.image.save(canvas, name)
                    print(f"[Saved] {name}")
                    continue

                
                if event.key in (pygame.K_1, pygame.K_2, pygame.K_3) and not text_active:
                    state["brush_key"] = int(event.unicode)

                
                if text_active:
                    if event.key == pygame.K_RETURN:
                        
                        rendered = font_txt.render(text_buf, True, state["color"])
                        canvas.blit(rendered, text_pos)
                        text_active = False
                        text_buf    = ""
                        text_pos    = None
                    elif event.key == pygame.K_ESCAPE:
                        text_active = False
                        text_buf    = ""
                        text_pos    = None
                    elif event.key == pygame.K_BACKSPACE:
                        text_buf = text_buf[:-1]
                    else:
                        if event.unicode and event.unicode.isprintable():
                            text_buf += event.unicode

            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                
                if mx < TOOLBAR_W:
                    for tool, r in state["tool_rects"].items():
                        if r.collidepoint(mx, my):
                            state["tool"] = tool
                            text_active   = False
                            text_buf      = ""
                    for k, r in state["size_rects"].items():
                        if r.collidepoint(mx, my):
                            state["brush_key"] = k
                    for i, r in state["palette_rects"].items():
                        if r.collidepoint(mx, my):
                            state["color"] = PALETTE[i]
                    continue

                
                cx, cy = canvas_pos(mx, my)
                tool   = state["tool"]

                if tool == "fill":
                    flood_fill(canvas, (cx, cy), state["color"])

                elif tool == "text":
                    text_active = True
                    text_pos    = (cx, cy)
                    text_buf    = ""

                elif tool in SHAPE_TOOLS:
                    drawing    = True
                    drag_start = (cx, cy)
                    preview_surf = canvas.copy()  
                elif tool == "pencil":
                    drawing  = True
                    prev_pos = (cx, cy)
                    draw_pencil(canvas, None, (cx, cy), state["color"], brush_size())

                elif tool == "eraser":
                    drawing  = True
                    prev_pos = (cx, cy)
                    draw_eraser(canvas, (cx, cy), WHITE, brush_size())

            
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if drawing and drag_start and state["tool"] in SHAPE_TOOLS:
                    mx, my = event.pos
                    cx, cy = canvas_pos(mx, my)
                    commit_shape(canvas, drag_start, (cx, cy))
                drawing      = False
                prev_pos     = None
                drag_start   = None
                preview_surf = None

            
            elif event.type == pygame.MOUSEMOTION:
                if not drawing:
                    continue
                mx, my = event.pos
                if mx < TOOLBAR_W:
                    continue
                cx, cy = canvas_pos(mx, my)
                tool   = state["tool"]

                if tool == "pencil":
                    draw_pencil(canvas, prev_pos, (cx, cy), state["color"], brush_size())
                    prev_pos = (cx, cy)

                elif tool == "eraser":
                    draw_eraser(canvas, (cx, cy), WHITE, brush_size())
                    prev_pos = (cx, cy)

                
                elif tool in SHAPE_TOOLS and drag_start and preview_surf:
                    canvas.blit(preview_surf, (0, 0))   # restore clean snapshot
                    commit_shape(canvas, drag_start, (cx, cy))

        
        screen.fill(BG_COLOR)
        screen.blit(canvas, (CANVAS_X, 0))

        
        if text_active and text_pos:
            rendered = font_txt.render(text_buf + "|", True, state["color"])
            screen.blit(rendered, (CANVAS_X + text_pos[0], text_pos[1]))

        draw_toolbar(screen, state, font_sm, font_xs)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()