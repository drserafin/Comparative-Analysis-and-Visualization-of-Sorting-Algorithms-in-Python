import pygame
import random
import math
import time
from algorithms import bubble_sort, merge_sort, quick_sort, radix_sort, linear_search_wrapper

pygame.init()

# -----------------------------------------------------------------------------
# 1. THEME & CONFIGURATION
# -----------------------------------------------------------------------------
class Theme:
    # Colors based on your reference image
    BG_DARK       = (8, 12, 20)      # Deepest background (Main Window)
    BG_PANEL      = (15, 23, 35)     # Lighter panel (Sidebar/Graph bg)
    
    ACCENT_CYAN   = (0, 220, 255)    # Bright Cyan (Active buttons, Start button)
    ACCENT_HOVER  = (0, 180, 210)    # Slightly darker for hover
    
    TEXT_WHITE    = (240, 240, 240)
    TEXT_GREY     = (100, 115, 130)  # For labels like "ALGORITHM"
    
    BAR_DEFAULT   = (20, 160, 160)   # Teal bars
    BAR_ACTIVE    = (255, 60, 60)    # Red for active comparison
    BAR_SORTED    = (50, 205, 50)    # Green for sorted
    
    BUTTON_OUTLINE = (40, 55, 75)    # Dark grey/blue outline for inactive buttons
    
    FONT_MONO = "consolas"           # Monospaced font for the "hacker" look

# -----------------------------------------------------------------------------
# 2. UI COMPONENTS (Buttons & Sliders)
# -----------------------------------------------------------------------------
class Button:
    def __init__(self, x, y, width, height, text, font, action_key=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.action_key = action_key  # Identifier for what this button does
        self.is_active = False
        self.is_hovered = False

    def draw(self, window, is_filled=False):
        # Determine Color
        color = Theme.BUTTON_OUTLINE
        text_color = Theme.TEXT_GREY
        
        if self.is_active:
            color = Theme.ACCENT_CYAN
            text_color = Theme.BG_DARK # Dark text on bright button
        elif self.is_hovered:
            color = (60, 80, 100)
            text_color = Theme.TEXT_WHITE
            
        # Draw Background
        if self.is_active or is_filled:
            if is_filled and not self.is_active: 
                # Special case for "Start" button (always filled cyan)
                pygame.draw.rect(window, Theme.ACCENT_CYAN, self.rect, border_radius=8)
                text_color = Theme.BG_DARK
            else:
                # Active toggle button
                pygame.draw.rect(window, Theme.ACCENT_CYAN, self.rect, border_radius=8)
        else:
            # Outlined inactive button
            pygame.draw.rect(window, color, self.rect, width=1, border_radius=8)

        # Draw Text
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        window.blit(text_surf, text_rect)

    def check_click(self, pos):
        return self.rect.collidepoint(pos)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

class Slider:
    def __init__(self, x, y, width, min_val, max_val, initial_val):
        self.rect = pygame.Rect(x, y, width, 6) # Track
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.dragging = False
        
        # Handle position
        self.handle_radius = 8
        self.update_handle_pos()

    def update_handle_pos(self):
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        handle_x = self.rect.x + (self.rect.width * ratio)
        self.handle_rect = pygame.Rect(handle_x - self.handle_radius, self.rect.centery - self.handle_radius, 
                                       self.handle_radius*2, self.handle_radius*2)

    def draw(self, window):
        # Draw Track (Dark Grey)
        pygame.draw.rect(window, (40, 50, 60), self.rect, border_radius=3)
        # Draw Active Track (Cyan part on the left)
        active_track = pygame.Rect(self.rect.x, self.rect.y, self.handle_rect.centerx - self.rect.x, self.rect.height)
        pygame.draw.rect(window, Theme.ACCENT_CYAN, active_track, border_radius=3)
        # Draw Handle
        pygame.draw.circle(window, Theme.BG_DARK, self.handle_rect.center, self.handle_radius) # Inner black
        pygame.draw.circle(window, Theme.ACCENT_CYAN, self.handle_rect.center, self.handle_radius, width=2) # Ring

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        
        if self.dragging and pygame.mouse.get_pressed()[0]:
            mouse_x = pygame.mouse.get_pos()[0]
            # Clamp to track
            mouse_x = max(self.rect.left, min(mouse_x, self.rect.right))
            ratio = (mouse_x - self.rect.left) / self.rect.width
            self.value = int(self.min_val + (ratio * (self.max_val - self.min_val)))
            self.update_handle_pos()
            return True # Value changed
        return False

# -----------------------------------------------------------------------------
# 3. DRAW INFORMATION CLASS
# -----------------------------------------------------------------------------
class DrawInformation:
    def __init__(self, width, height, lst):
        self.width = width
        self.height = height
        
        self.window = pygame.display.set_mode((width, height))
        pygame.display.set_caption("SortLab - Algorithm Visualizer")

        # Layout Constants
        self.SIDEBAR_WIDTH = 280
        self.GRAPH_PAD = 30
        
        # Fonts
        self.font_sm = pygame.font.SysFont(Theme.FONT_MONO, 14)
        self.font_md = pygame.font.SysFont(Theme.FONT_MONO, 18)
        self.font_lg = pygame.font.SysFont(Theme.FONT_MONO, 24, bold=True)
        self.font_xl = pygame.font.SysFont(Theme.FONT_MONO, 32, bold=True)

        self.set_list(lst)

    def set_list(self, lst):
        self.lst = lst
        self.min_val = min(lst)
        self.max_val = max(lst)

        # Graph area is strictly to the left of the sidebar
        self.graph_width = self.width - self.SIDEBAR_WIDTH - (self.GRAPH_PAD * 2)
        self.block_width = max(1, round(self.graph_width / len(lst)))
        
        # Height calculations
        graph_height = self.height - 150 # Leave room for header/footer
        val_range = (self.max_val - self.min_val) if (self.max_val - self.min_val) > 0 else 1
        self.block_height = math.floor(graph_height / val_range)
        
        self.start_x = self.GRAPH_PAD

# -----------------------------------------------------------------------------
# 4. HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def generate_list(n, min_val, max_val, mode="Random"):
    lst = []
    if mode == "Random":
        lst = [random.randint(min_val, max_val) for _ in range(n)]
    elif mode == "Sorted":
        lst = [int(min_val + (i * (max_val-min_val)/n)) for i in range(n)]
    elif mode == "Reversed":
        lst = [int(min_val + (i * (max_val-min_val)/n)) for i in range(n)]
        lst.reverse()
    elif mode == "Nearly Sorted":
        lst = [int(min_val + (i * (max_val-min_val)/n)) for i in range(n)]
        # Swap a few random pairs
        for _ in range(n // 5): 
            i1, i2 = random.randint(0, n-1), random.randint(0, n-1)
            lst[i1], lst[i2] = lst[i2], lst[i1]
    return lst

def draw_sidebar_text(window, text, x, y, font, color=Theme.TEXT_GREY):
    surf = font.render(text, True, color)
    window.blit(surf, (x, y))

# -----------------------------------------------------------------------------
# 5. MAIN LOOP
# -----------------------------------------------------------------------------
import pygame
import random
import math
from algorithms import bubble_sort, merge_sort, quick_sort, radix_sort, linear_search_wrapper

pygame.init()

# -----------------------------------------------------------------------------
# 1. THEME & CONFIGURATION
# -----------------------------------------------------------------------------
class Theme:
    # Colors based on your reference image
    BG_DARK       = (8, 12, 20)      # Deepest background (Main Window)
    BG_PANEL      = (15, 23, 35)     # Lighter panel (Sidebar/Graph bg)
    
    ACCENT_CYAN   = (0, 220, 255)    # Bright Cyan (Active buttons, Start button)
    
    TEXT_WHITE    = (240, 240, 240)
    TEXT_GREY     = (100, 115, 130)  # For labels like "ALGORITHM"
    
    BAR_DEFAULT   = (20, 160, 160)   # Teal bars
    BAR_ACTIVE    = (255, 60, 60)    # Red for active comparison
    
    BUTTON_OUTLINE = (40, 55, 75)    # Dark grey/blue outline for inactive buttons
    
    FONT_MONO = "consolas"           # Monospaced font for the "hacker" look

# -----------------------------------------------------------------------------
# 2. UI COMPONENTS (Buttons & Sliders)
# -----------------------------------------------------------------------------
class Button:
    def __init__(self, x, y, width, height, text, font, action_key=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.action_key = action_key  # Identifier for what this button does
        self.is_active = False
        self.is_hovered = False

    def draw(self, window, is_filled=False):
        # Determine Color
        color = Theme.BUTTON_OUTLINE
        text_color = Theme.TEXT_GREY
        
        if self.is_active:
            color = Theme.ACCENT_CYAN
            text_color = Theme.BG_DARK # Dark text on bright button
        elif self.is_hovered:
            color = (60, 80, 100)
            text_color = Theme.TEXT_WHITE
            
        # Draw Background
        if self.is_active or is_filled:
            if is_filled and not self.is_active: 
                # Special case for "Start" button (always filled cyan)
                pygame.draw.rect(window, Theme.ACCENT_CYAN, self.rect, border_radius=8)
                text_color = Theme.BG_DARK
            else:
                # Active toggle button
                pygame.draw.rect(window, Theme.ACCENT_CYAN, self.rect, border_radius=8)
        else:
            # Outlined inactive button
            pygame.draw.rect(window, color, self.rect, width=1, border_radius=8)

        # Draw Text
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        window.blit(text_surf, text_rect)

    def check_click(self, pos):
        return self.rect.collidepoint(pos)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

class Slider:
    def __init__(self, x, y, width, min_val, max_val, initial_val):
        self.rect = pygame.Rect(x, y, width, 6) # Track
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.dragging = False
        
        # Handle position
        self.handle_radius = 8
        self.update_handle_pos()

    def update_handle_pos(self):
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        handle_x = self.rect.x + (self.rect.width * ratio)
        self.handle_rect = pygame.Rect(handle_x - self.handle_radius, self.rect.centery - self.handle_radius, 
                                       self.handle_radius*2, self.handle_radius*2)

    def draw(self, window):
        # Draw Track (Dark Grey)
        pygame.draw.rect(window, (40, 50, 60), self.rect, border_radius=3)
        # Draw Active Track (Cyan part on the left)
        active_track = pygame.Rect(self.rect.x, self.rect.y, self.handle_rect.centerx - self.rect.x, self.rect.height)
        pygame.draw.rect(window, Theme.ACCENT_CYAN, active_track, border_radius=3)
        # Draw Handle
        pygame.draw.circle(window, Theme.BG_DARK, self.handle_rect.center, self.handle_radius) # Inner black
        pygame.draw.circle(window, Theme.ACCENT_CYAN, self.handle_rect.center, self.handle_radius, width=2) # Ring

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        
        if self.dragging and pygame.mouse.get_pressed()[0]:
            mouse_x = pygame.mouse.get_pos()[0]
            # Clamp to track
            mouse_x = max(self.rect.left, min(mouse_x, self.rect.right))
            ratio = (mouse_x - self.rect.left) / self.rect.width
            self.value = int(self.min_val + (ratio * (self.max_val - self.min_val)))
            self.update_handle_pos()
            return True # Value changed
        return False

# -----------------------------------------------------------------------------
# 3. DRAW INFORMATION CLASS
# -----------------------------------------------------------------------------
class DrawInformation:
    def __init__(self, width, height, lst):
        self.width = width
        self.height = height
        
        self.window = pygame.display.set_mode((width, height))
        pygame.display.set_caption("SortLab - Algorithm Visualizer")

        # Layout Constants
        self.SIDEBAR_WIDTH = 280
        self.GRAPH_PAD = 30
        
        # Fonts
        self.font_sm = pygame.font.SysFont(Theme.FONT_MONO, 14)
        self.font_md = pygame.font.SysFont(Theme.FONT_MONO, 18)
        self.font_lg = pygame.font.SysFont(Theme.FONT_MONO, 24, bold=True)
        self.font_xl = pygame.font.SysFont(Theme.FONT_MONO, 32, bold=True)

        self.set_list(lst)

    def set_list(self, lst):
        self.lst = lst
        self.min_val = min(lst)
        self.max_val = max(lst)

        # Graph area is strictly to the left of the sidebar
        self.graph_width = self.width - self.SIDEBAR_WIDTH - (self.GRAPH_PAD * 2)
        self.block_width = max(1, round(self.graph_width / len(lst)))
        
        # Height calculations
        graph_height = self.height - 150 # Leave room for header/footer
        val_range = (self.max_val - self.min_val) if (self.max_val - self.min_val) > 0 else 1
        self.block_height = math.floor(graph_height / val_range)
        
        self.start_x = self.GRAPH_PAD

# -----------------------------------------------------------------------------
# 4. HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def generate_list(n, min_val, max_val, mode="Random"):
    lst = []
    if mode == "Random":
        lst = [random.randint(min_val, max_val) for _ in range(n)]
    elif mode == "Sorted":
        lst = [int(min_val + (i * (max_val-min_val)/n)) for i in range(n)]
    elif mode == "Reversed":
        lst = [int(min_val + (i * (max_val-min_val)/n)) for i in range(n)]
        lst.reverse()
    elif mode == "Nearly Sorted":
        lst = [int(min_val + (i * (max_val-min_val)/n)) for i in range(n)]
        # Swap a few random pairs
        for _ in range(n // 5): 
            i1, i2 = random.randint(0, n-1), random.randint(0, n-1)
            lst[i1], lst[i2] = lst[i2], lst[i1]
    return lst

def draw_sidebar_text(window, text, x, y, font, color=Theme.TEXT_GREY):
    surf = font.render(text, True, color)
    window.blit(surf, (x, y))

# -----------------------------------------------------------------------------
# 5. MAIN LOOP
# -----------------------------------------------------------------------------
def main():
    run = True
    clock = pygame.time.Clock()

    # Initial Settings
    N = 50
    MIN_VAL, MAX_VAL = 5, 100
    current_algo_name = "Bubble Sort"
    current_algo_gen = bubble_sort
    current_input_mode = "Random"
    sorting = False
    start_time = None
    elapsed_time = 0
    accumulated_time = 0
    
    # 1. GENERATE INITIAL LIST
    lst = generate_list(N, MIN_VAL, MAX_VAL, current_input_mode)
    draw_info = DrawInformation(1100, 700, lst) 
    
    # --- SETUP UI ELEMENTS ---
    sidebar_x = draw_info.width - draw_info.SIDEBAR_WIDTH + 20
    
    # Algorithm Buttons
    btn_bubble = Button(sidebar_x, 100, 70, 30, "Bubble", draw_info.font_sm, "algo_bubble")
    btn_merge = Button(sidebar_x + 80, 100, 70, 30, "Merge", draw_info.font_sm, "algo_merge")
    btn_quick = Button(sidebar_x + 160, 100, 70, 30, "Quick", draw_info.font_sm, "algo_quick")
    btn_radix = Button(sidebar_x, 140, 70, 30, "Radix", draw_info.font_sm, "algo_radix")
    btn_linear = Button(sidebar_x + 80, 140, 70, 30, "Linear", draw_info.font_sm, "algo_linear") # New Button

    algo_buttons = [btn_bubble, btn_merge, btn_quick, btn_radix, btn_linear]
    btn_bubble.is_active = True # Default

    # Input Buttons
    btn_random = Button(sidebar_x, 240, 70, 30, "Random", draw_info.font_sm, "input_random")
    btn_sorted = Button(sidebar_x + 80, 240, 70, 30, "Sorted", draw_info.font_sm, "input_sorted")
    btn_reverse = Button(sidebar_x + 160, 240, 70, 30, "Reverse", draw_info.font_sm, "input_reversed")
    btn_nearly = Button(sidebar_x, 280, 110, 30, "Nearly Sorted", draw_info.font_sm, "input_nearly")
    
    input_buttons = [btn_random, btn_sorted, btn_reverse, btn_nearly]
    btn_random.is_active = True # Default

    # Sliders
    slider_size = Slider(sidebar_x, 370, 200, 10, 150, N)
    slider_speed = Slider(sidebar_x, 440, 200, 1, 100, 60) # FPS control

    # Action Buttons
    btn_start = Button(sidebar_x, 550, 230, 45, "Start", draw_info.font_lg, "action_start")
    btn_reset = Button(sidebar_x, 610, 230, 45, "Reset", draw_info.font_lg, "action_reset")

    algo_generator = None

    while run:
        # FPS Control based on Speed Slider
        clock.tick(slider_speed.value) 
        
        # 1. DRAW BACKGROUNDS
        draw_info.window.fill(Theme.BG_DARK)
        
        # Sidebar Background
        sidebar_rect = pygame.Rect(draw_info.width - draw_info.SIDEBAR_WIDTH, 0, draw_info.SIDEBAR_WIDTH, draw_info.height)
        pygame.draw.rect(draw_info.window, Theme.BG_PANEL, sidebar_rect)
        pygame.draw.line(draw_info.window, (30, 40, 50), (sidebar_rect.x, 0), (sidebar_rect.x, draw_info.height))

        # Graph Container Background (Rounded)
        graph_bg_rect = pygame.Rect(20, 80, draw_info.width - draw_info.SIDEBAR_WIDTH - 40, draw_info.height - 100)
        pygame.draw.rect(draw_info.window, Theme.BG_PANEL, graph_bg_rect, border_radius=12)

        # 2. HANDLE SORTING ANIMATION
        if sorting:
            try:
                row, color_indices = next(algo_generator)
                color_map = {idx: Theme.BAR_ACTIVE for idx in color_indices}
                elapsed_time = accumulated_time + (time.time() - start_time)
            except StopIteration:
                sorting = False
                color_map = {}
        else:
            color_map = {}

        # 3. DRAW BARS
        for i, val in enumerate(draw_info.lst):
            x = draw_info.start_x + i * draw_info.block_width
            
            # Height relative to graph container
            max_bar_height = draw_info.height - 160 
            normalized_height = (val - draw_info.min_val) / (draw_info.max_val - draw_info.min_val + 1)
            height = max(5, normalized_height * max_bar_height) 

            y = (draw_info.height - 30) - height 
            
            # Color logic
            color = Theme.BAR_DEFAULT
            if i in color_map:
                color = color_map[i]
            
            # Draw bar
            # Ensure bar stays inside graph width
            if x < draw_info.width - draw_info.SIDEBAR_WIDTH - 30:
                pygame.draw.rect(draw_info.window, color, (x, y, draw_info.block_width - 1, height), border_radius=2)

        # 4. DRAW HEADER INFO
        draw_sidebar_text(draw_info.window, ">_ SortLab", 30, 30, draw_info.font_lg, Theme.ACCENT_CYAN)
        draw_sidebar_text(draw_info.window, f"{current_algo_name}", 50, 100, draw_info.font_xl, Theme.TEXT_WHITE)
        
        # Complexity Hint
        if "Bubble" in current_algo_name: complexity = "O(n²)"
        elif "Merge" in current_algo_name: complexity = "O(n log n)"
        elif "Quick" in current_algo_name: complexity = "O(n log n)"
        elif "Radix" in current_algo_name: complexity = "O(nk)"
        elif "Linear" in current_algo_name: complexity = "O(n)" # Added Logic
        else: complexity = "O(n)"

        draw_sidebar_text(draw_info.window, f"Avg Complexity: {complexity}", 50, 140, draw_info.font_md, Theme.TEXT_GREY)

        # 5. DRAW SIDEBAR UI
        draw_sidebar_text(draw_info.window, "ALGORITHM", sidebar_x, 70, draw_info.font_sm)
        draw_sidebar_text(draw_info.window, "INPUT CONDITION", sidebar_x, 210, draw_info.font_sm)
        draw_sidebar_text(draw_info.window, f"ARRAY SIZE: {slider_size.value}", sidebar_x, 340, draw_info.font_sm)
        draw_sidebar_text(draw_info.window, f"SPEED: {slider_speed.value}%", sidebar_x, 410, draw_info.font_sm)
        draw_sidebar_text(draw_info.window, f"TIME: {elapsed_time:.2f}s", sidebar_x, 480, draw_info.font_sm)

        # Buttons
        for btn in algo_buttons + input_buttons:
            if btn.check_hover(pygame.mouse.get_pos()): pass 
            btn.draw(draw_info.window)
            
        btn_start.text = "Stop" if sorting else "Start"
        btn_start.is_active = sorting 
        btn_start.draw(draw_info.window, is_filled=True)
        btn_reset.draw(draw_info.window)

        # Sliders
        slider_size.draw(draw_info.window)
        slider_speed.draw(draw_info.window)

        pygame.display.update()

        # 6. EVENT HANDLING
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            # Slider Events
            if slider_size.handle_event(event):
                N = slider_size.value
                draw_info.set_list(generate_list(N, MIN_VAL, MAX_VAL, current_input_mode))
                sorting = False
                algo_generator = None
            
            slider_speed.handle_event(event)

            # Button Click Events
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not sorting:
                    # Algorithm Selection
                    for btn in algo_buttons:
                        if btn.check_click(event.pos):
                            for b in algo_buttons: b.is_active = False
                            btn.is_active = True
                            
                            if btn.action_key == "algo_bubble": 
                                current_algo_gen = bubble_sort
                                current_algo_name = "Bubble Sort"
                            elif btn.action_key == "algo_merge": 
                                current_algo_gen = merge_sort
                                current_algo_name = "Merge Sort"
                            elif btn.action_key == "algo_quick": 
                                current_algo_gen = quick_sort
                                current_algo_name = "Quick Sort"
                            elif btn.action_key == "algo_radix": 
                                current_algo_gen = radix_sort
                                current_algo_name = "Radix Sort"
                            elif btn.action_key == "algo_linear": 
                                current_algo_gen = linear_search_wrapper
                                current_algo_name = "Linear Search"
                    
                    # Input Selection
                    for btn in input_buttons:
                        if btn.check_click(event.pos):
                            for b in input_buttons: b.is_active = False
                            btn.is_active = True
                            
                            if btn.action_key == "input_random": current_input_mode = "Random"
                            elif btn.action_key == "input_sorted": current_input_mode = "Sorted"
                            elif btn.action_key == "input_reversed": current_input_mode = "Reversed"
                            elif btn.action_key == "input_nearly": current_input_mode = "Nearly Sorted"
                            
                            draw_info.set_list(generate_list(N, MIN_VAL, MAX_VAL, current_input_mode))

                    # Start
                    if btn_start.check_click(event.pos):
                        sorting = True
                        start_time = time.time()
                        algo_generator = current_algo_gen(draw_info.lst)
                    
                    # Reset
                    if btn_reset.check_click(event.pos):
                        sorting = False
                        start_time = None
                        elapsed_time = 0
                        accumulated_time = 0
                        draw_info.set_list(generate_list(N, MIN_VAL, MAX_VAL, current_input_mode))
                else:
                    # Allow Stop while sorting
                    if btn_start.check_click(event.pos):
                        accumulated_time += (time.time() - start_time)
                        elapsed_time = accumulated_time
                        sorting = False
                        start_time = None

    pygame.quit()

if __name__ == "__main__":
    main()
