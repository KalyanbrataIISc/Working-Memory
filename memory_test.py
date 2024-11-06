import pygame
import sys
import random
import csv
import time

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

# Experiment parameters
set_sizes = [5, 10, 15, 20, 25, 30, 35]  # Updated set sizes with 30 and 35 added
random.shuffle(set_sizes)  # Randomize the order of set sizes for presentation
all_words = [
    "apple", "grape", "cloud", "light", "stone", "tiger", "river", "chair", "plaza", "brush",
    "scale", "hotel", "train", "plane", "forest", "liver", "stone", "creek", "park", "stage",
    "movie", "house", "plane", "bottle", "vigor", "shade", "smile", "watch", "piano", "lemon",
    "daisy", "guitar", "shelf", "bread", "catch", "leaf", "purse", "track", "guide", "pearl",
    "lunar", "pencil", "track", "mango", "swipe", "candy", "cookie", "juice", "moss", "path",
    "shine", "laser", "cherry", "liver", "grape", "beach", "grape", "horse", "stone", "stove",
    "glove", "flame", "kick", "bounce", "clash", "smoke", "shout", "baker", "sugar", "board",
    "knock", "flood", "stone", "shaky", "carve", "clamp", "boil", "glory", "vivid", "flask",
    "mint", "smile", "dash", "pride", "frill", "habit", "tight", "scarf", "shirt", "glove",
    "whale", "plane", "leaf", "tiger", "storm", "swoop", "brave", "lucky", "chat", "dice",
    "vibe", "meat", "love", "hop", "ice", "plane", "shelf", "dog", "elephant", "fish", "lake",
    "dart", "task", "lucky", "clean", "rush", "lane", "golf", "nail", "hat", "cat", "box",
    "puff", "fridge", "cloud", "trick", "brink", "joke", "quiz", "mist", "tail", "tide", "star",
    "bell", "feel", "muse", "clue", "gale", "sort", "slam", "push", "flip", "glide", "plug",
    "bead", "page", "lock", "star", "scrap", "pipe", "tart", "flip", "space", "tool", "edge",
    "slot", "clay", "trap", "chop", "fair", "spin", "spool", "skirt", "tear", "bead", "tale",
    "flop", "bake", "hole", "tail", "loft", "trim", "bike", "slip", "trip", "rock", "swoop",
    "gleam", "rest", "dash", "bike", "golf", "cast", "coil", "straw", "fluff", "maze", "trim",
    "whip", "rays", "glow", "rose", "trap", "task", "zone", "rays", "pace", "flock", "task",
    "wild", "peep", "drip", "wood", "flip", "tape", "quick", "rain", "mice", "zoom", "slam",
    "rock", "turn", "brim", "dear", "glow", "spoon", "tail", "fire", "stamp", "goal", "tune",
    "good", "race", "rich", "clay", "wind", "loud", "path", "dear", "page", "trip", "lace",
    "soft", "flip", "loud", "duck", "rim", "frost", "test", "crisp", "lamp", "back", "bark",
    "race", "trap", "flap", "lock", "spin", "tip", "cloud", "blow", "coin", "speed", "race",
    "shine", "loud", "jack", "task", "palm", "fish", "star", "hint", "shout", "snip", "pass",
    "dream", "pull", "jump", "race", "step", "time", "tune", "mix", "bell", "shout", "drain"
]  # Further expanded word list for larger sets

data = []

# Button class
class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = GRAY

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surf = word_font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Main experiment function
def run_experiment():
    used_words = set()
    for set_size in set_sizes:
        # Ensure no common words between sets by using the difference between all_words and used_words
        available_words = list(set(all_words) - used_words)
        trial_words = random.sample(available_words, set_size)
        used_words.update(trial_words)
        display_fixation()
        display_words(trial_words, set_size)
        
        # Generate test words: 5 from set and 5 from outside the set
        test_words = random.sample(trial_words, 5) + random.sample(list(set(all_words) - set(trial_words)), 5)
        random.shuffle(test_words)  # Randomize the order of test words

        # Ask multiple questions per set size
        for test_word in test_words:
            is_target = test_word in trial_words
            display_test_word(test_word)
            response, response_time = collect_response()
            correct = (response == "Yes" and is_target) or (response == "No" and not is_target)
            timestamp = time.time()
            trial_data = {
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
        pygame.time.delay(500)  # Small delay between set sizes

    # Save data to CSV
    save_data()

# Display fixation cue
def display_fixation():
    screen.fill(WHITE)
    fixation_text = fixation_font.render("+", True, BLACK)
    fixation_rect = fixation_text.get_rect(center=(window_width/2, window_height/2))
    screen.blit(fixation_text, fixation_rect)
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
        screen.blit(timer_text, (window_width - 150, 10))

        # Display words
        for i, word in enumerate(words):
            word_text = word_font.render(word, True, BLACK)
            word_rect = word_text.get_rect(center=positions[i])
            screen.blit(word_text, word_rect)

        pygame.display.flip()
        clock.tick(60)

# Generate random positions for words
def generate_positions(num_words):
    positions = []
    exclusion_zone = pygame.Rect(window_width/2 - 50, window_height/2 - 50, 100, 100)
    while len(positions) < num_words:
        x = random.randint(50, window_width - 50)
        y = random.randint(50, window_height - 100)
        new_rect = pygame.Rect(x - 50, y - 15, 100, 30)
        if not new_rect.colliderect(exclusion_zone) and all(not new_rect.colliderect(pygame.Rect(pos[0] - 50, pos[1] - 15, 100, 30)) for pos in positions):
            positions.append((x, y))
    return positions

# Display test word
def display_test_word(test_word):
    screen.fill(WHITE)
    word_text = word_font.render(test_word, True, BLACK)
    word_rect = word_text.get_rect(center=(window_width/2, window_height/2 - 50))
    screen.blit(word_text, word_rect)
    pygame.display.flip()

# Collect response
def collect_response():
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
                    response = "Yes"
                if no_button.is_clicked(event.pos):
                    response = "No"

        yes_button.draw()
        no_button.draw()
        pygame.display.flip()
        clock.tick(60)
    response_time = time.time() - start_time
    return response, response_time

# Save data to CSV
def save_data():
    with open('experiment_data.csv', mode='w', newline='') as file:
        fieldnames = ["Set Size", "Words Displayed", "Test Word", "Is Target",
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
        "After a short delay, a test word will appear.",
        "Press 'Yes' if you saw the word earlier, 'No' if you did not.",
        "",
        "Press any key to start the experiment."
    ]
    screen.fill(WHITE)
    y_offset = 100
    for line in instructions:
        instruction_text = word_font.render(line, True, BLACK)
        instruction_rect = instruction_text.get_rect(center=(window_width/2, y_offset))
        screen.blit(instruction_text, instruction_rect)
        y_offset += 40
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
