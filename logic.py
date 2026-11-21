CARD_ORDER = [
        [("Kier", 9), ("Kier", 10), ("Kier", "J"), ("Kier", "Q"), ("Kier", "K"), ("Kier", "A")],
        [("Karo", 9), ("Karo", 10), ("Karo", "J"), ("Karo", "Q"), ("Karo", "K"), ("Karo", "A")],
        [("Trefl", 9),("Trefl", 10),("Trefl", "J"),("Trefl", "Q"),("Trefl", "K"),("Trefl", "A")],
        [("Pik", 9),  ("Pik", 10), ("Pik", "J"), ("Pik", "Q"), ("Pik", "K"), ("Pik", "A")]
]

def create_layout(deck : list) -> list:
    layout = [
        deck[0:6],
        deck[6:12],
        deck[12:18],
        deck[18:23] + [None]
    ]
    hand = deck[23]
    return layout, hand

def target_card(card : tuple) -> tuple:
    for i in range(4):
        for j in range(6):
            if CARD_ORDER[i][j] == card:
                return (i,j)
    
def is_layout_correct(layout : list, hand : tuple) -> bool:
    for i in range(4):
        for j in range(6):
            if i == 3 and j == 5:
                continue
            if layout[i][j] != CARD_ORDER[i][j]:
                return False
    
    if layout[3][5] is not None:
        return False

    if hand != CARD_ORDER[3][5]:
        return False

    return True

def play_move(hand : tuple, layout : list, moves : list) -> tuple:
    x,y = target_card(hand)
    picked = layout[x][y] 
    layout[x][y] = hand

    moves.append({
            "was_in_hand": hand, 
            "where_it_moved": (x,y),
            "now_in_hand": picked
    })
  
    return picked

def play_game(predefined_deck) -> tuple[bool, list, list, list, tuple]:
    deck = predefined_deck[:]
    initial_deck = deck[:]

    layout, hand = create_layout(deck)
    moves = []

    max_moves = 23
    moves_count = 0

    while hand != CARD_ORDER[3][5]:
        hand = play_move(hand,layout,moves)
        moves_count += 1
        if moves_count > max_moves:
            return False, moves, initial_deck, layout, hand

    won = is_layout_correct(layout, hand)

    return won, moves, initial_deck, layout, hand

def load_deck_from_file(filepath : str) -> list:
    deck = []
    seen_cards = set()
    
    valid_cards_flat = [card for row in CARD_ORDER for card in row]

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise ValueError(f"Nie znaleziono pliku: {filepath}")

    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        
        parts = line.split()
        
        if len(parts) != 2:
            raise ValueError(f"Oczekiwano formatu: Kolor Figura")
        
        suit_str, val_str = parts[0], parts[1]

        if val_str.isdigit():
            val = int(val_str)
        else:
            val = val_str
        
        card = (suit_str, val)

        if card not in valid_cards_flat:
            raise ValueError(f"Nieistniejąca karta {card}")

        if card in seen_cards:
            raise ValueError(f"Duplikat karty {card}")
        
        seen_cards.add(card)
        deck.append(card)

    if len(deck) != 24:
        raise ValueError(f"Nieprawidłowa liczba kart: {len(deck)}")

    return deck