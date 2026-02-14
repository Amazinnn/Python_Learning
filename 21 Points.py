# 21 Points

import random

class Card :
    """牌"""
    
    def __init__(self,face):
        self.face = face

    def __repr__(self):
        faces = ['','A','2','3','4','5','6',
                 '7','8','9','10','J','Q','K']
        return f"{faces[self.face]}"


class Poker :
    """扑克"""

    def __init__(self):
        self.cards = [Card(face)
                      for _ in range(4)
                      for face in range(1,14)]
    
        
    def shuffle(self):
        self.current = 0
        random.shuffle(self.cards)
        random.shuffle(self.cards)

    def deal(self):
        if self.has_next():
            card = self.cards[self.current]
            self.current += 1
            return card
        else :
            return None

    def has_next(self):
        return self.current < len(self.cards)


class Player:
    """玩家"""

    def __init__(self,name):
        self.cards = []
        self.name = name
        self.is_bust = False
        

    def hit(self,card):
        print(f"{self.name.title()} hits {str(card)}.")
        self.cards.append(card)

    def __repr__(self):
        return f"{self.name.title()}: {[str(card) for card in self.cards]} (Points：{self.calc()})"

    def calc(self):
        value = 0
        ace_count = 0
        for card in self.cards :
            if card.face in (11,12,13):
                value +=10
            elif card.face == 1 :
                ace_count +=1
                value+=10
            elif 2 <= card.face <= 10 :
                value += card.face
            else :
                pass
        while value >21 and ace_count > 0 :
            value -=9
            ace_count -=1
        return value

    def stand(self):
        print(f"{self.name.title()} stands.\n")


class Dealer:
    """庄家"""

    def __init__(self,name):
        self.name = name
        self.cards = []
        self.hole_up_card = True
        self.is_bust = False

    def hit(self,card):
        self.cards.append(card)
        if len(self.cards) == 1:
            print(f"{self.name.title()} hits *.")
        else :
            print(f"{self.name.title()} hits {str(card)}.")

    def __repr__(self):
        cardlist = ""
        if self.hole_up_card and len(self.cards) > 0 :
            return f"{self.name.title()}: [*] {[str(card) for card in self.cards[1:]]}"
        else :
            return f"{self.name.title()}:{[str(card) for card in self.cards[:]]}(Points：{self.calc()})"

    def calc(self):
        value = 0
        ace_count = 0
        for card in self.cards :
            if card.face in (11,12,13):
                value +=10
            elif card.face == 1 :
                ace_count +=1
                value+=10
            elif 2 <= card.face <= 10 :
                value += card.face
            else :
                pass
        while value >21 and ace_count > 0 :
            value -=9
            ace_count -=1
        return value
    
    def stand(self):
        print(f"{self.name.title()} stands.")

    def face_up_card(self):
        self.hole_up_card = False
        print(f"{self.name.title()} has his card face-up.")


if __name__ == "__main__":
    # 创建一副牌并洗牌
    poker = Poker()
    poker.shuffle()
    
    # 创建玩家和庄家
    player = Player(input("Please enter the player's name:"))
    dealer = Dealer(input("Please enter the dealer's name:"))
    print("\n")
    
    # 发牌
    player.hit(poker.deal())
    player.hit(poker.deal())
    dealer.hit(poker.deal())
    dealer.hit(poker.deal())
    
    print("\n初始状态：")
    print(player)
    print(dealer)  # 应该显示一张暗牌
    
    while True :
        if 0 == int(input(f"\nDo you want to stand(enter 0) or hit(enter 1)?")):
            player.stand()
            break
        else :
            player.hit(poker.deal())
            print(player)
            if player.calc() > 21 :
                player.is_bust = True
                break

    if player.is_bust == False :
        dealer.face_up_card()
        print(dealer)
        while dealer.calc() <17 :
            dealer.hit(poker.deal())
            print(dealer)

    if dealer.calc() >21 :
        dealer.is_bust = True

    if player.is_bust == True :
        print(f"\n{dealer.name.title()} wins!")
    elif dealer.is_bust == True :
        print(f"\n{player.name.title()} wins!")
    elif player.calc() > dealer.calc():
        print(f"\n{player.name.title()} wins!")
    elif player.calc() < dealer.calc():
        print(f"\n{dealer.name.title()} wins!")
    else :
        print("\nGame pushs!")
