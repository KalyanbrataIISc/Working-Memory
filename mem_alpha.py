import pygame
import sys
import random
import csv
import time
from words import words  # Ensure you have a 'words.py' file with a 'words' list

# Initialize Pygame
pygame.init()

# Set up the window
window_width, window_height = 800, 600
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Working Memory Experiment")
clock = pygame.time.Clock()

# Fonts
fixation_font = pygame.font.SysFont(None, 72)
word_font = pygame.font.SysFont(None, 36)
timer_font = pygame.font.SysFont(None, 24)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Experiment parameters
set_sizes = [5, 10, 15, 20, 25, 30, 35]  # Set sizes
trials = []
for set_size in set_sizes:
    trials.extend([set_size]*3)  # 3 trials per set size
random.shuffle(trials)  # Randomize the order of trials

all_words = words  # Expanded word list to ensure enough unique words

data = []

total_trials = len(trials)
current_trial_number = 0  # Will be updated during the experiment

# Button class
class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = GRAY
        self.highlighted = False

    def draw(self):
        if self.highlighted:
            pygame.draw.rect(screen, GREEN, self.rect)  # Highlighted color
        else:
            pygame.draw.rect(screen, self.color, self.rect)
        text_surf = word_font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Function to draw the progress bar
def draw_progress_bar(current_trial, total_trials):
    progress_bar_width = window_width - 40  # Leave some padding
    progress_bar_height = 20
    progress = current_trial / total_trials
    filled_width = int(progress_bar_width * progress)

    # Outline of the progress bar
    pygame.draw.rect(screen, BLACK, (20, 20, progress_bar_width, progress_bar_height), 2)
    # Filled part of the progress bar
    pygame.draw.rect(screen, BLUE, (22, 22, filled_width, progress_bar_height - 4))

    # Progress text
    progress_text = timer_font.render(f"Trial {current_trial} of {total_trials}", True, BLACK)
    progress_rect = progress_text.get_rect(center=(window_width / 2, 50))
    screen.blit(progress_text, progress_rect)

# Main experiment function
def run_experiment():
    global current_trial_number
    trial_number = 1
    for set_size in trials:
        current_trial_number += 1
        trial_words = random.sample(all_words, set_size)
        display_fixation()
        display_words(trial_words, set_size)

        # Generate 5 target and 5 lure test words
        target_test_words = random.sample(trial_words, min(5, len(trial_words)))
        lure_test_words = random.sample(list(set(all_words) - set(trial_words)), 5)
        test_words = target_test_words + lure_test_words
        random.shuffle(test_words)

        test_number = 1
        for test_word in test_words:
            is_target = test_word in trial_words
            display_test_word(test_word)
            response, response_time = collect_response(test_word)
            correct = (response == "Yes" and is_target) or (response == "No" and not is_target)
            timestamp = time.time()
            trial_data = {
                "Trial Number": trial_number,
                "Test Number": test_number,
                "Set Size": set_size,
                "Words Displayed": trial_words,
                "Test Word": test_word,
                "Is Target": is_target,
                "Participant Response": response,
                "Correct": correct,
                "Timestamp": timestamp,
                "Response Time": response_time
            }
            data.append(trial_data)
            test_number += 1
            pygame.time.delay(500)  # Small delay between questions
        trial_number += 1
        pygame.time.delay(500)  # Small delay between trials

    # Save data to CSV
    save_data()

# Display fixation cue
def display_fixation():
    screen.fill(WHITE)
    fixation_text = fixation_font.render("+", True, BLACK)
    fixation_rect = fixation_text.get_rect(center=(window_width/2, window_height/2))
    screen.blit(fixation_text, fixation_rect)
    # Draw progress bar
    draw_progress_bar(current_trial_number, total_trials)
    pygame.display.flip()
    pygame.time.delay(1000)  # Display for 1 second

# Display words
def display_words(words, set_size):
    display_time = set_size * 1000  # 1 second per word
    start_time = pygame.time.get_ticks()
    positions = generate_positions(len(words))
    while pygame.time.get_ticks() - start_time < display_time:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(WHITE)
        # Timer
        time_left = display_time - (pygame.time.get_ticks() - start_time)
        timer_text = timer_font.render(f"Time Left: {int(time_left/1000) + 1}s", True, GRAY)
        screen.blit(timer_text, (10, window_height - 30))

        # Display words
        for i, word in enumerate(words):
            word_text = word_font.render(word, True, BLACK)
            word_rect = word_text.get_rect(center=positions[i])
            screen.blit(word_text, word_rect)

        # Draw progress bar
        draw_progress_bar(current_trial_number, total_trials)

        pygame.display.flip()
        clock.tick(60)

# Generate random positions for words
def generate_positions(num_words):
    positions = []
    exclusion_zone = pygame.Rect(window_width/2 - 50, window_height/2 - 50, 100, 100)
    attempts = 0
    max_attempts = 10000  # Increased attempts for larger sets
    while len(positions) < num_words and attempts < max_attempts:
        x = random.randint(50, window_width - 50)
        y = random.randint(80, window_height - 150)  # Adjusted to avoid overlapping with progress bar and buttons
        new_rect = pygame.Rect(x - 50, y - 15, 100, 30)
        if not new_rect.colliderect(exclusion_zone) and all(not new_rect.colliderect(pygame.Rect(pos[0] - 50, pos[1] - 15, 100, 30)) for pos in positions):
            positions.append((x, y))
        attempts += 1
    if attempts == max_attempts:
        print("Error: Unable to place all words without overlap.")
        pygame.quit()
        sys.exit()
    return positions

# Display test word
def display_test_word(test_word):
    screen.fill(WHITE)
    word_text = word_font.render(test_word, True, BLACK)
    word_rect = word_text.get_rect(center=(window_width/2, window_height/2 - 50))
    screen.blit(word_text, word_rect)
    # Draw progress bar
    draw_progress_bar(current_trial_number, total_trials)
    pygame.display.flip()

# Collect response
def collect_response(test_word):
    yes_button = Button(window_width/2 - 100, window_height/2 + 50, 80, 40, "Yes")
    no_button = Button(window_width/2 + 20, window_height/2 + 50, 80, 40, "No")
    start_time = time.time()
    response = None
    while response is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if yes_button.is_clicked(event.pos):
                    yes_button.highlighted = True
                    response = "Yes"
                elif no_button.is_clicked(event.pos):
                    no_button.highlighted = True
                    response = "No"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    yes_button.highlighted = True
                    response = "Yes"
                elif event.key == pygame.K_RIGHT:
                    no_button.highlighted = True
                    response = "No"

        screen.fill(WHITE)
        # Redraw test word
        word_text = word_font.render(test_word, True, BLACK)
        word_rect = word_text.get_rect(center=(window_width/2, window_height/2 - 50))
        screen.blit(word_text, word_rect)

        yes_button.draw()
        no_button.draw()

        # Draw progress bar
        draw_progress_bar(current_trial_number, total_trials)

        pygame.display.flip()
        clock.tick(60)

    response_time = time.time() - start_time
    # Show the highlighted button for confirmation
    pygame.display.flip()
    pygame.time.delay(200)

    # Reset highlights
    yes_button.highlighted = False
    no_button.highlighted = False
    return response, response_time

# Save data to CSV
def save_data():
    with open('experiment_data.csv', mode='w', newline='') as file:
        fieldnames = ["Trial Number", "Test Number", "Set Size", "Words Displayed", "Test Word", "Is Target",
                      "Participant Response", "Correct", "Timestamp", "Response Time"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for trial in data:
            writer.writerow(trial)
    pygame.quit()
    sys.exit()

# Instruction screen
def show_instructions():
    instructions = [
        "Welcome to the Working Memory Experiment!",
        "",
        "You will be shown a set of words displayed randomly on the screen.",
        "Try to remember as many words as you can.",
        "After the words disappear, you will be shown a series of test words.",
        "Press 'Yes' if you saw the word earlier, 'No' if you did not.",
        "You can use the left arrow key for 'Yes' and the right arrow key for 'No'.",
        "",
        "Press any key to start the experiment."
    ]
    screen.fill(WHITE)
    y_offset = 50
    for line in instructions:
        instruction_text = word_font.render(line, True, BLACK)
        instruction_rect = instruction_text.get_rect(center=(window_width/2, y_offset))
        screen.blit(instruction_text, instruction_rect)
        y_offset += 30
    pygame.display.flip()
    wait_for_keypress()

# Wait for key press
def wait_for_keypress():
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

# Run the program
if __name__ == "__main__":
    show_instructions()
    run_experiment()
