class Card:
    def __init__(self, suit, value, image, x, y):
        self.suit = suit
        self.value = value
        self.image = image
        self.x = x
        self.y = y
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self,screen):
        screen.blit(self.image, self.rect)