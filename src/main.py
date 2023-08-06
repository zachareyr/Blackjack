import random
import sys
import time
from colorama import Fore, Style

flush = f"{Fore.RESET}{Style.RESET_ALL}"

class Utils:
    # turns a list [val1, val2] into a string "val1, val2"
    def list_to_comma_str(list):
            s = ""
            for i in list:
                s += f"{str(i)}, "
            return s[:-2]
    
    # applies a function to all members of a list
    def map(list, fn):
        list2 = []
        for i in list:
            list2.append(fn(i))
        return list2

    # gets the numerical value of a card, and prompts the user to select high or low if the card is an ace    
    def get_value(card, p=None):
            if p is None:
                p = ""
            if card[1] == "Ace":
                if Utils.options(f"{p}: You got an ace. Would you like to play high or low? {flush}", [["high", "h"], ["low", "l"]], fail_prompt=f"{p}: Invalid input. Type high or low.{flush}") == 0:
                    return 11
                else:
                    return 1
            elif card[1] in ["Jack", "King", "Queen"]:
                return 10
            else:
                return int(card[1])
    
    # keeps prompting the user with [prompt], until they input a valid option from [lops]. If input isn't valid, types [fail_prompt] or [prompt] if no [fail_prompt] is supplied
    def options(prompt, lops, fail_prompt = None):
        while True:
            inp = input(prompt).lower()
            for i in range(len(lops)):
                if inp in Utils.map(lops[i], lambda x: x.lower()):
                    return i
            else:
                if fail_prompt is not None:
                    print(fail_prompt)
                else:
                    print(prompt)

class Game:
    def __init__(self) -> None:
        self.starting_amount = self.get_starting_money()
        self.players = self.get_players()
        self.deck = []
        self.dealer_hand = 0
        self.dealer_hand_list = []

    # prompts to select the starting money for the players
    def get_starting_money(self) -> None:
        money = 100
        if Utils.options(f"The starting money for each player is {money}. Is this okay? ", [["yes", "y"], ["no", "n"]], "Yes or no.") == 0:
            return money
        
        while True:
            try:
                money = int(input("Input starting amount "))
            except ValueError:
                print("Money must be an integer")
            else:
                if money < 0:
                    print("You cannot start with negative money.")
                elif money == 0:
                    print("You cannot start with nothing.")
                else:
                    return money
    
    # prompts to choose number of players and the names of players
    def get_players(self) -> None:
        while True:
            try:
                num_players = int(input("How many players? "))
            except ValueError:
                print("Player count must be an integer")
            else:
                if num_players < 0:
                    print("You cannot have negative players.")
                elif num_players == 0:
                    print("You cannot have no players.")
                elif num_players > 4:
                    print("Maximum number of players is 4.")
                else:
                    break
        
        colors = [Fore.RED, Fore.GREEN, Fore.BLUE, Fore.YELLOW]
        players = []
        for i in range(num_players):
            name = input(f"{colors[i]}Enter name of player. ")
            if name == "":
                name = f"Player{i}"
            
            players.append(Player(self.starting_amount, name, colors[i]))
        return players
    
    # shuffles the deck
    def shuffle_deck(self):
        deck = [] 
        for i in ["Spades", "Hearts", "Diamonds", "Clubs"]:
            for j in ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"]:
                deck.append([f"{j} of {i}", Utils.get_value([i, j]) if j != "Ace" else "Ace"])
        random.shuffle(deck)
        self.deck = deck
    
    # gets every player's bet, ignoring people with no money
    def get_bets(self):
        for p in self.players:
            # if the player is out of money (from >=1 round ago), ignore them
            if p.status == 3:
                continue
            # if the player is out of money (starting this round), mark them as out
            elif p.money == 0:
                print(f"{p}: Out of money! You're out!{flush}")
                p.status = 3
            # otherwise, let them place a valid integer bet
            else:
                while True:
                    try:
                        bet = int(input(f"{p}: What would you like to bet?{flush} "))
                    except ValueError:
                        print(f"{p}: Invalid value for bet")
                    else:
                        if bet < 0:
                            print(f"{p}: You cannot bet negative amounts.{flush}")
                        elif bet == 0:
                            print(f"{p}: You cannot bet nothing.")
                        elif bet > p.money:
                            print(f"{p}: You don't have that much, limit your bets to ${p.money}.{flush}")
                        else:
                            p.bet = bet
                            print(f"{p}: You are betting ${bet}.{flush}")
                            break
    
    def action(self, player):
        # if the player is not drawing, ignore them
        if player.status != 0:
            return
        
        print(f"{player}: Your hand is {Utils.list_to_comma_str(player.hand_list)} (value {player.hand}).{flush}")
       
        next_step = Utils.options(f"{player}: What would you like to do? ", [["stand", "s"], ["hit", "h"]], "Stand or hit?")
        if next_step == 0:
            print(f"{player} has stood. Their hand is {Utils.list_to_comma_str(player.hand_list)} (value {player.hand}).{flush}")
            player.status = 1
            return
        elif next_step == 1:
            card = self.deck.pop(0)
            player.hand_list.append(card[0])
            val = Utils.get_value(card, player)
            if val == 1:
                player.hand_list[-1] += " (low)"
            elif val == 11:
                player.hand_list[-1] += " (high)"
            player.hand += val
            print(f"{player}: Your card is: {card[0]}. Your new hand is: {Utils.list_to_comma_str(player.hand_list)} (value {player.hand}).{flush}")
            
            if player.hand > 21:
                print(f"{player}: You bust!{flush}")
                player.status = 2
            elif player.hand == 21:
                print(f"{player} has blackjack.{flush}")
                player.status = 1

    def get_starting_hand(self, player=None):
        if player is None:
            self.dealer_hand = 0
            self.dealer_hand_list = []
            visible_hand = 0
            cards = [self.deck.pop(0), self.deck.pop(0)]
            self.dealer_hand_list = [cards[0][0], cards[1][0]]
            for i in cards:
                if i[1] == "Ace":
                    if visible_hand == 0:
                        visible_hand += 11
                    self.dealer_hand += 11
                else:
                    if visible_hand == 0:
                        visible_hand += Utils.get_value(i)
                    self.dealer_hand += Utils.get_value(i)
            print(f"The dealer has drawn their 2 cards. They lay a {self.dealer_hand_list[0]} down (value {visible_hand}).{flush}")
            return
        
        # if the player held or busted, reset their hand
        if player.status == 1 or player.status == 2:
            player.status = 0
        # if the player has no money, ignore them
        elif player.status == 3:
            return
        
        player.hand = 0
        player.hand_list = []

        cards = [self.deck.pop(0), self.deck.pop(0)]
        player.hand_list = [cards[0][0], cards[1][0]]
        print(f"{player}: Your starting deck is: {player.hand_list[0]} and {player.hand_list[1]}{flush}")
        for i in cards:
            player.hand += Utils.get_value(i, player)
        if player.hand == 21:
            print(f"{player} has a natural blackjack.{flush}")
            player.status = 2

    # runs 1 hand                     
    def run_hand(self):
        def turns_remaining():
            for i in self.players:
                if i.status == 0:
                    return True
            return False
        
        self.shuffle_deck()
        self.get_bets()

        tmp = False
        for p in self.players:
            if p.status != 3:
                tmp = True
        if not tmp:
            print(f"{flush}All players are out of money.")
            sys.exit()
        # get the dealer's starting hand
        self.get_starting_hand()
        # get the players' starting hands
        for p in self.players:
            if p.status != 3:
                tmp = True
            self.get_starting_hand(p)
        
        # run all player turns
        while turns_remaining():
            for p in self.players:
                self.action(p)

        # finish the dealer's hand
        dealer_draws = 0
        while self.dealer_hand <= 17:
            card = self.deck.pop(0)
            self.dealer_hand_list.append(card[0])
            if card[1] == "Ace":
                if self.dealer_hand <= 10:
                    self.dealer_hand += 11
                    self.dealer_hand_list[-1] += " (high)"
                else:
                    self.dealer_hand += 1
                    self.dealer_hand_list[-1] += " (low)"
            else:
                self.dealer_hand += Utils.get_value(card)
            dealer_draws += 1
        
        print(f"The dealer draws {dealer_draws} more cards, and then turns them over.")
        print(f"The dealer's hand was {Utils.list_to_comma_str(self.dealer_hand_list)} (value {self.dealer_hand}).{flush}")
        if self.dealer_hand > 21:
            print(f"The dealer busts. All players that didn't bust win.")
            self.dealer_hand = -1
        elif self.dealer_hand == 21:
            print(f"The dealer has blackjack.")
        for p in self.players:
            if p.status == 3:
                print(f"{p} is out.")
            else:
                if p.status == 2:
                    print(f"{p} busts with a value of {p.hand}. They lose{flush}")
                    p.money -= p.bet
                elif p.hand < self.dealer_hand:
                    print(f"{p}'s hand value is {p.hand}. They lose.{flush}")
                    p.money -= p.bet
                elif p.hand == self.dealer_hand:
                    # push = you get your bet back, no change to your money
                    print(f"{p} ties with {p.hand}. They push.{flush}")
                else:
                    print(f"{p}'s hand value is {p.hand}. They win.{flush}")
                    p.money += p.bet
                print(f"{p} now has ${p.money}.{flush}")
        input(f"Press enter to continue. ")
        return 1
     
        

class Player:
    status_strs = ["is playing", "has stood", "has bust", "is out"]
    def __init__(self, starting_money, name, color) -> None:
        self.money = starting_money
        self.name = name
        self.color = color
        self.hand = []
        self.hand_list = []
        self.bet = -1

        # 0: playing, 1: stood, 2: busted, 3:out
        self.status = 0

    def get_status(self):
        return f"{self.name} {Player.status_strs[self.status]}"
    
    def __str__(self):
        if self.status == 0:
            return f"{self.color}{self.name}"
        if self.status == 1 or 2:
            return f"{self.color}{Style.DIM}{self.name}"  
    
def main():
    game = Game()
    while True:
        game.run_hand()

if __name__ == "__main__":
    main()