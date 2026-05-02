import pygame
from collections import deque



BRUSH_SIZES = {1: 2, 2: 5, 3: 10}   



def draw_pencil(surface, prev_pos, curr_pos, color, size):
    """Draw a freehand stroke segment."""
    if prev_pos:
        pygame.draw.line(surface, color, prev_pos, curr_pos, size)
    else:
        pygame.draw.circle(surface, color, curr_pos, size // 2)


def draw_line(surface, start, end, color, size):
    """Draw a straight line."""
    pygame.draw.line(surface, color, start, end, size)


def draw_rectangle(surface, start, end, color, size):
    """Draw a rectangle outline."""
    x = min(start[0], end[0])
    y = min(start[1], end[1])
    w = abs(end[0] - start[0])
    h = abs(end[1] - start[1])
    pygame.draw.rect(surface, color, (x, y, w, h), size)


def draw_circle(surface, start, end, color, size):
    """Draw a circle outline whose diameter spans start→end."""
    cx = (start[0] + end[0]) // 2
    cy = (start[1] + end[1]) // 2
    r  = max(1, int(((end[0]-start[0])**2 + (end[1]-start[1])**2)**0.5 // 2))
    pygame.draw.circle(surface, color, (cx, cy), r, size)


def draw_square(surface, start, end, color, size):
    """Draw a square (equal sides)."""
    side = max(abs(end[0]-start[0]), abs(end[1]-start[1]))
    sx   = start[0] if end[0] >= start[0] else start[0] - side
    sy   = start[1] if end[1] >= start[1] else start[1] - side
    pygame.draw.rect(surface, color, (sx, sy, side, side), size)


def draw_right_triangle(surface, start, end, color, size):
    """Right-angle triangle: right-angle at start."""
    p1 = start
    p2 = (end[0],   start[1])
    p3 = (end[0],   end[1])
    pygame.draw.polygon(surface, color, [p1, p2, p3], size)


def draw_equilateral_triangle(surface, start, end, color, size):
    """Equilateral triangle above the base line start→end."""
    import math
    base = end[0] - start[0]
    h    = int(abs(base) * math.sqrt(3) / 2)
    p1   = start
    p2   = end
    p3   = ((start[0]+end[0])//2, start[1] - h)
    pygame.draw.polygon(surface, color, [p1, p2, p3], size)


def draw_rhombus(surface, start, end, color, size):
    """Rhombus whose bounding box is start→end."""
    x0, y0 = min(start[0],end[0]), min(start[1],end[1])
    x1, y1 = max(start[0],end[0]), max(start[1],end[1])
    cx = (x0+x1)//2
    cy = (y0+y1)//2
    pts = [(cx,y0),(x1,cy),(cx,y1),(x0,cy)]
    pygame.draw.polygon(surface, color, pts, size)


def draw_eraser(surface, pos, bg_color, size):
    """Erase with a square rubber."""
    r = size * 4
    pygame.draw.rect(surface, bg_color, (pos[0]-r//2, pos[1]-r//2, r, r))



def flood_fill(surface, pos, fill_color):
    """BFS flood-fill starting at pos with fill_color."""
    x, y = pos
    w, h = surface.get_size()
    if not (0 <= x < w and 0 <= y < h):
        return

    target = surface.get_at((x, y))[:3]
    fill   = fill_color[:3] if len(fill_color) == 4 else fill_color

    if target == fill:
        return

    visited = set()
    queue   = deque([(x, y)])

    while queue:
        cx, cy = queue.popleft()
        if (cx, cy) in visited:
            continue
        if not (0 <= cx < w and 0 <= cy < h):
            continue
        if surface.get_at((cx, cy))[:3] != target:
            continue

        surface.set_at((cx, cy), fill)
        visited.add((cx, cy))

        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx, ny = cx+dx, cy+dy
            if (nx, ny) not in visited:
                queue.append((nx, ny))