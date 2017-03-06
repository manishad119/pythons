
from Crypto.Hash import SHA as SHA1
import struct
import os
import sys
from Crypto import Random
from Crypto.Cipher import AES
import man_secgen

MAGIC1=7865423 #Identifier 4 byte int at the head of file
MAGIC2=0x7865a35bfd3e2b09 #Identifier 8 byte encrypted with a random number at block
SEEK_BEGIN=0
SEEK_CURRENT=1
SEEK_END=2






#Pad data into multiples of 16 bytes to make it AES-encryptable data is mutable
def addPadding(data):
    if len(data)%16 ==0:
        return 0
    else:
        paddingamt=16-(len(data)%16)
        padding=Random.get_random_bytes(paddingamt)
        data.extend(padding)
        return paddingamt



#Encrypt each chunk of data. Data must be padded to a multiple of 16 
def encrypt_chunk(data,key,iv):
    aes=AES.new(key,AES.MODE_CBC,iv)
    return aes.encrypt(data)

    
#Encrypt srcFile into well formatted AES-encrypted dstFile using key obtained by
#SHA1 hash of pword
def encryptFile(srcFile,dstFile,pword):
    """Encrypt srcFile into well formatted AES-encrypted dstFile using key obtained by
    SHA1 hash of pword """
    
    src=open(srcFile,"rb",4096)
    dst=open(dstFile,"w+b",4096)
    key=man_secgen.getKey(pword)
    #print (" keylen =", len(key)," key=",key)
    # add MAGIC1 at the beginning of file
    dst.write(struct.pack("<I",MAGIC1))
    #Encrypted MAGIC2 follows.Used for quick password check
    magic2bytes=struct.pack("<Q",MAGIC2)
    padding=Random.get_random_bytes(8)
    plain=magic2bytes+padding
    #print (" magic ", plain)
    iv=Random.get_random_bytes(16)
    #print (" iv ", iv)
    aes=AES.new(key,AES.MODE_ECB)
    magicencr=aes.encrypt(plain)
    dst.write(magicencr)
    #write iv in plain text
    dst.write(iv)
    print (" magicencr ", magicencr)
    
    #leave space. We will remember the position and return here to write
    #the number of 4096 byte CBC chunks of 128 bit  AES blocks and the padding
    #in the last chunk encrypted plus the length of last encrypted chunk
    
    writepos=dst.tell()
    dst.seek(16,SEEK_CURRENT)
    #Encrypt with chunks of 4096 or filesize bytes using cbc of 128 bit AES blocks
    data=src.read(4096)
    blockcount=0
    padding=0
    #Length of last encrypted chunk
    len_last_chunk=4096
    hash1=SHA1.new()
    print("Encrypting..\r")
    while len(data)==4096:
        blockcount+=1
        
        hash1.update(data)
        print("Encrypting ",blockcount*4096," bytes \r")
        cipher=encrypt_chunk(data,key,iv)
        dst.write(cipher)
        data=src.read(4096)
        
        
    if len(data)>0:
        blockcount+=1
        #IMPORTANT: Since hash is calculated for original file content hash1 must
        #be updated before padding is added
        hash1.update(data)
        #Making data mutable to pad and then back to immutable to encrypt
        print("Encrypting ",blockcount*4096+len(data),"bytes \r")
        data=bytearray(data)
        padding=addPadding(data)
        data=bytes(data)
        cipher=encrypt_chunk(data,key,iv)
        len_last_chunk=len(cipher)
        
        dst.write(cipher)

    #160-bit SHA1 hash of the file contents are encrypted into two CBC AES blocks
    #and appended to the file
    print("Encryption completed")
    hashpad=Random.get_random_bytes(12)
    content_hash=hash1.digest()
    hash_plain=content_hash+hashpad
    aes=AES.new(key,AES.MODE_CBC,iv)
    hashencr=aes.encrypt(hash_plain)
    dst.write(hashencr)

    #Finally return to writepos to write the number of blocks and the padding in last
    #block plus the length of last encrypted chunk

    dst.seek(writepos,SEEK_BEGIN)
    aes=AES.new(key,AES.MODE_ECB)
    num_pad=struct.pack("<III",blockcount,padding,len_last_chunk)
    numpad1=Random.get_random_bytes(4)
    towrite=aes.encrypt(num_pad+numpad1)
    dst.write(towrite)

    ##Close the files

    src.close()
    dst.close()

#Print an error message  and close all files in case decryption fails
def fail_decryption(message,src,dst):
    src.close()
    fname=dst.name
    dst.close()
    os.remove(fname)
    print("Error: ",message,"\n Output file removed",file=sys.stderr)

#Decrypt each chunk of data. Data must be padded to a multiple of 16 
def decrypt_chunk(data,key,iv):
    aes=AES.new(key,AES.MODE_CBC,iv)
    return aes.decrypt(data)
    

#Decrypt well fornatted AES-encrypted srcFile into dstFile using key obtained by
#SHA1 hash of pword
def decryptFile(srcFile, dstFile ,pword):
    """Decrypt well formatted AES-encrypted srcFile into dstFile using key obtained by
    SHA1 hash of pword"""
    src=open(srcFile,"rb",4096)
    dst=open(dstFile,"wb",4096)
    key=man_secgen.getKey(pword)
    #Check if the first 4 bytes=MAGIC1. If it fails at this point then the
    #file is either corrupted or not the corrent file
    buf=src.read(4)
    (magic1,)=struct.unpack("<I",buf)
    if magic1!=MAGIC1:
        print (magic1, ":",MAGIC1)
        fail_decryption("File format not correct",src,dst)
        return
    
    #Check if the next 16 bytes is encrypted MAGIC2. If the decrypted extracted
    #number does not match with MAGIC2 then the entered password must be wrong
    aes=AES.new(key,AES.MODE_ECB)
    buf=src.read(16)
    bufplain=aes.decrypt(buf)
    (magic2,)=struct.unpack("<Q",bufplain[0:8])
    if magic2!=MAGIC2:
        fail_decryption("Wrong password", src, dst)
        return
    
    #Next 16 bytes is the iv
    iv=src.read(16)

    #Next 16 bytes consists of number of chunks and the padding for last block
    #encrypted as single block AES in EBC mode

    buf=src.read(16)
    aes=AES.new(key,AES.MODE_ECB)
    bufplain=aes.decrypt(buf)
    (blockcount,padding,len_last_chunk)=struct.unpack("<III",bufplain[0:12])

    #Do not bother if there is no data to decrypt

    if blockcount==0:
        return
    

    ##Start decrypting data and update hash for decrypted data for all chunks except
    # the last chunk
    hash1=SHA1.new()
    print("Decrypting..\r")
    for ind in  range(0,blockcount-1):
        cipher=src.read(4096)
        data=decrypt_chunk(cipher,key,iv)
        dst.write(data)
        hash1.update(data)
        print("Decrypting ",(ind+1)*4096, " bytes\r")

    #For the last chunk
    cipher=src.read(len_last_chunk)
    datapad=decrypt_chunk(cipher,key,iv)
    trim=len(datapad)-padding
    data=datapad[0:trim]
    dst.write(data)
    hash1.update(data)
    print ("Decryption completed..")

    ##Finally decrypt the hash and compare to calculated hash

    cipher=src.read(32)
    content_hash=hash1.digest()
    aes=AES.new(key,AES.MODE_CBC,iv)
    hash_dr=aes.decrypt(cipher)[0:20]
    #print(content_hash ," ", hash_dr)

    #Fail decryption if hash does not match

    if hash_dr>content_hash or content_hash>hash_dr:
        fail_decryption("Hash does not match. File is corrupted",src,dst)
        return

    ##Finally close the files
    src.close()
    dst.close()
           


           
    
    
    


    

    

    
    

    
    
                
                
                



        
        

    

    
        
    
    
    



    
    
    
    
    
        
