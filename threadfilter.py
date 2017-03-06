#Multithreaded prime number filter
from queue import Queue
import threading
#All processing threads
threads=[]
finished=False

def process(numberQueue,maxPrime):
    global threads
    global finished
    prime=numberQueue.get()
    print(threading.get_ident(),":",prime,end="\n")
    #if it is the last thread signal finished and return
    if len(threads)==maxPrime:
        finished=True
        return
    nextThread=createThread(maxPrime)
    #Filter numbers and continue sending to next thread
    #until last thread signals end
    while not finished:
        num=numberQueue.get()
        if num % prime !=0:
            nextThread.numberQueue.put(num)
        pass
    #Wait for nextThread to end before it does
    nextThread.join()

def createThread(maxPrime):
    numberQueue=Queue()
    nextThread=threading.Thread(target=process,args=(numberQueue,maxPrime))
    nextThread.numberQueue=numberQueue
    threads.append(nextThread)
    nextThread.start()
    return nextThread


#Start the program. maxPrime will be equal to subsequent threads
def domain(maxPrime):
    global finished
    firstthread=createThread(maxPrime)
    firstthread.numberQueue.put(2)
    firstthread.numberQueue.put(3)
    num=1
    while not finished:
        firstthread.numberQueue.put(6*num-1)
        firstthread.numberQueue.put(6*num+1)
        num=num+1
        pass
    firstthread.join()
    print("Over")
        
    
    
