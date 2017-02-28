
#from functools import reduce

def getprimes(high):
    "get all primes from 2 to high"
    if high<2:
        return []
    elif high==2:
        return [2]
    else :
        list1=range(3,high+1,2)
        result=[2]
        while len(list1)>0:
            num=list1[0]
            result.append(num)
            list1=[x for x in list1[1:] if x % num!=0]
            
            
        return result

def fibonacci(num):
    "Get fibonacci function of num"
    if num<0:
        pass
    if num==0:
        return 0
    elif num==1:
        return 1
    else :
        a11,a12,a21,a22,n1,n2=0,1,1,1,0,1
        num-=1
        while num>0:
            if num % 2 !=0:
                n1,n2,num=a11*n1+a12*n2,a21*n1+a22*n2,num-1
            else :
                a11,a12,a21,a22,num=a11*a11+a12*a21,a11*a12+a12*a22,a21*a11+a22*a12,a21*a12+a22*a22,num/2
        return n2








                
                
        
     

        
