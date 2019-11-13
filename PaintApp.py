import pygame
import math
from pygame.locals import *
from UnionFind import *
from Square import *
pygame.init()
screen = pygame.display.set_mode((1000, 600))
pygame.display.set_caption('Paint')
font = pygame.font.SysFont('times', 18)
small_font = pygame.font.SysFont('helvetica', 12)

# COLORS:
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (120, 120, 120)
LIGHT_GRAY = (200, 200, 200)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 153)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
LIGHT_BLUE = (102, 178, 255)
ORANGE = (255, 128, 0)
PURPLE = (153, 0, 153)
PINK = (255, 102, 255)


def find_pixel(x, y):
    """
    Finds the top-left corner of the pixel that contains a given dot
    :param x: x coordinate of the dot
    :param y: y coordinate of the dot
    :return: x,y coordinates of the top-left corner of the pixel
    """
    while x % 5 != 0:
        x -= 1
    while y % 5 != 0:
        y -= 1
    return x, y


def adjust_square(start_x, start_y, width, height):
    """
    Fixes coordinates before drawing a square in case width/height are smaller than start_x/start_y respectively
    :param start_x: Original start_x
    :param start_y: Original start_y
    :param width: Current width
    :param height: Current height
    :return: Updated coordinates
    """
    if width < start_x:  # Mouse was dragged left
        temp = start_x
        start_x = width
        width = temp
    if height < start_y:  # Mouse was dragged up
        temp = start_y
        start_y = height
        height = temp
    return start_x, start_y, width, height


def make_square(current_color, start_x, start_y, width, height, mode):
    """
    Creates a blank square on the screen. Used for modes 'Square', 'Oval', Copy' and 'Cut'.
    :param current_color: Color of the square/Oval
    :param start_x: x coordinate of where the square/Oval started
    :param start_y: y coordinate of where the square/Oval started
    :param width: Width of the square/Oval
    :param height: Height of the square/Oval
    :param mode: Current mode being used
    :return: Replica of the surface the square/Oval covers and updated start_x and start_y coordinates
    """
    # Fix coordinates in case start_x > width and/or start_y > height:
    start_x, start_y, width, height = adjust_square(start_x, start_y, width, height)
    if mode == 'Oval':
        '''
        In case an oval is being drawn, the start_x, start_y, width and height parameters will be used to
        determine the rectangle in which the oval is blocked.
        The oval will be plotted using the formula for the graph of an ellipse.
        '''
        # Determine shape:
        if width - start_x > height - start_y:
            shape = 'Horizontal'
        else:
            shape = 'Vertical'
        # Find all necessary coordinates:
        center_x, center_y = start_x + (width - start_x)/2, start_y + (height - start_y)/2    # Center of the ellipse
        if shape == 'Horizontal':
            a = center_x - start_x    # Distance from width to center
            b = center_y - start_y    # Distance from height to center
        else:
            b = center_x - start_x  # Distance from width to center
            a = center_y - start_y  # Distance from height to center

    # Create replica of the surface that will be covered by the *entire* square before it is drawn:
    save_rect = pygame.Rect(start_x, start_y, width - start_x + 5, height - start_y + 5)
    save_last = pygame.Surface((width - start_x + 5, height - start_y + 5))
    save_last.blit(screen, (0, 0), area=save_rect)
    
    if abs(width - start_x) >= 5 and abs(height - start_y) >= 5:    # Square is more than 2 pixels wide/high
        # Create replica of the surface covered *only by the inside* of the square before it is drawn:
        filler_rect = pygame.Rect(start_x + 5, start_y + 5, width - start_x - 5, height - start_y - 5)
        save_filler = pygame.Surface((width - start_x - 5, height - start_y - 5))
    else:
        filler_rect = pygame.Rect(start_x, start_y, width - start_x, height - start_y)
        save_filler = pygame.Surface((width - start_x, height - start_y))
    save_filler.blit(screen, (0, 0), area=filler_rect)

    # Draw a filled square and blit back the filler surface to create an empty square:
    if mode == 'Square':
        pygame.draw.rect(screen, current_color, (start_x, start_y, width - start_x + 5, height - start_y + 5))
        screen.blit(save_filler, (start_x + 5, start_y + 5))

    elif mode == 'Oval':
        if shape == 'Horizontal':
            for x in range(start_x, width):
                # Apply formula for the graph of a horizontal ellipse:
                y1 = center_y + math.sqrt(b ** 2 - ((b * (x - center_x))/a) ** 2)
                y2 = center_y - math.sqrt(b ** 2 - ((b * (x - center_x))/a) ** 2)
                y1, y2 = int(y1), int(y2)
                color_x, color_y = find_pixel(x, y1)
                if color_x < width and color_y < height:
                    pygame.draw.rect(screen, current_color, (color_x, color_y, 5, 5))
                color_x, color_y = find_pixel(x, y2)
                if color_x < width and color_y < height:
                    pygame.draw.rect(screen, current_color, (color_x, color_y, 5, 5))
                if x == start_x + 4 or x == width - 4:    # Close off holes in the left/right ends of the ellipse
                    for y in range(y2, y1):
                        color_x, color_y = find_pixel(x, y)
                        pygame.draw.rect(screen, current_color, (color_x, color_y, 5, 5))
        else:
            for y in range(start_y, height):
                # Apply formula for the graph of a vertical ellipse:
                x1 = center_x + math.sqrt(b ** 2 - ((b * (y - center_y))/a) ** 2)
                x2 = center_x - math.sqrt(b ** 2 - ((b * (y - center_y))/a) ** 2)
                x1, x2 = int(x1), int(x2)
                color_x, color_y = find_pixel(x1, y)
                if color_x < width and color_y < height:
                    pygame.draw.rect(screen, current_color, (color_x, color_y, 5, 5))
                color_x, color_y = find_pixel(x2, y)
                if color_x < width and color_y < height:
                    pygame.draw.rect(screen, current_color, (color_x, color_y, 5, 5))
                if y == start_y + 4 or y == height - 4:    # Close off holes in the top/bottom ends of the ellipse
                    for x in range(x2, x1):
                        color_x, color_y = find_pixel(x, y)
                        pygame.draw.rect(screen, current_color, (color_x, color_y, 5, 5))

    else:    # 'Copy'/'Cut' mode, create a thin-lined square (that disappears after use)
        pygame.draw.rect(screen, BLACK, (start_x, start_y, width - start_x + 5, height - start_y + 5), 1)
        screen.blit(save_filler, (start_x + 5, start_y + 5))
    return save_last, start_x, start_y


def open_color_plate(current_color):
    """
    Opens the color plate and lets the user pick one of 117 available coors
    :param current_color: The current color
    :return: New color, and true if user continues using Paint, false if user exits
    """
    new_color = current_color
    pygame.draw.rect(screen, WHITE, (150, 20, 830, 560))
    color_plate = [(51, 0, 0), (102, 0, 0), (153, 0, 0),               # Column 1
                   (204, 0, 0), (255, 0, 0), (255, 51, 51),
                   (255, 102, 102), (255, 153, 153), (255, 204, 204),
                   (51, 25, 0), (102, 51, 0), (153, 76, 0),            # Column 2
                   (204, 102, 0), (255, 128, 0), (255, 153, 51),
                   (255, 178, 102), (255, 204, 153), (255, 229, 204),
                   (51, 51, 0), (102, 102, 0), (153, 153, 0),          # Column 3
                   (204, 204, 0), (255, 255, 0), (255, 255, 51),
                   (255, 255, 102), (255, 255, 153), (255, 255, 204),
                   (25, 51, 0), (51, 102, 0), (76, 153, 0),            # Column 4
                   (102, 204, 0), (128, 255, 0), (153, 255, 51),
                   (178, 255, 102), (204, 255, 153), (229, 255, 204),
                   (0, 51, 0), (0, 102, 0), (0, 153, 0),               # Column 5
                   (0, 204, 0), (0, 255, 0), (51, 255, 51),
                   (102, 255, 102), (153, 255, 153), (204, 255, 204),
                   (0, 51, 25), (0, 102, 51), (0, 153, 76),            # Column 6
                   (0, 204, 102), (0, 255, 128), (51, 255, 153),
                   (102, 255, 178), (153, 255, 204), (204, 255, 229),
                   (0, 51, 51), (0, 102, 102), (0, 153, 153),          # Column 7
                   (0, 204, 204), (0, 255, 255), (51, 255, 255),
                   (102, 255, 255), (153, 255, 255), (204, 255, 255),
                   (0, 25, 51), (0, 51, 102), (0, 76, 153),            # Column 8
                   (0, 102, 204), (0, 128, 255), (51, 153, 255),
                   (102, 178, 255), (153, 204, 255), (204, 229, 225),
                   (0, 0, 51), (0, 0, 102), (0, 0, 153),               # Column 9
                   (0, 0, 204), (0, 0, 255), (51, 51, 255),
                   (102, 102, 255), (153, 153, 255), (204, 204, 255),
                   (25, 0, 51), (51, 0, 102), (76, 0, 153),            # Column 10
                   (102, 0, 204), (127, 0, 255), (153, 51, 255),
                   (178, 102, 255), (204, 153, 255), (229, 204, 255),
                   (51, 0, 51), (102, 0, 102), (153, 0, 153),          # Column 11
                   (204, 0, 204), (255, 0, 255), (255, 51, 255),
                   (255, 102, 255), (255, 153, 255), (255, 204, 255),
                   (51, 0, 25), (102, 0, 51), (153, 0, 76),            # Column 12
                   (204, 0, 102), (255, 0, 127), (255, 51, 153),
                   (255, 102, 178), (255, 153, 204), (255, 204, 229),
                   (0, 0, 0), (32, 32, 32), (64, 64, 64),              # Column 13
                   (96, 96, 96), (128, 128, 128), (160, 160, 160),
                   (192, 192, 192), (224, 224, 224), (255, 255, 255)]    # RGB values of 117 colors
    color_positions = []
    count = 0
    current_color_pos = 0
    for i in range(13):
        for j in range(9):    # Position the colors on the screen
            color_positions.append(pygame.draw.rect(screen, color_plate[count],
                                                    (152 + (63.7 * i), 22 + (62 * j), 60, 60)))
            if color_plate[count] == current_color:
                # "Vanish"" current color
                pygame.draw.rect(screen, WHITE, (152 + (63.7 * i), 22 + (62 * j), 60, 60))
                current_color_pos = count
            count += 1

    while True:
        cursor = (mouse_x, mouse_y) = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT:
                return new_color, False

            elif event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
                for i in range(117):
                    if color_positions[i].collidepoint(cursor):    # User chose color
                        if i != current_color_pos:    # Check that it isn't the currently equipped color
                            new_color = screen.get_at((mouse_x, mouse_y))
                            pygame.draw.rect(screen, WHITE, color_positions[i])  # "Vanish" new color
                            pygame.draw.rect(screen, new_color, (80, 565, 14, 14))
                            pygame.draw.rect(screen, color_plate[current_color_pos], color_positions[current_color_pos])
                            # (line 185) return previous color
                            current_color_pos = i
                if pygame.Rect(30, 25, 90, 40).collidepoint(cursor):    # User leaves the color plate
                    return new_color, True
        pygame.display.flip()


def help_screen():
    """
    Controls the screen while "Help" is being accessed
    :return: True if user continues using Paint, false if user exits
    """
    pygame.draw.rect(screen, WHITE, (150, 20, 830, 560))
    help_text = ["Welcome to Paint!", "Color: pick one of 117 colors.", "Pen: free draw across the canvas.",
                 "Fill: fill an enclosed area on the canvas.", "Eraser: turn selected areas on canvas back into white.",
                 "Square: draw a blank rectangle on the canvas.", "Oval: draw a blank ellipse on the canvas.",
                 "Clear: reset canvas.", "Copy: copy a rectangular area from canvas.",
                 "Cut: copy a rectangular area from canvas and whiten it", "Paste: paste back copied area.",
                 "Undo: undo last action (pen/eraser/fill/square/Oval/cut/paste/clear/load).",
                 "Save: save current canvas.",
                 "Load: load last saved canvas. Note: loading without saving loads blank canvas.",
                 "Screenshot: save current canvas to your computer."]

    help_lines = []
    count = 0
    for text in help_text:    # Position text lines on the screen
        help_lines.append(font.render(text, 0, BLACK))

        screen.blit(help_lines[count], (160, 30 + (30 * count)))
        count += 1
    pygame.display.flip()

    while True:
        cursor = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
                if pygame.Rect(900, 2, 80, 18).collidepoint(cursor):
                    return True


def generate_file_name(num):
    """
    Recursively looks for a file name that doesn't exist in folder for saving a screenshot
    :param num: Suffix for the file name
    :return: Valid file name
    """
    file_name = 'C:/Users/yargr/Desktop/screenshot'
    if num == 0:    # First call
        file_name += '.jpg'
    else:
        file_name += str(num) + '.jpg'

    try:    # Look for a file by that name
        pygame.image.load(file_name)
    except:    # File doesn't exist - name is valid
        return file_name
    else:    # Name exists - try again with new suffix
        file_name = generate_file_name(num + 1)

    return file_name


###################################
    # UNION FUNCTIONS:
###################################


def pixel_id(x, y):
    """
    Finds the cell containing the given x, y coordinates inside the 166x112 table of the canvas
    :param x: x coordinate
    :param y: y coordinate
    :return: ID (serial number) of the cell
    """
    pixel_x, pixel_y = find_pixel(x, y)
    pixel_x -= 150
    pixel_y -= 20
    return (int(pixel_x/5) * 112) + int(pixel_y/5)


def connect(uf, x1, y1, x2, y2):
    """
    Performs union of sets containing the given 2 pixels.
    :param uf: UnionFind object
    :param x1: x coordinate of 1st pixel
    :param y1: y coordinate of 1st pixel
    :param x2: x coordinate of 2nd pixel
    :param y2: y coordinate of 2nd pixel
    :return: void
    """
    element1 = pixel_id(x1, y1)
    element2 = pixel_id(x2, y2)

    uf.union(element1, element2)


def are_connected(uf, x1, y1, x2, y2):
    """
    Checks if 2 pixels belong to the same set
    :param uf: UnionFind object
    :param x1: x coordinate of 1st pixel
    :param y1: y coordinate of 1st pixel
    :param x2: x coordinate of 2nd pixel
    :param y2: y coordinate of 2nd pixel
    :return: True if the pixels belong to the same set, false otherwise
    """
    return uf.find_leader(pixel_id(x1, y1)) == UnionFind.find_leader(uf, pixel_id(x2, y2))


def unify(uf):
    """
    Performs union-find on the entire canvas
    :param uf: UnionFind object
    :return: void
    """
    for i in range(150, 980, 5):
        for j in range(20, 580, 5):
            if i < 980 and screen.get_at((i, j)) == screen.get_at((i + 5, j)):
                connect(uf, i, j, i + 5, j)
            if j < 580 and screen.get_at((i, j)) == screen.get_at((i, j + 5)):
                connect(uf, i, j, i, j + 5)


def main():

    ###################################
    # SETTING BASE SCREEN:
    ###################################

    screen.fill(GRAY)
    canvas = pygame.draw.rect(screen, WHITE, (150, 20, 830, 560))

    ###################################
    # SETTING CURRENT COLOR:
    ###################################

    current_color = BLACK   # Default starting color
    last_color = BLACK
    current_color_pos = pygame.draw.rect(screen, current_color, (80, 565, 14, 14))
    current_color_text = font.render("Color: ", 0, BLACK)
    current_color_text_pos = current_color_text.get_rect()
    current_color_text_pos.topleft = (30, 560)
    screen.blit(current_color_text, current_color_text_pos)

    ###################################
    # SETTING BUTTONS:
    ###################################

    buttons_pos = []
    buttons_text = [font.render('Colors', 0, BLACK), font.render('Pen', 0, BLACK), font.render('Fill', 0, BLACK),
                    font.render('Eraser', 0, BLACK), font.render('Square', 0, BLACK), font.render('Oval', 0, BLACK),
                    font.render('Copy', 0, BLACK), font.render('Cut', 0, BLACK), font.render('Paste', 0, BLACK),
                    font.render('Clear', 0, BLACK), font.render('Undo', 0, BLACK)]
    for i in range(11):
        buttons_pos.append(pygame.draw.rect(screen, BLACK, (30, (20 + 50 * (i % 11)), 90, 40), 1))
        text_pos = buttons_text[i].get_rect()
        text_pos.centerx = buttons_pos[i].centerx
        text_pos.centery = buttons_pos[i].centery
        screen.blit(buttons_text[i], text_pos)

    top_buttons_pos = []
    top_buttons_text = [small_font.render('Help', 0, BLACK), small_font.render('Load', 0, BLACK),
                        small_font.render('Save', 0, BLACK), small_font.render('Screenshot', 0, BLACK)]
    for i in range(4):
        top_buttons_pos.append(pygame.draw.rect(screen, BLACK, (900 - 90 * (i % 4), 2, 80, 18), 1))
        text_pos = top_buttons_text[i].get_rect()
        text_pos.centerx = top_buttons_pos[i].centerx
        text_pos.centery = top_buttons_pos[i].centery
        screen.blit(top_buttons_text[i], text_pos)

    ###################################
    # SETTING EVERYTHING UP:
    ###################################

    mode_list = ['Pen', 'Fill', 'Eraser', 'Square', 'Oval', 'Copy', 'Cut', 'Paste']
    mode = 'Pen'    # Default starting mode
    prev_eraser = False    # True when mode = 'Eraser' (for switching color from eraser white to what it was before)
    mode_text = font.render("Mode: " + mode, 0, BLACK)
    mode_text_pos = mode_text.get_rect()
    mode_text_pos.topleft = (30, 580)
    screen.blit(mode_text, mode_text_pos)

    draw_square = False    # False by default, true only when a square is being drawn
    draw_pen = False    # False by default, true only when pen/eraser is in use
    save_draft = pygame.Surface((830, 560))    # Used for the save/load buttons
    save_canvas = pygame.Surface((830, 560))    # Used for the colors/help buttons
    save_undo = pygame.Surface((830, 560))    # Used for undo button
    save_copy = pygame.Surface((0, 0))    # Ued for copy/cut/paste buttons
    save_draft.blit(screen, (0, 0), area=canvas)
    save_undo.blit(screen, (0, 0), area=canvas)

    pygame.display.flip()

    ###################################
    # MAIN LOOP:
    ###################################

    while True:
        cursor = (mouse_x, mouse_y) = pygame.mouse.get_pos()

        ###################################
        # DRAWING OR ERASING:
        ###################################

        if canvas.collidepoint(cursor) and pygame.mouse.get_pressed()[0] and mode in ['Pen', 'Eraser']:

            if not draw_pen:
                save_undo.blit(screen, (0, 0), area=canvas)
            draw_pen = True
            draw_x, draw_y = find_pixel(mouse_x, mouse_y)
            pygame.draw.rect(screen, current_color, (draw_x, draw_y, 5, 5))

        if draw_pen and (not pygame.mouse.get_pressed()[0] or not canvas.collidepoint(cursor)):
            # Pen/eraser was used and mouse was released or left canvas
            draw_pen = False

        ###################################
        # DRAWING SQUARE/OVAL/COPY/CUT:
        ###################################

        if canvas.collidepoint(cursor) and pygame.mouse.get_pressed()[0] and \
                mode in ['Square', 'Oval', 'Copy', 'Cut'] and not draw_square:
            original_x, original_y = start_x, start_y = find_pixel(mouse_x, mouse_y)
            width, height = find_pixel(mouse_x + 5, mouse_y + 5)
            save_rect = pygame.Rect(start_x, start_y, width - start_x, height - start_y)
            save_last = pygame.Surface((width - start_x, height - start_y))
            save_last.blit(screen, (0, 0), area=save_rect)
            if mode in ['Square', 'Oval']:
                save_undo.blit(screen, (0, 0), area=canvas)
            pygame.draw.rect(screen, current_color, (start_x, start_y, width - start_x, height - start_y))
            draw_square = True

        if draw_square and canvas.collidepoint(cursor) and pygame.mouse.get_pressed()[0]:
            # Mouse is being held down inside canvas, show square progress
            width, height = find_pixel(mouse_x, mouse_y)
            screen.blit(save_last, (start_x, start_y))
            start_x = original_x
            start_y = original_y
            save_last, start_x, start_y = make_square(current_color, start_x, start_y, width, height, mode)

        if not canvas.collidepoint(cursor) and draw_square:
            # Mouse is being held down outside canvas, show square progress
            width, height = find_pixel(mouse_x, mouse_y)
            if width < 150:  # Cursor is left of the canvas
                width = 150
            if width >= 980:  # Cursor is right of the canvas
                if mode == 'Oval':
                    width = 980
                else:
                    width = 975
            if height < 20:  # Cursor is above the canvas
                height = 20
            if height >= 580:  # Cursor if below the canvas
                if mode == 'Oval':
                    height = 580
                else:
                    height = 575

            screen.blit(save_last, (start_x, start_y))
            start_x = original_x
            start_y = original_y
            save_last, start_x, start_y = make_square(current_color, start_x, start_y, width, height, mode)

        if draw_square and not pygame.mouse.get_pressed()[0]:    # Square is done
            if mode == 'Copy' or mode == 'Cut':
                screen.blit(save_last, (start_x, start_y))    # Remove thin square
                save_copy = pygame.Surface((save_last.get_width(), save_last.get_height()))
                save_copy.blit(save_last, (0, 0))
                if mode == 'Cut':
                    save_undo.blit(screen, (0, 0), area=canvas)
                    save_last.fill(WHITE)
                    screen.blit(save_last, (start_x, start_y))
            del save_last    # Free memory
            del save_rect    # Free memory
            draw_square = False

        pygame.display.flip()

        ###################################
        # COLORING BUTTONS WHILE HOVERING:
        ###################################

        for i in range(11):    # Left buttons
            if buttons_pos[i].collidepoint(cursor):
                pygame.draw.rect(screen, LIGHT_GRAY, (buttons_pos[i].x + 1, buttons_pos[i].y + 1,
                                                      buttons_pos[i].w - 2, buttons_pos[i].h - 2))
            else:
                pygame.draw.rect(screen, GRAY, (buttons_pos[i].x + 1, buttons_pos[i].y + 1,
                                                buttons_pos[i].w - 2, buttons_pos[i].h - 2))
            text_pos = buttons_text[i].get_rect()
            text_pos.centerx = buttons_pos[i].centerx
            text_pos.centery = buttons_pos[i].centery
            screen.blit(buttons_text[i], text_pos)

        for i in range(4):    # Top buttons
            if top_buttons_pos[i].collidepoint(cursor):
                pygame.draw.rect(screen, LIGHT_GRAY, (top_buttons_pos[i].x + 1, top_buttons_pos[i].y + 1,
                                                      top_buttons_pos[i].w - 2, top_buttons_pos[i].h - 2))
            else:
                pygame.draw.rect(screen, GRAY, (top_buttons_pos[i].x + 1, top_buttons_pos[i].y + 1,
                                                top_buttons_pos[i].w - 2, top_buttons_pos[i].h - 2))
            text_pos = top_buttons_text[i].get_rect()
            text_pos.centerx = top_buttons_pos[i].centerx
            text_pos.centery = top_buttons_pos[i].centery
            screen.blit(top_buttons_text[i], text_pos)

        pygame.display.flip()

        ###################################
        # EVENT LOOP:
        ###################################

        for event in pygame.event.get():
            if event.type == QUIT:
                return

            elif event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
                if buttons_pos[0].collidepoint(cursor):    # Colors
                    save_canvas.blit(screen, (0, 0), area=canvas)
                    current_color, carry_on = open_color_plate(current_color)
                    if carry_on:
                        screen.blit(save_canvas, canvas)
                        if mode == 'Eraser':
                            mode = 'Pen'
                    else:
                        return

                for i in range(1, 9):    # Check if a "mode" button has been clicked
                    if buttons_pos[i].collidepoint(cursor):
                        mode = mode_list[i - 1]
                        if mode == 'Pen' or mode == 'Fill' or mode == 'Square':
                            if prev_eraser:
                                current_color = last_color
                            prev_eraser = False
                        elif mode == 'Eraser':
                            last_color = current_color
                            current_color = WHITE
                            prev_eraser = True

                if buttons_pos[9].collidepoint(cursor):    # CLear
                    save_undo.blit(screen, (0, 0), area=canvas)
                    canvas = pygame.draw.rect(screen, WHITE, (150, 20, 830, 560))

                if buttons_pos[10].collidepoint(cursor):    # Undo
                    screen.blit(save_undo, (150, 20))

                for i in range(4):    # Check if a top button has been clicked
                    if top_buttons_pos[i].collidepoint(cursor):
                        if i == 0:    # Help
                            save_canvas.blit(screen, (0, 0), area=canvas)
                            carry_on = help_screen()
                            if carry_on:
                                screen.blit(save_canvas, canvas)
                            else:
                                return

                        if i == 1:    # Load
                            save_undo.blit(screen, (0, 0), area=canvas)
                            screen.blit(save_draft, (150, 20))

                        if i == 2:    # Save
                            save_draft.blit(screen, (0, 0), area=canvas)

                        if i == 3:    # Screenshot
                            screenshot = screen.subsurface(canvas)
                            file_name = generate_file_name(0)
                            pygame.image.save(screenshot, file_name)

                if canvas.collidepoint(cursor) and mode == 'Fill':    # Filling an area
                    save_undo.blit(screen, (0, 0), area=canvas)
                    union = UnionFind(18592)
                    unify(union)
                    pixel_x, pixel_y = find_pixel(mouse_x, mouse_y)
                    pygame.draw.rect(screen, current_color, (pixel_x, pixel_y, 5, 5))
                    for i in range(150, 980, 5):
                        for j in range(20, 580, 5):
                            if i < 975 and are_connected(union, pixel_x, pixel_y, i + 5, j):
                                pygame.draw.rect(screen, current_color, (i + 5, j, 5, 5))
                            if j < 575 and are_connected(union, pixel_x, pixel_y, i, j + 5):
                                pygame.draw.rect(screen, current_color, (i, j + 5, 5, 5))

                    if are_connected(union, pixel_x, pixel_y, 150, 20):    # Top left pixel dealt with separately
                        pygame.draw.rect(screen, current_color, (150, 20, 5, 5))

                if mode == 'Paste' and canvas.collidepoint(cursor):
                    paste_x, paste_y = find_pixel(mouse_x, mouse_y)
                    save_undo.blit(screen, (0, 0), area=canvas)
                    if 980 - paste_x < save_copy.get_width() or 580 - paste_y < save_copy.get_height():
                        # area chosen for pasting is too small, paste partial image.
                        screen.blit(save_copy, (paste_x, paste_y), area=(0, 0, 980 - paste_x, 580 - paste_y))
                    else:
                        screen.blit(save_copy, (paste_x, paste_y))

            current_color_pos = pygame.draw.rect(screen, current_color, (80, 565, 14, 14))
            mode_text = font.render("Mode: " + mode, 0, BLACK)
            (x, y, w, h) = (mode_text_pos.x, mode_text_pos.y, mode_text_pos.w, mode_text_pos.h)
            pygame.draw.rect(screen, GRAY, (x, y, w, h))    # Override current mode text with blank gray rectangle
            mode_text_pos = mode_text.get_rect()
            mode_text_pos.topleft = (30, 580)
            screen.blit(mode_text, mode_text_pos)


if __name__ == '__main__':
    main()
