from urllib.request import urlopen
links=open('qakbot_link.txt','r').read()
links=links.split()
count=0
leftover=open('leftover.txt','w')
for x in links:
    try:
        myConnection = urlopen(x).read()
        png_header=bytes.fromhex('25504446')
        if png_header in myConnection:
            file=open(f'qakbot_{count}.pdf','wb')
            file.write(myConnection)
            file.close()
        else:
            file=open(f'qakbot_{count}.html','wb')
            file.write(myConnection)
            file.close()
        count+=1
    except:
        leftover.write(x)
leftover.close()