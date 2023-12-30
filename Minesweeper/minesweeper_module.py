import pygame
DARK_GREEN = (0,200,0)
DARK_SILVER = (113,112,117)
GREEN = (0, 255, 0)
SILVER = (192, 192, 192)
RED = (255,0,0)
DARK_RED = (139, 0, 0)
class Squares:
           
    def __init__(self,color,x,y,side):
        self.color = color
        self.x = x
        self.y = y
        self.side = side
    def display(self,screen):
        pygame.draw.rect(screen, self.color , pygame.Rect((self.x,self.y),(self.side,self.side)))
        if self.color == GREEN:
            pygame.draw.rect(screen,DARK_GREEN,pygame.Rect((self.x,self.y),(self.side,self.side)),2)
        elif self.color == SILVER:
            pygame.draw.rect(screen,DARK_SILVER,pygame.Rect((self.x,self.y),(self.side,self.side)),2)
        elif self.color == RED:
            pygame.draw.rect(screen,DARK_RED,pygame.Rect((self.x,self.y),(self.side,self.side)),2)
        
class Lines:
    def __init__(self,color,x,y,thickness,square_size):
        self.color=color
        self.x=x
        self.y=y
        self.thickness = thickness
        self.square_size= square_size
    def display(self,screen):
        pygame.draw.line(screen, self.color, (self.x, self.y), (self.x + self.square_size, self.y + self.square_size),self.thickness)
        pygame.draw.line(screen, self.color, (self.x, self.y + self.square_size), (self.x + self.square_size, self.y),self.thickness)
        
class Numbers:
    def __init__(self,text,x,y,color,background_color,font):
        self.text = text
        self.x= x
        self.y = y
        self.color = color
        self.BGC = background_color
        self.font = font
    def display(self,screen,square_size):
        text = self.font.render(self.text, True, self.color)
        text_rect = text.get_rect(center=(self.x+square_size//2,self.y+square_size//2))
        screen.blit(text, text_rect)
        
        
    