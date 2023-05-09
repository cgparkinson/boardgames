# TODO: integrate with pygame
import pygame

pygame.init()
bounds = (1024, 768)
window = pygame.display.set_mode(bounds)
pygame.display.set_caption("SnaPy")

from enum import Enum
import pygame
import random

class Suits(Enum):
  CLUB = 0
  SPADE = 1
  HEART = 2
  DIAMOND = 3

class Card:
  suit = None
  value = None
  image = None

  def __init__(self, suit, value):
    self.suit = suit
    self.value = value
    self.image = pygame.image.load('images/' + self.suit.name + '-' + str(self.value) + '.svg')

class Deck:
  cards = None

  def __init__(self):
    self.cards = []
    for suit in Suits:
      for value in range(1,14):
        self.cards.append(Card(suit, value))

  def shuffle(self):
    random.shuffle(self.cards)

  def deal(self):
    return self.cards.pop()

  def length(self):
    return len(self.cards)
  
class Pile:
  cards = None

  def __init__(self):
    self.cards = []

  def add(self, card):
    self.cards.append(card)

  def peek(self):
    if (len(self.cards) > 0):
      return self.cards[-1]
    else:
      return None

  def popAll(self):
    return self.cards

  def clear(self):
    self.cards = []

  def isSnap(self):
    if (len(self.cards) > 1):
      return (self.cards[-1].value == self.cards[-2].value)
    return False
  
class Player:
  hand = None
  flipKey = None
  snapKey = None
  name = None

  def __init__(self, name, flipKey, snapKey):
    self.hand = []
    self.flipKey = flipKey
    self.snapKey = snapKey
    self.name = name

  def draw(self, deck):
    self.hand.append(deck.deal())

  def play(self):
    return self.hand.pop(0)
  
class GameState(Enum):
  PLAYING = 0
  SNAPPING = 1
  ENDED = 2

class SnapEngine:
  deck = None
  player1 = None
  player2 = None
  pile = None
  state = None
  currentPlayer = None
  result = None

  def __init__(self):
    self.deck = Deck()
    self.deck.shuffle()
    self.player1 = Player("Player 1", pygame.K_q, pygame.K_w)
    self.player2 = Player("Player 2", pygame.K_o,pygame.K_p)
    self.pile = Pile()
    self.deal()
    self.currentPlayer = self.player1
    self.state = GameState.PLAYING

  def deal(self):
    half = self.deck.length() // 2
    for i in range(0, half):
      self.player1.draw(self.deck)
      self.player2.draw(self.deck)

  def switchPlayer(self):
    if self.currentPlayer == self.player1:
      self.currentPlayer = self.player2
    else:
      self.currentPlayer = self.player1

  def winRound(self, player):
    self.state = GameState.SNAPPING
    player.hand.extend(self.pile.popAll())
    self.pile.clear()

  def play(self, key):
    if key == None:
      return

    if self.state == GameState.ENDED:
      return
    
    if key == self.currentPlayer.flipKey:
      self.pile.add(self.currentPlayer.play())
      self.switchPlayer()

    snapCaller = None
    nonSnapCaller = None
    isSnap = self.pile.isSnap()

    if (key == self.player1.snapKey):
      snapCaller = self.player1
      nonSnapCaller = self.player2
    elif (key == self.player2.snapKey):
      snapCaller = self.player2
      nonSnapCaller = self.player1

    if isSnap and snapCaller:
      self.winRound(snapCaller)
      self.result = {
        "winner": snapCaller,
        "isSnap": True,
        "snapCaller": snapCaller
      }
      self.winRound(snapCaller)
    elif not isSnap and snapCaller:
      self.result = {
        "winner": nonSnapCaller,
        "isSnap": False,
        "snapCaller": snapCaller
      }
      self.winRound(nonSnapCaller)

    if len(self.player1.hand) == 0:
      self.result = {
        "winner": self.player2,
      }
      self.state = GameState.ENDED
    elif len(self.player2.hand) == 0:
      self.result = {
        "winner": self.player1,
      }
      self.state = GameState.ENDED

gameEngine = SnapEngine()

cardBack = pygame.image.load('images/BACK.png')
cardBack = pygame.transform.scale(cardBack, (int(238*0.8), int(332*0.8)))
def renderGame(window):
  window.fill((15,0,169))
  font = pygame.font.SysFont('comicsans',60, True)

  window.blit(cardBack, (100, 200))
  window.blit(cardBack, (700, 200))

  text = font.render(str(len(gameEngine.player1.hand)) + " cards", True, (255,255,255))
  window.blit(text, (100, 500))

  text = font.render(str(len(gameEngine.player2.hand)) + " cards", True, (255,255,255))
  window.blit(text, (700, 500))

  topCard = gameEngine.pile.peek()
  if (topCard != None):
    window.blit(topCard.image, (400, 200))

  if gameEngine.state == GameState.PLAYING:
    text = font.render(gameEngine.currentPlayer.name + " to flip", True, (255,255,255))
    window.blit(text, (20,50))

  if gameEngine.state == GameState.SNAPPING:
    result = gameEngine.result
    if result["isSnap"] == True:
      message = "Winning Snap! by " + result["winner"].name
    else:
      message = "False Snap! by " + result["snapCaller"].name + ". " + result["winner"].name + " wins!"
    text = font.render(message, True, (255,255,255))
    window.blit(text, (20,50))

  if gameEngine.state == GameState.ENDED:
    result = gameEngine.result
    message = "Game Over! " + result["winner"].name + " wins!"
    text = font.render(message, True, (255,255,255))
    window.blit(text, (20,50))



run = True
while run:
  key = None;
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      run = False
    if event.type == pygame.KEYDOWN:
      key = event.key

  gameEngine.play(key)
  renderGame(window)
  pygame.display.update()

  if gameEngine.state == GameState.SNAPPING:
    pygame.time.delay(3000)
    gameEngine.state = GameState.PLAYING
