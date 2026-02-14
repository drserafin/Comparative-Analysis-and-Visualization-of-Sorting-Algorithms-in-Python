import pygame
import random
import math
from algorithms import bubble_sort, merge_sort, quick_sort, radix_sort, linear_search_wrapper

pygame.init()

# -----------------------------------------------------------------------------
# CLASS: DrawInformation
# Manages window settings (width, height), colors, and dynamic scaling.
# -----------------------------------------------------------------------------
class DrawInformation:
    BLACK = 0, 0, 0
    WHITE = 255, 255, 255
    GREEN = 0, 255, 0
    RED = 255, 0, 0
    GREY = 128, 128, 128
    BAR_COLOR = (0, 150, 136)       # Teal/Green like the reference
    BAR_BORDER = (0, 100, 90)       # Darker teal for border
    ACTIVE_COLOR = (255, 100, 100)  # Reddish for active bars
    
    BACKGROUND_COLOR = (15, 23, 42) # Dark Navy/Black background
    SORTING_BG_COLOR = (5, 8, 20) # Match background (Dark Navy)

    SIDE_PAD = 100
    TOP_PAD = 150

    # Fonts
    FONT = pygame.font.SysFont('comicsans', 20)
    LARGE_FONT = pygame.font.SysFont('comicsans', 30)

    def __init__(self, width, height, lst):
        self.width = width
        self.height = height

        self.window = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Sorting Algorithm Visualizer")

        self.set_list(lst)

    def set_list(self, lst):
        self.lst = lst
        self.min_val = min(lst)
        self.max_val = max(lst)

        self.block_width = round((self.width - self.SIDE_PAD) / len(lst))
        # Determine height scale factor
        val_range = (self.max_val - self.min_val) if (self.max_val - self.min_val) > 0 else 1
        self.block_height = math.floor((self.height - self.TOP_PAD) / val_range)
        self.start_x = self.SIDE_PAD // 2

# -----------------------------------------------------------------------------
# FUNCTION: draw
# The "Master Painter". Draws text, background, and calls draw_list.
# -----------------------------------------------------------------------------
def draw(draw_info, algo_name):
    draw_info.window.fill(draw_info.BACKGROUND_COLOR)

    # 1. Render Algorithm Name
    title = draw_info.LARGE_FONT.render(f"{algo_name}", 1, draw_info.WHITE)
    draw_info.window.blit(title, (draw_info.width/2 - title.get_width()/2, 5))

    # 2. Render Controls
    controls = draw_info.FONT.render("R - Reset | SPACE - Start/Pause", 1, draw_info.GREY)
    draw_info.window.blit(controls, (draw_info.width/2 - controls.get_width()/2, 45))

    # 3. Render Algorithm Choices
    sorting = draw_info.FONT.render("B:Bubble | M:Merge | Q:Quick | X:Radix | L:Linear", 1, draw_info.GREY)
    draw_info.window.blit(sorting, (draw_info.width/2 - sorting.get_width()/2, 75))

    draw_list(draw_info)
    pygame.display.update()

# -----------------------------------------------------------------------------
# FUNCTION: draw_list
# UPDATED: Draws rounded bars with borders
# -----------------------------------------------------------------------------
def draw_list(draw_info, color_positions={}, clear_bg=False):
    lst = draw_info.lst

    # Define the area where bars are drawn
    sorting_area_rect = (
        draw_info.SIDE_PAD // 2,
        draw_info.TOP_PAD,
        draw_info.width - draw_info.SIDE_PAD,
        draw_info.height - draw_info.TOP_PAD
    )

    # 1. ALWAYS draw the background box first
    pygame.draw.rect(draw_info.window, draw_info.SORTING_BG_COLOR, sorting_area_rect)

    if clear_bg:
        pass

    for i, val in enumerate(lst):
        x = draw_info.start_x + i * draw_info.block_width
        y = draw_info.height - (val - draw_info.min_val) * draw_info.block_height
        
        # Calculate height extending to bottom
        bar_height = draw_info.height - y

        # Default Color
        color = draw_info.BAR_COLOR
        border_color = draw_info.BAR_BORDER

        # Highlight active bars
        if i in color_positions:
            color = color_positions[i]
            border_color = (255, 255, 255) # White border for active bars

        # 1. Draw the Main Bar (Rounded Top)
        rect_shape = (x, y, draw_info.block_width, bar_height)
        
        # Draw filled bar
        pygame.draw.rect(draw_info.window, color, rect_shape, 
                         border_top_left_radius=5, border_top_right_radius=5)
        
        # 2. Draw the Border (Thin outline)
        pygame.draw.rect(draw_info.window, border_color, rect_shape, width=1,
                         border_top_left_radius=5, border_top_right_radius=5)

    # Draw border around the entire graph area
    pygame.draw.rect(draw_info.window, draw_info.GREY, sorting_area_rect, 1)

    if clear_bg:
        pygame.display.update()

# -----------------------------------------------------------------------------
# FUNCTION: generate_starting_list
# -----------------------------------------------------------------------------
def generate_starting_list(n, min_val, max_val):
    lst = []
    for _ in range(n):
        val = random.randint(min_val, max_val)
        lst.append(val)
    return lst

# -----------------------------------------------------------------------------
# MAIN LOOP
# -----------------------------------------------------------------------------
def main():
    run = True
    clock = pygame.time.Clock()

    n = 50
    min_val = 0
    max_val = 100

    lst = generate_starting_list(n, min_val, max_val)
    draw_info = DrawInformation(1000, 700, lst)

    sorting = False
    paused = False 

    # Defaults
    sorting_algorithm = bubble_sort
    sorting_algo_name = "Bubble Sort"
    sorting_algorithm_generator = None

    while run:
        clock.tick(60) 

        if sorting:
            try:
                row, color_indices = next(sorting_algorithm_generator)
                color_positions = {idx: draw_info.ACTIVE_COLOR for idx in color_indices}  
                draw_list(draw_info, color_positions, clear_bg=True)
            except StopIteration:
                sorting = False
             
        else:
            draw(draw_info, sorting_algo_name)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_r:
                lst = generate_starting_list(n, min_val, max_val)
                draw_info.set_list(lst)
                sorting = False
                sorting_algorithm_generator = None

            elif event.key == pygame.K_SPACE:
                if sorting:
                    sorting = False 
                    paused = True
                elif paused:
                    sorting = True 
                    paused = False
                else:
                    sorting = True
                    sorting_algorithm_generator = sorting_algorithm(draw_info.lst)

            elif not sorting:
                if event.key == pygame.K_b:
                    sorting_algorithm = bubble_sort
                    sorting_algo_name = "Bubble Sort"
                elif event.key == pygame.K_m:
                    sorting_algorithm = merge_sort
                    sorting_algo_name = "Merge Sort"
                elif event.key == pygame.K_q:
                    sorting_algorithm = quick_sort
                    sorting_algo_name = "Quick Sort"
                elif event.key == pygame.K_x: 
                    sorting_algorithm = radix_sort
                    sorting_algo_name = "Radix Sort"
                elif event.key == pygame.K_l:
                    sorting_algorithm = linear_search_wrapper
                    sorting_algo_name = "Linear Search"
                
                pygame.display.set_caption(f"Sorting Visualizer - {sorting_algo_name}")

    pygame.quit()

if __name__ == "__main__":
    main()