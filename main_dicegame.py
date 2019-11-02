# --------------------------------------------------------------------
# Program: Review Assignment #3 - Pygame Dice Game
# Author: Alex Hyde, Keon Madani
# Description: This program generates and animates a random dice roll
#   for each player of length 6-10. Each player has to guess their
#   score, and if they get it is added to their total score. The first
#   person to reach the target score wins. For tie breakers, the
#   player with the most points wins, and if they are still tied,
#   only the tied players keep player.
# Input: The program takes input from the user using custom pygame
#   input functions for the number of players, number of dice, target
#   score, and to guess the score of their dice roll.
# --------------------------------------------------------------------

import pygame
import dice3d

pygame.init()

# screen dimensions
WIN_WIDTH = 1000
WIN_HEIGHT = 600

# set win screen for the dice
dice3d.init(WIN_WIDTH, WIN_HEIGHT)

# use same window for the dice and the game
WIN = dice3d.win

#colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
THE_BLUE = (130, 250, 226)


# object for an input box
class InputBox:
    def __init__(self, prompt, x, y, int_input=False, bg_colour=None, bg_border=0):
        self.x = x
        self.y = y
        self.prompt = prompt    # the prompt that is always displayed in the input box
        if int_input:   # if the input must be an integer
            self.VALID_KEYS = "0123456789"
        else:
            self.VALID_KEYS = "0123456789qwertyuiopasdfghjklzxcvbnm"
        #the text being inputed
        self.input_text = ""
        self.bg_colour = bg_colour
        self.bg_border = bg_border
        self.drawable = None    # the total text of the input box in the form of rendered text
        self.update()   # sets the drawable

    # sets and resets the drawable (to update the text when input is given)
    def update(self):
        text = self.prompt + self.input_text
        if self.drawable in drawables:  # remove the previous text so there are no overlapping texts
            drawables.remove(self.drawable)
        self.drawable = print_text(text, self.x, self.y)

    # set the input text given a key press
    def set_input(self, event):
        if event.unicode in self.VALID_KEYS:
            self.input_text += event.unicode
        elif event.key == pygame.K_BACKSPACE:
            if self.input_text != "":
                self.input_text = self.input_text[:-1]
        self.update()   # update new drawable with new text

    # return the input
    def get_input(self):
        return self.input_text


# class to make rendered text easily drawable from a list
class Text:
    def __init__(self, text, x, y):
        self.text = text
        self.x = x
        self.y = y

    def draw(self):
        WIN.blit(self.text, (self.x, self.y))


# button class for simple circular or rectangular buttons with a text
class Button:
    def __init__(self, x, y, dimentions, text, shape, colour=BLACK):
        self.x = x
        self.y = y
        self.dimensions = dimentions
        self.text = text
        self.shape = shape
        self.colour = colour

    # draw the button depending on whether it is circular or rectangular
    def draw(self):
        if self.shape == "circle":
            pygame.draw.circle(WIN, self.colour, (int(self.x), int(self.y)), self.dimensions)
            create_text(self.text, True, self.y, center_y=True).draw()
        elif self.shape == "rect":
            pygame.draw.rect(WIN, self.colour, (self.x, self.y, self.dimensions[0], self.dimensions[1]))
            create_text(self.text, True, self.y + self.dimensions[1]/2, center_y=True).draw()

    # check if the button is clicked
    def is_clicked(self, mouse_pos):
        if self.shape == "circle":
            return (self.x-mouse_pos[0])**2 + (self.y-mouse_pos[0])**2 < self.dimensions**2
        elif self.shape == "rect":
            return self.x<mouse_pos[0]<self.x+self.dimensions[0] and self.y<mouse_pos[1]<self.y+self.dimensions[0]


# function to animate the 3d rolling dice and return their values when the rolls are done
def roll_dice(num_dice):
    global closeGame
    dice_list = []
    die_size = 200
    bottom_row = num_dice // 2
    top_row = num_dice - bottom_row

    # generate coordinates for dice to make two rows
    for die in range(bottom_row):
        dice_list.append(dice3d.createCube((WIN_WIDTH-bottom_row*die_size)/2 + die*die_size + die_size/2, 400, 400))
    for die in range(top_row):
        dice_list.append(dice3d.createCube((WIN_WIDTH-top_row*die_size)/2 + die*die_size + die_size/2, 200, 400))

    drawables.append(dice_list)

    # animate the rolling dice
    while dice_list[0].rolling and not closeGame:
        redraw()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                closeGame = True
        for die in dice_list:
            die.roll()

    # return a list of dice values and the list of dice drawables (to remove them later)
    return [die.get_roll_value() for die in dice_list], dice_list


# Calculates a max score when given a list of rolled dice
def maxScore(diceList):
    all_sequence_scores = 0
    while len(diceList) > 1:
        current_sequence = 0
        longest_sequence = 0
        for num in range(1,7):
            if num in diceList:
                diceList.remove(num)
                current_sequence += 1
                if current_sequence > longest_sequence:
                    longest_sequence = current_sequence
            else:
                current_sequence = 0
                if longest_sequence == 1:
                    longest_sequence = 0
                else:
                    all_sequence_scores += longest_sequence ** 2
                    longest_sequence = 0
        if longest_sequence == 1:
            longest_sequence = 0
        all_sequence_scores += longest_sequence ** 2
    return all_sequence_scores


# input function to create an input box and wait for input
def inpt(prompt, x, y, int_input=False, return_null=True, bg_colour=None, bg_border=0):
    global closeGame
    # create input box
    input_box = InputBox(prompt, x, y, int_input, bg_colour, bg_border)
    while not closeGame:
        redraw()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                closeGame = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:    # if enter is pressed, return the input
                    if not ((not return_null) and input_box.get_input() == ""):
                        drawables.remove(input_box.drawable)
                        return input_box.get_input()
                else:
                    input_box.set_input(event)
    return 0


def print_text(str_text, x, y, bg_colour=None, bg_border=0, bg_width=0):
    text = FONT.render(str_text, True, BLACK)
    if x is True:
        x = (WIN_WIDTH - text.get_width()) / 2
    if bg_colour is not None:
        pygame.draw.rect(WIN, bg_colour, (x - bg_border, y - bg_border,
                                          text.get_width() + bg_border * 2, text.get_height() + bg_border * 2), bg_width)
    drawable = Text(text, x, y)
    drawables.append(drawable)
    return drawable


def create_text(str_text, x, y, center_y=False):
    text = FONT.render(str_text, True, BLACK)
    if x is True:
        x = (WIN_WIDTH - text.get_width()) / 2
    if center_y:
        y = (y - text.get_height()/2)
    drawable = Text(text, x, y)
    return drawable


def redraw():
    WIN.fill(THE_BLUE)

    for drawable in drawables:
        if type(drawable) == list:
            for nested_drawable in drawable:
                nested_drawable.draw()
        else:
            drawable.draw()

    pygame.display.update()


FONT = pygame.font.SysFont("Lucida Bright", 35)

drawables = []

roll_button = Button(WIN_WIDTH/2, 500, 50, "ROLL", "circle", RED)
restart_button = Button(WIN_WIDTH/2-150, 500, (300, 50), "RESTART GAME", "rect", BLUE)

clock = pygame.time.Clock()
inSetup = True
inPlay = False
inEndScreen = False
closeGame = False


while not closeGame:
    redraw()
    clock.tick(60)

    if inSetup:
        drawables = []
        num_players = int(inpt("Enter number of players: ", True, 500, True, False))
        while num_players < 1 and not closeGame:
            num_players = int(inpt("Enter a valid number of players: ", True, 500, True, False))
        num_dice = int(inpt("Enter number of dice (6 - 10): ", True, 500, True, False))
        while num_dice > 10 or num_dice < 6 and not closeGame:
            num_dice = int(inpt("Enter valid number of dice (6 - 10): ", True, 500, True, False))
        target_score = int(inpt("Enter target score: ", True, 500, True, False))

        score_list = [0] * num_players
        player_list = list(range(num_players))  # list of 0 to number of players -1
        winning_players = []
        player_index = 0

        current_scores_drawable = print_text(("Current scores: " + ", ".join(list(map(str, score_list)))), 10, 10)
        current_player_drawable = None

        inSetup = False
        inPlay = True

    elif inPlay:
        # iterates through all the active players (one full run of the loop is one round)
        player = player_list[player_index]

        redraw()
        if current_player_drawable not in drawables:
            current_player_drawable = print_text(("Current Player: " + str(player + 1)), True, 90)

        if roll_button not in drawables:
            drawables.append(roll_button)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                inGame = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if roll_button.is_clicked(pygame.mouse.get_pos()):
                    drawables.remove(roll_button)

                    # creates a list with all of the randomized values of the rolled dice
                    dice_list, dice_drawables = roll_dice(num_dice)

                    # calculates the score from the randomized list of dice values
                    score = maxScore(dice_list)

                    # gets valid integer input for the guess
                    guess_score = int(inpt("What is your score from this roll: ", True, 500, True, False))

                    # checks if the guess is correct and adds the score to the appropriate player
                    if guess_score == score:
                        correct_answer_drawable = print_text(("Correct, player " + str(player + 1) + " receives " +
                                                              str(score) + " points!"), True, 90)
                        score_list[player] += score
                    else:
                        correct_answer_drawable = print_text(("Incorrect, player " + str(player + 1) +
                                                              " receives no points. Correct score: " + str(score)), True, 90)
                    drawables.remove(current_player_drawable)

                    drawables.remove(current_scores_drawable)
                    current_scores_drawable = print_text(("Current scores: " + ", ".join(list(map(str, score_list)))), 10, 10)

                    if not closeGame:
                        redraw()
                        pygame.time.delay(3000)

                    drawables.remove(correct_answer_drawable)
                    drawables.remove(dice_drawables)

                    # if a player has achieved or passed the target score, they are appended to a winning players list
                    # possible for multiple players to be on the list if they achieve the score in the same round
                    if score_list[player] >= target_score:
                        winning_players.append(player)

                    player_index += 1

        if player_index > len(player_list) - 1:
            player_index = 0
            # if there is only one winning player, they win and the game is done
            if len(winning_players) == 1:
                winner = winning_players[0]
                drawables = []
                print_text("PLAYER " + str(winner+1) + " WINS!!", True, 100)
                drawables.append(restart_button)
                inPlay = False
                inEndScreen = True

            # if there are multiple winning players, run tie breaker code
            elif len(winning_players) > 1:

                # get the highest score from all of the players
                highestScore = max(score_list)

                # if only one player has the highest score, they win and the game is done
                if score_list.count(highestScore) == 1:
                    winner = score_list.index(highestScore)
                    drawables = []
                    print_text("PLAYER " + str(winner+1) + " WINS!!", True, 100)
                    drawables.append(restart_button)
                    inPlay = False
                    inEndScreen = True

                # if multiple players both have the same highest score, they become the only players in the player list (playerList)
                # they then play another round (for loop above), and they are the only players that will be playing
                else:
                    numPlayers = score_list.count(highestScore)
                    newPlayerList = []
                    for player, score in enumerate(score_list):
                        if score == highestScore:
                            newPlayerList.append(player)
                    player_list = newPlayerList
                    drawablesSave = drawables.copy()
                    print_text("TIE BREAKER!! PLAYERS: " + ", ".join(list(map(lambda p: str(p + 1), player_list))), True, 300)
                    redraw()
                    pygame.time.delay(2000)
                    drawables = drawablesSave.copy()

    if inEndScreen:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                closeGame = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.is_clicked(pygame.mouse.get_pos()):
                    inEndScreen = False
                    inSetup = True


pygame.quit()
