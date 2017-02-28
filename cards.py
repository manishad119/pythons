
COLORS=["spade","diamond","heart","club"]
NUMBERS=["A",2,3,4,5,6,7,8,9,10,"J","Q","K"]

def enumcard(num):
    assert num in NUMBERS,"Invalid number"
    if num =="A":
        return 1
    elif num =="J":
        return 11
    elif num=="Q":
        return 12
    elif num=="K":
        return 13
    else :
        return num

def rankcard(num):
    assert num in NUMBERS, "Invalid number"
    if num =="A":
        return 14
    else :
        return enumcard(num)


def getNewDeck():
    listoflists= [[(col,num) for num in NUMBERS] for col in COLORS]
    deck=[]
    for list1 in listoflists:
        deck.extend(list1)
    return deck


def testfaras(player):
    faras=Faras(player)
    cards= faras.distribute()
    cardclassify=[Faras.classify_card(card) for card in cards]
    for (card,data) in zip(cards,cardclassify):
        print(card,"\n",data,"\n\n")
    print("Winner is ",Faras.getWinner(cardclassify))


    
              
    



from Crypto.Random import random

class Faras:

    #levels in Faras

    LEVELS=["top","dual","color","run","dblrun","trial"]

    def __init__(self,numofplayer):
        "Constructor of new faras game"
        assert numofplayer>1 and numofplayer<=17, "Error: must have between 2 and 17 players"
        self.numofplayer=numofplayer
        self.deck=getNewDeck()
        random.shuffle(self.deck)

    def distribute(self):
        "Distribute cards among players in the game"
        raw_list=[]
        for rounds in range(0,3):
            roundcardlist=[]
            for players in range(0,self.numofplayer):
                roundcardlist.append(self.deck.pop())
            raw_list.append(roundcardlist)
        return [(en,card1,card2,card3) for ((en,card1),card2,card3) in zip(enumerate(raw_list[0]),raw_list[1],raw_list[2])]

        
    @staticmethod
    def getWinner(cardclassify):
        if len(cardclassify)<2:
            return cardclassify[0]["num"]
        maxm=-1
        for ind in range(0,len(cardclassify)):
            if maxm==-1:
                maxm=ind
            else :
                maxm=Faras.compare_cards(cardclassify[maxm],cardclassify[ind])
        return maxm
                    
        
        
        
    
    # analyse the cards used for comparison and return data about the combination
    @staticmethod
    def classify_card(card_tuple):
        "Static method: classify a combination of three cards in faras type and other relevent data for comparison"
        data={"num":card_tuple[0]}
        card1=card_tuple[1]
        card2=card_tuple[2]
        card3=card_tuple[3]
        hascolor=False
        
        #Check for trial and presence of color
        if card1[1]==card2[1] and card2[1]==card3[1]:
            data["type"]="trial"
            data["high"]=rankcard(card1[1])
            return data
        elif card1[0]==card2[0] and card2[0]==card3[0]:
            hascolor=True

        #Sort the card ranks and detect duals or sequences
        card_list=[card1,card2,card3]
        num_list=[rankcard(num) for (col,num) in card_list]
        num_list.sort()

        #Look for sequence
        hassequence=False

        if num_list[1]-num_list[0]==1 and num_list[2]-num_list[1]==1:
            hassequence=True
            data["high"]=num_list[2]
            if num_list[2]==14:
                data["langadi"]=False
        elif num_list[0]==2 and num_list[1]==3 and num_list[2]==14:
            hassequence=True
            data["high"]=14
            data["langadi"]=True

        #Classify as run or dblrun for sequences
        if hascolor and hassequence:
            data["type"]="dblrun"
            return data
        elif hassequence:
            data["type"]="run"
            return data

        #Look for dual
        if num_list[0]==num_list[1]:
            data["type"]="dual"
            data["dbl"]=num_list[0]
            data["sgl"]=num_list[2]
            return data
        elif num_list[1]==num_list[2]:
            data["type"]="dual"
            data["dbl"]=num_list[2]
            data["sgl"]=num_list[0]
            return data

        #Write cards for other types
        data["high"]=num_list[2]
        data["mid"]=num_list[1]
        data["low"]=num_list[0]

        if hascolor :
            data["type"]="color"
        else :
            data["type"]="top"
        return data
        
    #return num for card with higher high       
    @staticmethod
    def compare_trial(card_data1,card_data2):
        high1=card_data1["high"]
        high2=card_data2["high"]
        if high1>high2:
            return card_data1["num"]
        elif high2>high1:
            return card_data2["num"]
        else :
            return -1 #This should be impossible but just in case

    
    @staticmethod
    def compare_sequence(card_data1,card_data2):
        high1=card_data1["high"]
        high2=card_data2["high"]
        if high1>high2:
            return card_data1["num"]
        elif high2>high1:
            return card_data2["num"]
        else:
            #If high is A then check if one of them is langadi and return the other one
            #If both are same (langadi or not) return -1
            if high1==14:
                if card_data1["langadi"] and not card_data2["langadi"]:
                    return card_data2["num"]
                elif not card_data1["langadi"] and card_data2["langadi"]:
                    return card_data1["num"]
                else:
                    return -1

    
    @staticmethod
    def compare_top(card_data1,card_data2):
        high1=card_data1["high"]
        high2=card_data2["high"]
        num1=card_data1["num"]
        num2=card_data2["num"]
        mid1=card_data1["mid"]
        mid2=card_data2["mid"]
        low1=card_data1["low"]
        low2=card_data2["low"]

        if high1>high2:
            return num1
        elif high2>high1 :
            return num2

        if mid1>mid2:
            return num1
        elif mid2>mid1:
            return num2

        if low1>low2:
            return num1
        elif low2>low1:
            return num2
        else :
            return -1

    @staticmethod
    def compare_dual(card_data1,card_data2):
        dbl1=card_data1["dbl"]
        dbl2=card_data2["dbl"]
        sgl1=card_data1["sgl"]
        sgl2=card_data2["sgl"]
        num1=card_data1["num"]
        num2=card_data2["num"]

        if dbl1>dbl2:
            return num1
        elif dbl2>dbl1:
            return num2

        if sgl1>sgl2:
            return num1
        elif sgl2>sgl1:
            return num2
        else :
            return -1
                
                         
    
    
    #compare two combinations and return the enum of stronger one. If both have same strength
    #return -1
    @staticmethod
    def compare_cards(card_data1,card_data2):
        num1=card_data1["num"]
        num2=card_data2["num"]
        type1=card_data1["type"]
        type2=card_data2["type"]
        if Faras.LEVELS.index(type1)>Faras.LEVELS.index(type2):
            return num1
        elif Faras.LEVELS.index(type2)>Faras.LEVELS.index(type1):
            return num2
        else :
            if type1=="trial":
                return Faras.compare_trial(card_data1,card_data2)
            elif type1=="run" or type1=="dblrun":
                return Faras.compare_run(card_data1,card_data2)
            elif type1=="top" or type1=="color":
                return Faras.compare_top(card_data1,card_data2)
            elif type1=="dual":
                return Faras.compare_dual(card_data1,card_data2)
            else:
                return -1

import sys
    
class ChaliFaras(Faras):
    
    "The game of chali faras, the main type of faras"

    class ChaliFarasPlayer:
        "Someone to play ChaliFaras"

        PLAYERSTATES=["blind","open","quit"]

        def __init__(self,name,card,initial,state="blind"):
             assert state in ChaliFaras.ChaliFarasPlayer.PLAYERSTATES,"Invalid state"
             self.name=name
             self.card=card
             self.bets=[initial]
             self.state=state

        def bet(self,amount):
            assert self.state!="quit","Error: quit player %s bets"%self.name
            self.bets.append(amount)
            
        #Look at the card and get its relevant data after classification
        def seecard(self):
            assert self.state=="blind","Error:only blind player can open"
            self.state="open"
            self.card_data=Faras.classify_card(self.card)
            print(self.card,"\n",self.card_data)
            return self.card

        def quit(self):
            assert self.state=="open","Error,only open player can quit"
            self.state="quit"

        
         

    def __init__(self,playernames,initial,turn):
         """Initialize the game and does distribution starting the game.
         The players are given with the initial bet and the first better
         """
         Faras.__init__(self,len(playernames))
         self.initial=initial
         cards=self.distribute()
         self.playernames=playernames
         self.blindnum=len(playernames)
         self.remaining=len(playernames)
         #First player to start
         assert turn in playernames,"Error no player %s"%turn
         self.turn=turn
         #Make a dictionary of player names with their respective player objects
         players=[ChaliFaras.ChaliFarasPlayer(name,card,initial) for name,card in zip(playernames,cards)]
         self.players=dict(zip(playernames,players))
         

    def bet(self,playername,amount):
        "Player bets"
        assert playername in self.playernames,"Error: no player %s"%playername
        self.players[playername].bet(amount)

    def quit(self,playername):
        "Player quits"
        assert playername in self.playernames,"Error: no player %s"%playername
        self.remaining-=1
        self.players[playername].quit()
        if self.remaining==1:
            self.turn=playername
            assert self.nextTurn()==playername
            self.winner=self.nextTurn()
            self.endgame()
            

    def seecard(self,playername):
        "Player sees card"
        assert playername in self.playernames,"Error: no player %s"%playername
        self.blindnum-=1
        return self.players[playername].seecard()

    #This means next person to do action
    #The game itself does not enforce turns and is the job of using
    #module (e.g. the game server) to make sure it works
    def nextTurn(self):
        "The player who will play next"
        thisturn=self.turn
        nextindex=self.playernames.index(thisturn)
        nextindex=(nextindex +1)%len(self.playernames)
        
        #Skip players that have quit
        while self.players[self.playernames[nextindex]].state=="quit":
            nextindex=(nextindex+1)%len(self.playernames)

        self.turn=self.playernames[nextindex]
        
        return thisturn

    #A player does show. Showing player must bet a minimum amount
    #If showing player has stronger than the rest, he/she wins
    #If showing player ties with someone for the strongest card, shower loses
    #For the remaining players one closest to shower gets priority for tie

    def show(self,playername,amount):
        "Show cards to end the game with a bet"
        assert playername in self.playernames,"Error:no player %s"%playername
        showplayer=self.players[playername]
        if showplayer.state=="open" and self.blindnum>0:
            print("You cannot show while there are blind players",file=sys.stderr)
            return
        self.bet(playername,amount)
        if showplayer.state=="blind":
            self.seecard(playername)
        #See your card
        #For each remaining members compare the shower's card and the current
        #winning card and get a winner
        winning_card=showplayer.card_data
        winner=playername
        foundstronger=False
        #make sure of it starts right after you
        self.turn=playername
        assert self.nextTurn()==playername
        nextplayer=self.nextTurn()
        while nextplayer!=playername:
            if self.players[nextplayer].state=="blind":
                #The blind one gotta see card first
                self.seecard(nextplayer)
            nextcard=self.players[nextplayer].card_data
            strongernum=Faras.compare_cards(winning_card,nextcard)
            #If we get the stronger than current winning card or ties
            #with the shower for the strongest card, the winning card is
            #nextcard
            if strongernum==nextcard["num"] or (strongernum<0 and not foundstronger):
                foundstronger=True
                winner=nextplayer
                winningcard=nextcard               
            nextplayer=self.nextTurn()

        #Set the winner and return
        self.winner=winner
        self.endgame()

    def endgame(self):
        self.winsum=sum([sum(self.players[player].bets) for player in self.players]) 
        print("The winner is %s sum of %d"%(self.winner,self.winsum))
        
        
        

    


    


    
         
         

    
     
        
        

    

                
            
                
            
        
    

    
    
    
    

