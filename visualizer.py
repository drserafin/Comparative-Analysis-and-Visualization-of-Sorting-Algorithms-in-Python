"""
Group Project #1: Sorting Algorithm Visualizer
--------------------------------------------------------------------------------
This module handles the visualization of sorting algorithms using Pygame.

COMPONENT OVERVIEW:

1. class DrawInformation:
   - Manages window settings (width, height), colors, and dynamic scaling.
   - Calculates the specific dimensions (block_width, block_height) for drawing bars
     based on the list size, ensuring the graph fits perfectly on screen.

2. function draw(draw_info):
   - The "Master Painter" called every frame when sorting is PAUSED.
   - Clears the screen, draws the background, renders control text (R, SPACE), 
     and calls draw_list() to paint the bars.

3. function draw_list(draw_info, clear_bg=False):
   - Converts the numerical list into visual rectangles.
   - Uses the math from DrawInformation to calculate X/Y coordinates.
   - Includes an optimization (clear_bg) to redraw only the bar area during 
     animations to ensure high performance (FPS).

4. function generate_starting_list(n, min_val, max_val):
   - Generates the random list of integers (the data) to be sorted.
   - Called during initialization and when the user resets (Key 'R').

5. function main():
   - The "Game Loop." Runs at 60 FPS.
   - Listens for User Input (Quit, Reset, Start/Pause).
   - Manages the Sorting Generator (advances the algorithm one step at a time).
   - triggers the drawing functions.
--------------------------------------------------------------------------------
"""

import pygame
import random
import math
from algorithms import bubble_sort, merge_sort

pygame.init()

class DrawInformation:
    BLACK = 0, 0, 0
    WHITE = 255, 255, 255
    GREEN = 0, 255, 0
    RED = 255, 0, 0
    GREY = 128, 128, 128  # Added Grey for potential use
    BACKGROUND_COLOR = (100, 149, 237) # Cornflower Blue

    SORTING_BG_COLOR = (50,50,50)

    SIDE_PAD = 100
    TOP_PAD = 150

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
        val_range = (self.max_val - self.min_val) if (self.max_val - self.min_val) > 0 else 1
        self.block_height = math.floor((self.height - self.TOP_PAD) / val_range)
        self.start_x = self.SIDE_PAD // 2


def draw(draw_info, algo_name):
    draw_info.window.fill(draw_info.BACKGROUND_COLOR)

    # 1. Render the Algorithm Name (Large and Centered)
    title_font = pygame.font.SysFont('comicsans', 40) # Larger font
    title = title_font.render(f"{algo_name}", 1, draw_info.BLACK) # Black text
    draw_info.window.blit(title, (draw_info.width/2 - title.get_width()/2, 5))

    # 2. Render the Controls (Smaller and below title)
    controls_font = pygame.font.SysFont('comicsans', 20)
    controls = controls_font.render("R - Reset | SPACE - Start/Pause", 1, draw_info.BLACK)
    draw_info.window.blit(controls, (draw_info.width/2 - controls.get_width()/2, 45))
    
    # 3. Render the Algorithm Selectors
    sorting_font = pygame.font.SysFont('comicsans', 20)
    sorting = sorting_font.render("B - Bubble Sort | M - Merge Sort", 1, draw_info.BLACK)
    draw_info.window.blit(sorting, (draw_info.width/2 - sorting.get_width()/2, 75))

    draw_list(draw_info)
    pygame.display.update()


def draw_list(draw_info, clear_bg=False):
    lst = draw_info.lst

    # 1. Define the Box Area
    sorting_area_rect = (
        draw_info.SIDE_PAD // 2,        # X
        draw_info.TOP_PAD,              # Y
        draw_info.width - draw_info.SIDE_PAD, # Width
        draw_info.height - draw_info.TOP_PAD  # Height
    )

    # 2. Draw the Background Color (The "Eraser")
    # This fills the box with Grey/Black to wipe away old bars
    pygame.draw.rect(draw_info.window, draw_info.SORTING_BG_COLOR, sorting_area_rect)

    if clear_bg:
        pass

    # 3. Draw the Bars
    for i, val in enumerate(lst):
        GAP = 2 
        x = draw_info.start_x + i * draw_info.block_width
        
        bar_width = max(1, draw_info.block_width - GAP)
        bar_height = (val - draw_info.min_val) * draw_info.block_height
        y = draw_info.height - bar_height

        color = draw_info.WHITE

        # Draw the bar
        pygame.draw.rect(draw_info.window, color, (x, y, bar_width, bar_height))

    # 4. Draw the Border (ONCE, after the loop finishes)
    pygame.draw.rect(draw_info.window, draw_info.BLACK, sorting_area_rect, 3)

    # 5. Update the Display (Crucial for animation!)
    if clear_bg:
        pygame.display.update()


def generate_starting_list(n, min_val, max_val):
    lst = []
    for _ in range(n):
        val = random.randint(min_val, max_val)
        lst.append(val)
    return lst


def main():
    run = True
    clock = pygame.time.Clock()

    n = 30
    min_val = 0
    max_val = 100

    lst = generate_starting_list(n, min_val, max_val)
    draw_info = DrawInformation(800, 600, lst)

    sorting = False
    sorting_algorithm = bubble_sort
    sorting_algo_name = "Bubble Sort"
    sorting_algorithm_generator = None

    while run:
        clock.tick(60)

        if sorting:
            try:
                # Advance the algorithm by one step
                next(sorting_algorithm_generator)
                draw_list(draw_info, clear_bg=True)
            except StopIteration:
                sorting = False
        else:
            draw(draw_info, sorting_algo_name)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                # R - Reset
                if event.key == pygame.K_r:
                    lst = generate_starting_list(n, min_val, max_val)
                    draw_info.set_list(lst)
                    sorting = False
                    sorting_algorithm_generator = None # <--- THIS IS THE FIX
                
                # SPACE - Start / Pause
                elif event.key == pygame.K_SPACE:
                    if sorting:
                        sorting = False
                    else:
                        sorting = True
                        # If we just started (or reset), create the generator
                        if sorting_algorithm_generator is None:
                            sorting_algorithm_generator = sorting_algorithm(draw_info.lst)

                # B - Select Bubble Sort
                elif event.key == pygame.K_b:
                    sorting = False
                    sorting_algorithm = bubble_sort
                    sorting_algo_name = "Bubble Sort"
                    sorting_algorithm_generator = None 
                    pygame.display.set_caption(f"Sorting Visualizer - {sorting_algo_name}")

                # M - Select Merge Sort
                elif event.key == pygame.K_m:
                    sorting = False
                    sorting_algorithm = merge_sort
                    sorting_algo_name = "Merge Sort"
                    sorting_algorithm_generator = None 
                    pygame.display.set_caption(f"Sorting Visualizer - {sorting_algo_name}")

    pygame.quit()

if __name__ == "__main__":
    main()