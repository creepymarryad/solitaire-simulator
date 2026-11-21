import os
import pygame
import card_class

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

class Game:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height

        self.font = pygame.font.Font(os.path.join(ASSETS_DIR, "Monocraft.ttc"), 20)
        self.filename = ""
        self.moves_total = 0

        try:
            self.title_img = pygame.image.load(os.path.join(ASSETS_DIR, "other", "title.png")).convert_alpha()
        except FileNotFoundError:
            self.title_img = None

        CARD_WIDTH = 120
        CARD_HEIGHT = 170

        self.images = {}
        suits = ["Kier", "Karo", "Trefl", "Pik"]
        values = [9, 10, "J", "Q", "K", "A"]

        try:
            for s in suits:
                for v in values:
                    filename = os.path.join(ASSETS_DIR, "cards", f"{s.lower()}_{str(v).lower()}.png")
                    img = pygame.image.load(filename).convert_alpha()
                    img = pygame.transform.scale(img, (CARD_WIDTH, CARD_HEIGHT))
                    self.images[(s, v)] = img
        except FileNotFoundError as e:
            print(f"Error loading graphics: {e}")

        try:
            self.card_back = pygame.image.load(os.path.join(ASSETS_DIR, "cards", "shirt.png")).convert_alpha()
            self.card_back = pygame.transform.scale(self.card_back, (CARD_WIDTH, CARD_HEIGHT))
        except FileNotFoundError:
            self.card_back = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
            self.card_back.fill((0,0,0))

        self.moves = []
        self.current_move_idx = 0
        self.last_move_time = 0
        self.move_delay = 500
        self.all_revealed = False

    def set_game_data(self, initial_deck, moves, filename="", moves_count=0):
        self.deck_state = initial_deck
        self.moves = moves
        self.filename = filename
        self.moves_total = moves_count
        
        self.current_move_idx = 0
        self.all_revealed = False
        
        self.table_cards = [None] * 23
        
        START_X = 150
        START_Y = 200 
        GAP_X = 160
        GAP_Y = 190

        for i, card_data in enumerate(initial_deck):
            row = i // 6
            col = i % 6
            pixel_x = START_X + (col * GAP_X)
            pixel_y = START_Y + (row * GAP_Y)

            suit, val = card_data

            if i == 23:
                img = self.images[(suit, val)]
                self.hand_card_obj = card_class.Card(suit, val, img, 1400, 400) 
            else:
                new_card_obj = card_class.Card(suit, val, self.card_back, pixel_x, pixel_y)
                self.table_cards[i] = new_card_obj
        
        self.last_move_time = pygame.time.get_ticks()

    def reveal_remaining_cards(self):
        suits = ["Kier", "Karo", "Trefl", "Pik"]
        values = [9, 10, "J", "Q", "K", "A"]

        for i in range(23):
            row = i // 6
            col = i % 6
            
            correct_suit = suits[row]
            correct_val = values[col]

            if self.table_cards[i]:
                self.table_cards[i].image = self.images[(correct_suit, correct_val)]

    def update_cards_positions(self, move):
        target_row, target_col = move['where_it_moved']
        target_idx = target_row * 6 + target_col

        card_to_place_data = move['was_in_hand']
        card_picked_up_data = move['now_in_hand']

        placed_img = self.images[card_to_place_data]
        self.table_cards[target_idx].image = placed_img
        self.table_cards[target_idx].suit = card_to_place_data[0]
        self.table_cards[target_idx].value = card_to_place_data[1]

        picked_img = self.images[card_picked_up_data]
        self.hand_card_obj.image = picked_img
        self.hand_card_obj.suit = card_picked_up_data[0]
        self.hand_card_obj.value = card_picked_up_data[1]

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "exit"
            
            now = pygame.time.get_ticks()
            
            if self.moves and self.current_move_idx < len(self.moves):
                if now - self.last_move_time > self.move_delay:
                    current_move = self.moves[self.current_move_idx]
                    self.update_cards_positions(current_move)
                    self.current_move_idx += 1
                    self.last_move_time = now

            elif not self.all_revealed:
                self.reveal_remaining_cards()
                self.all_revealed = True
            
            self.screen.fill((140, 180, 94)) 

            if self.title_img:
                title_x = (self.width - self.title_img.get_width()) // 2
                self.screen.blit(self.title_img, (title_x, 20))

            for card in self.table_cards:
                if card is not None:
                    card.draw(self.screen)

            if hasattr(self, 'hand_card_obj'):
                self.hand_card_obj.draw(self.screen)

            if self.filename:
                info_text = f"Plik: {self.filename} | Ruchy w rozwiazaniu: {self.moves_total}"
                text_surf = self.font.render(info_text, True, (193, 255, 201))
                self.screen.blit(text_surf, (1200, self.height - 40))

            pygame.display.flip()
            
        return "exit"