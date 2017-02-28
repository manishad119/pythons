DICES=["spade","club","langur","diamond","burja","heart"]

from Crypto.Random import random
class LangurBurjaGame:

    def __init__(self):
        "Initialize the game and roll the dice"
        self.bets={}
        self.dices=[random.choice(DICES) for _any in range(6)]
        self.dicenum=dict([(dice,self.dices.count(dice)) for dice in DICES ])


    def bet(self,playername,figure,amount):
        "Betting in langurburja"
        assert figure in DICES,"No figure %s"%figure
        if playername not in self.bets:
            self.bets[playername]=[(figure,amount)]
        else :
            self.bets[playername].append((figure,amount))


    def open(self):
        "Open results"
        self.result={}
        print(self.dices,"\n")
        print(self.dicenum,"\n")
        for player in self.bets:
            bets,playersum=self.bets[player],0
            for figure,amount in bets:
                if self.dicenum[figure]<2:
                    playersum-=amount
                else :
                    playersum+=self.dicenum[figure]*amount
            self.result[player]=playersum
        print(self.result)


    

        
            
        
        
        



