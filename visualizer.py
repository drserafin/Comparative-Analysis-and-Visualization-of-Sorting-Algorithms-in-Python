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
    BG_DARK       = (8, 12, 20)      
    BG_PANEL      = (15, 23, 35)     
    
    ACCENT_CYAN   = (0, 220, 255)    
    ACCENT_HOVER  = (0, 180, 210)    
    
    TEXT_WHITE    = (240, 240, 240)
    TEXT_GREY     = (100, 115, 130)  
    
    BAR_DEFAULT   = (20, 160, 160)   # Teal
    BAR_ACTIVE    = (255, 60, 60)    # Red for active comparison
    BAR_SORTED    = (50, 205, 50)    # Green for sorted
    
    BUTTON_OUTLINE = (40, 55, 75)    
    FONT_MONO = "consolas"           

# -----------------------------------------------------------------------------
# 2. UI COMPONENTS
# -----------------------------------------------------------------------------
class Button:
    def __init__(self, x, y, width, height, text, font, action_key=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.action_key = action_key  
        self.is_active = False
        self.is_hovered = False

    def draw(self, window, is_filled=False):
        color = Theme.BUTTON_OUTLINE
        text_color = Theme.TEXT_GREY
        
        if self.is_active:
            color = Theme.ACCENT_CYAN
            text_color = Theme.BG_DARK 
        elif self.is_hovered:
            color = (60, 80, 100)
            text_color = Theme.TEXT_WHITE
            
        if self.is_active or is_filled:
            pygame.draw.rect(window, Theme.ACCENT_CYAN, self.rect, border_radius=8)
            if is_filled and not self.is_active: text_color = Theme.BG_DARK
        else:
            pygame.draw.rect(window, color, self.rect, width=1, border_radius=8)

        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        window.blit(text_surf, text_rect)

    def check_click(self, pos): return self.rect.collidepoint(pos)
    def check_hover(self, pos): self.is_hovered = self.rect.collidepoint(pos)

class Slider:
    def __init__(self, x, y, width, min_val, max_val, initial_val):
        self.rect = pygame.Rect(x, y, width, 6) 
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.dragging = False
        self.handle_radius = 8
        self.update_handle_pos()

    def update_handle_pos(self):
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        handle_x = self.rect.x + (self.rect.width * ratio)
        self.handle_rect = pygame.Rect(handle_x - self.handle_radius, self.rect.centery - self.handle_radius, 
                                       self.handle_radius*2, self.handle_radius*2)

    def draw(self, window):
        pygame.draw.rect(window, (40, 50, 60), self.rect, border_radius=3)
        active_track = pygame.Rect(self.rect.x, self.rect.y, self.handle_rect.centerx - self.rect.x, self.rect.height)
        pygame.draw.rect(window, Theme.ACCENT_CYAN, active_track, border_radius=3)
        pygame.draw.circle(window, Theme.BG_DARK, self.handle_rect.center, self.handle_radius) 
        pygame.draw.circle(window, Theme.ACCENT_CYAN, self.handle_rect.center, self.handle_radius, width=2)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        
        if self.dragging and pygame.mouse.get_pressed()[0]:
            mouse_x = pygame.mouse.get_pos()[0]
            mouse_x = max(self.rect.left, min(mouse_x, self.rect.right))
            ratio = (mouse_x - self.rect.left) / self.rect.width
            self.value = int(self.min_val + (ratio * (self.max_val - self.min_val)))
            self.update_handle_pos()
            return True 
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
        self.SIDEBAR_WIDTH = 280
        self.GRAPH_PAD = 30
        self.font_sm = pygame.font.SysFont(Theme.FONT_MONO, 14)
        self.font_md = pygame.font.SysFont(Theme.FONT_MONO, 18)
        self.font_lg = pygame.font.SysFont(Theme.FONT_MONO, 24, bold=True)
        self.font_xl = pygame.font.SysFont(Theme.FONT_MONO, 32, bold=True)
        self.set_list(lst)

    def set_list(self, lst):
        self.lst = lst
        self.min_val = min(lst)
        self.max_val = max(lst)
        self.graph_width = self.width - self.SIDEBAR_WIDTH - (self.GRAPH_PAD * 2)
        self.block_width = max(1, round(self.graph_width / len(lst)))
        self.start_x = self.GRAPH_PAD

# -----------------------------------------------------------------------------
# 4. HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def generate_list(n, min_val, max_val, mode="Random"):
    if mode == "Random": return [random.randint(min_val, max_val) for _ in range(n)]
    elif mode == "Sorted": return [int(min_val + (i * (max_val-min_val)/n)) for i in range(n)]
    elif mode == "Reversed": return sorted([random.randint(min_val, max_val) for _ in range(n)], reverse=True)
    elif mode == "Nearly Sorted":
        lst = sorted([random.randint(min_val, max_val) for _ in range(n)])
        for _ in range(max(1, n // 10)):
            i1, i2 = random.randint(0, n-1), random.randint(0, n-1)
            lst[i1], lst[i2] = lst[i2], lst[i1]
        return lst
    return [random.randint(min_val, max_val) for _ in range(n)]

def draw_sidebar_text(window, text, x, y, font, color=Theme.TEXT_GREY):
    surf = font.render(text, True, color)
    window.blit(surf, (x, y))

# -----------------------------------------------------------------------------
# 5. MAIN LOOP
# -----------------------------------------------------------------------------
def main():
    run = True
    clock = pygame.time.Clock()

    N = 10
    MIN_VAL, MAX_VAL = 5, 100
    current_algo_name = "Bubble Sort"
    current_algo_gen = bubble_sort
    current_input_mode = "Random"
    sorting = False
    
    # Performance Tracking Variables
    start_time = None
    elapsed_time = 0
    accumulated_time = 0
    ops_count = 0  

    lst = generate_list(N, MIN_VAL, MAX_VAL, current_input_mode)
    draw_info = DrawInformation(1100, 700, lst) 
    sidebar_x = draw_info.width - draw_info.SIDEBAR_WIDTH + 20
    
    # UI Element Initialization
    btn_bubble = Button(sidebar_x, 100, 70, 30, "Bubble", draw_info.font_sm, "algo_bubble")
    btn_merge = Button(sidebar_x + 80, 100, 70, 30, "Merge", draw_info.font_sm, "algo_merge")
    btn_quick = Button(sidebar_x + 160, 100, 70, 30, "Quick", draw_info.font_sm, "algo_quick")
    btn_radix = Button(sidebar_x, 140, 70, 30, "Radix", draw_info.font_sm, "algo_radix")
    btn_linear = Button(sidebar_x + 80, 140, 70, 30, "Linear", draw_info.font_sm, "algo_linear")
    algo_buttons = [btn_bubble, btn_merge, btn_quick, btn_radix, btn_linear]
    btn_bubble.is_active = True 

    btn_random = Button(sidebar_x, 240, 70, 30, "Random", draw_info.font_sm, "input_random")
    btn_sorted = Button(sidebar_x + 80, 240, 70, 30, "Sorted", draw_info.font_sm, "input_sorted")
    btn_reverse = Button(sidebar_x + 160, 240, 70, 30, "Reverse", draw_info.font_sm, "input_reversed")
    btn_nearly = Button(sidebar_x, 280, 110, 30, "Nearly Sorted", draw_info.font_sm, "input_nearly")
    input_buttons = [btn_random, btn_sorted, btn_reverse, btn_nearly]
    btn_random.is_active = True 

    slider_size = Slider(sidebar_x, 370, 200, 10, 150, N)
    slider_speed = Slider(sidebar_x, 440, 200, 1, 100, 60) 
    btn_start = Button(sidebar_x, 580, 230, 45, "Start", draw_info.font_lg, "action_start")
    btn_reset = Button(sidebar_x, 635, 230, 45, "Reset", draw_info.font_lg, "action_reset")

    algo_generator = None
    color_map = {}

    while run:
        clock.tick(slider_speed.value) 
        
        if sorting:
            elapsed_time = accumulated_time + (time.time() - start_time)
            try:
                data = next(algo_generator)
                ops_count += 1
                if len(data) == 3:
                    row, active_indices, sorted_indices = data
                else:
                    row, active_indices = data
                    sorted_indices = []

                color_map = {idx: Theme.BAR_SORTED for idx in sorted_indices}
                for idx in active_indices: color_map[idx] = Theme.BAR_ACTIVE
            except StopIteration:
                sorting = False
                color_map = {i: Theme.BAR_SORTED for i in range(len(draw_info.lst))}

        # Drawing Layers
        draw_info.window.fill(Theme.BG_DARK)
        pygame.draw.rect(draw_info.window, Theme.BG_PANEL, (draw_info.width - draw_info.SIDEBAR_WIDTH, 0, draw_info.SIDEBAR_WIDTH, draw_info.height))
        pygame.draw.rect(draw_info.window, Theme.BG_PANEL, (20, 80, draw_info.width - draw_info.SIDEBAR_WIDTH - 40, draw_info.height - 100), border_radius=12)

        for i, val in enumerate(draw_info.lst):
            x = draw_info.start_x + i * draw_info.block_width
            norm_height = (val - draw_info.min_val) / (draw_info.max_val - draw_info.min_val + 1)
            height = max(5, norm_height * (draw_info.height - 160))
            y = (draw_info.height - 30) - height 
            color = color_map.get(i, Theme.BAR_DEFAULT)
            if x < draw_info.width - draw_info.SIDEBAR_WIDTH - 30:
                pygame.draw.rect(draw_info.window, color, (x, y, draw_info.block_width - 1, height), border_radius=2)

        # Labels & Performance Stats
        draw_sidebar_text(draw_info.window, ">_ SortLab", 30, 30, draw_info.font_lg, Theme.ACCENT_CYAN)
        draw_sidebar_text(draw_info.window, f"{current_algo_name}", 50, 100, draw_info.font_xl, Theme.TEXT_WHITE)
        
        complexities = {"Bubble": "O(n²)", "Merge": "O(n log n)", "Quick": "O(n log n)", "Radix": "O(nk)", "Linear": "O(n)"}
        comp_text = complexities.get(current_algo_name.split()[0], "O(n)")
        draw_sidebar_text(draw_info.window, f"Avg Complexity: {comp_text}", 50, 140, draw_info.font_md, Theme.TEXT_GREY)

        draw_sidebar_text(draw_info.window, f"TIME: {elapsed_time:.2f}s", sidebar_x, 480, draw_info.font_md, Theme.ACCENT_CYAN)
        draw_sidebar_text(draw_info.window, f"STEPS: {ops_count}", sidebar_x, 510, draw_info.font_md, Theme.TEXT_WHITE)

        draw_sidebar_text(draw_info.window, "ALGORITHM", sidebar_x, 70, draw_info.font_sm)
        draw_sidebar_text(draw_info.window, "INPUT CONDITION", sidebar_x, 210, draw_info.font_sm)
        draw_sidebar_text(draw_info.window, f"ARRAY SIZE: {slider_size.value}", sidebar_x, 340, draw_info.font_sm)
        draw_sidebar_text(draw_info.window, f"SPEED (FPS): {slider_speed.value}", sidebar_x, 410, draw_info.font_sm)

        for btn in algo_buttons + input_buttons:
            btn.check_hover(pygame.mouse.get_pos())
            btn.draw(draw_info.window)
            
        btn_start.text = "Pause" if sorting else ("Resume" if algo_generator else "Start")
        btn_start.is_active = sorting
        btn_start.draw(draw_info.window, is_filled=True)
        btn_reset.draw(draw_info.window)
        slider_size.draw(draw_info.window)
        slider_speed.draw(draw_info.window)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: run = False
            
            if slider_size.handle_event(event):
                N = slider_size.value
                draw_info.set_list(generate_list(N, MIN_VAL, MAX_VAL, current_input_mode))
                sorting = False; algo_generator = None; elapsed_time = 0; accumulated_time = 0; ops_count = 0; color_map = {}
            
            slider_speed.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_start.check_click(event.pos):
                    if sorting:
                        accumulated_time += (time.time() - start_time)
                        sorting = False
                    else:
                        sorting = True
                        start_time = time.time()
                        if not algo_generator: algo_generator = current_algo_gen(draw_info.lst)

                elif btn_reset.check_click(event.pos):
                    # RESET ALL STATES
                    sorting = False; algo_generator = None; start_time = None; 
                    elapsed_time = 0; accumulated_time = 0; ops_count = 0
                    color_map = {} # Reverts bars to Teal
                    draw_info.set_list(generate_list(N, MIN_VAL, MAX_VAL, current_input_mode))

                elif not sorting:
                    for btn in algo_buttons:
                        if btn.check_click(event.pos):
                            for b in algo_buttons: b.is_active = False
                            btn.is_active = True
                            current_algo_name = btn.text + (" Search" if "Linear" in btn.text else " Sort")
                            map_key = {"algo_bubble": bubble_sort, "algo_merge": merge_sort, "algo_quick": quick_sort, "algo_radix": radix_sort, "algo_linear": linear_search_wrapper}
                            current_algo_gen = map_key[btn.action_key]
                            algo_generator = None; elapsed_time = 0; accumulated_time = 0; ops_count = 0; color_map = {}
                            draw_info.set_list(generate_list(N, MIN_VAL, MAX_VAL, current_input_mode))
                    
                    for btn in input_buttons:
                        if btn.check_click(event.pos):
                            for b in input_buttons: b.is_active = False
                            btn.is_active = True
                            current_input_mode = btn.text
                            draw_info.set_list(generate_list(N, MIN_VAL, MAX_VAL, current_input_mode))
                            algo_generator = None; elapsed_time = 0; accumulated_time = 0; ops_count = 0; color_map = {}

    pygame.quit()

if __name__ == "__main__":
    main()