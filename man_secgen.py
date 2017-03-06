from Crypto.Hash import SHA256
from Crypto.Hash import SHA512
from Crypto.Random import random

#Common public exponent
e=65537

#Hash password into encryption key
def getKey(password):
    hash1=SHA256.new()
    hash1.update(password.encode("utf-8"))
    #hexall=lambda d: reduce(lambda x,y:x+y,map(hex,d))
    digest=hash1.digest()
    key=[digest[i]^digest[i+16] for i in range(16)]
    return bytes(key)

#Extended euclidean algorithm code copied from wikibooks
def xgcd(b, n):
    x0, x1, y0, y1 = 1, 0, 0, 1
    while n != 0:
        q, b, n = b // n, n, b % n
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
    return  b, x0, y0

#Modular inverse code copied from wikibooks
def mulinv(b, n):
    g, x, _ = xgcd(b, n)
    if g == 1:
        return x % n


#Compute 2048-bit RSA key pair from username and password

def getKeys(username,password):
    """Compute RSA key pair from username and password
    
    While the algorithm may not be completely deterministic by itself,
    the probability that it gives a non-deterministic result~probability
    that one or both of the numbers are composite=PK=1-(1-2**(-100))**2
    ~1.588e-30 every time, Probability that there is at least one
    non-deterministic result instance out of k runs=1-(1-PK)**k~k*(1-PK)**k-1*PK
    which is still very low since k is rarely above 10000.
    For 10000 runs, it is about as high as guessing an 85-bit number correctly"""

    #since ':' is an illegal character for a username not allowing same username
    #almost certainly gives different RSA keys for different people
    startstring=username+":"+password
    startseq=startstring.encode()
    gen=NumberGenerator(startseq)
    primes=[]
    #Keep generating prime numbers until we have two prime numbers p
    #such that (p-1) % e!=0
    while len(primes)<2:
        num=gen.generate(1024)
        p=firstProbPrimeAfter(num,100)
        #Accept if p-1 is co-prime to e
        if (p-1) % e !=0:
            primes.append(p)
    p,q=primes[0],primes[1]
    phi=(p-1)*(q-1)
    d=mulinv(e,phi)
    #N=p*q where N,e is public key and N,d is private key
    return (p*q,e,d)



def gcd(a,b):
    if a>b: a,b=b,a
    while b%a !=0:
        a,b=b%a,a
    return a

def jacobi(a,n):
    if n%2==0 or n<0:
        #print(n)
        raise Exception("Invalid n: must be positive odd integer")
    if a==1 or n==1:return 1
    if a>n: a=a%n
    if a==0:return 0
    pack=1
    #Loop forever. It should eventually return
    while True:
        #Extract factors of 2 from a
        packing=(n%8==3 or n%8==5)
        #print("During entry a=%d n=%d"%(a,n))
        while a%2==0:
            if packing: pack*=-1
            a=a//2
        if a==1: return pack
        elif gcd(a,n)!=1: return 0
        if a%4==3 and n%4==3: pack*=-1
        #print("During exit a=%d n=%d"%(a,n))
        a,n=n%a,a
        



def ssPrimalityTestOnce(num):
    "Test once for solovay-strassen primality test on num"
    if num<2: raise Exception("num must be >=2")
    if num==2 or num==3: return True
    a=random.randint(2,num-1)
    jac=jacobi(a,num)
    return jac!=0 and pow(a,(num-1)//2,num)==jac % num

def ssProbPrime(num,k):
    """Test num for solovay-strassen primality test n times such that
    Prob(num is composite/returns True)==2*(-k)"""
    if k<1: raise Exception("k must be >=1")
    if num==2 or num==3: return True
    if num%5==0: return False
    for s in range(0,k):
        if not ssPrimalityTestOnce(num) :return False
    return True
    

#Using Solovay-Strassen primality test to find first probable prime after num
#with composite probability of 2**(-k)
def firstProbPrimeAfter(num,k):
    """Uses Solovay-Strassen primality test to find first probable prime after num
    . Has compositeness probability of 2**-k"""
    #Test all numbers >=num of the form 6n+5 or 6n+1 after num until one probable
    #prime of degree k is found
    mod,n=num%6,num//6
    #print("num=",num,"\n")
    if mod<=1:
        num+=(1-mod) #If mod is 0 add 1 if mod is 1 do nothing
        if ssProbPrime(num,k) :return num
    #print("num=",num,"\n")
    
    num=6*n+5
    #print("num=",num,"\n")
    if ssProbPrime(num,k):return num
    #Loop until one prime is found
    num+=2
    while True:
        if ssProbPrime(num,k): return num
        num+=4
        if ssProbPrime(num,k): return num
        num+=2
    


def testfunc(uname,password):
    print("Nothing")
    print("%s %s"%(uname,password))
    print("Calculating key.. Please wait")
    (N,pub,pri)=getKeys(uname,password)
    print ("key (%d,%d,%d)\n"%(N,pub,pri))
    plain=random.randint(2,N-1)
    cipher=pow(plain,pub,N)
    decr=pow(cipher,pri,N)
    
    print ("plain: ",plain,"\n")
    print("cipher: ",cipher, "\n")
    print("decr: ",decr,"\n")
    pass

#Hash based (SHA512) cryptographically secure yet deterministic prng
class NumberGenerator:
    """Generates a n-bit n%256=0 cryptographically secure psudorandom
    deterministic to the seed using SHA512 hash. I use it for calculating
    large (e.g. RSA) keys from passwords etc. The first bit of the generated
    number is set to 1"""

    def __init__(self,seed):
        "Start with an arbitrary sized seed"
        self.state=seed

    def generate(self,nbits):
        "Generate next nbits-bit integer where nbits % 256==0 with first bit 1"
        if nbits % 256 !=0:
            print ("Number of bits must be a multiple of 256",file=sys.stderr)
            return 0
        rounds=nbits //256
        data=b""
        for i in range(rounds):
            sha512=SHA512.new(self.state)
            shadigest=sha512.digest()
            #For the first one make sure the first bit is 1
            if i==0:
                aslist=list(shadigest)
                aslist[0]|=0x80
                shadigest=bytes(aslist)
            data+=shadigest[0:32]
            self.state=shadigest[32:]
        #Compute big-endian hex string from the bytes object and parse it
        return int(data.hex(),base=16)



            
        
            
    
    
    

