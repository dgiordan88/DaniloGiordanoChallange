#!/usr/bin/env python

import pycurl
from StringIO import StringIO

def DumpResult(Domain,Owner,Protocol,DNSTime, TCPConn, SSLNeg, TTFB, RXTime):

    FTime = open("../results/DomainsTime.txt","a")

    FTime.write(Domain + " "+ Owner+ " "+Protocol+" %.3f %.3f %.3f %.3f %.3f\n"%(DNSTime, TCPConn, SSLNeg, TTFB-SSLNeg, RXTime))
    
    FTime.close()
    
    
def TimeAnalysis(Domain,Protocol):
    

    DNSTime=-1
    TCPConn=-1
    SSLNeg=-1
    TTFB= -1
    RXTime=-1 

    #Set CURL parameters
    buffer = StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, Protocol+"://" + Domain)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.FOLLOWLOCATION, True)
    c.setopt(c.USERAGENT, 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0')
    c.setopt(pycurl.TIMEOUT, 60)
    c.setopt(pycurl.NOSIGNAL, 1)
    
    try:
        c.perform()
    except:
        print("Error accessing "+Domain + " with protocol: "+ Protocol +" \n")
        return -1,DNSTime, TCPConn, SSLNeg, TTFB, RXTime


    #Timing INFO: https://photodelphinus.com/Imagenes/carga/cURL/Manual/libcurl/curl_easy_getinfo.html
    DNSTime = c.getinfo(c.NAMELOOKUP_TIME)
    ConnTime = c.getinfo(c.CONNECT_TIME)
    TCPConn = ConnTime - DNSTime
    PreTransfer = c.getinfo(c.PRETRANSFER_TIME)
    SSLNeg = PreTransfer - ConnTime
    TTFB = c.getinfo(c.STARTTRANSFER_TIME)
    Total = c.getinfo(c.TOTAL_TIME)
    RXTime = Total - TTFB



    c.close()

    return 1, DNSTime, TCPConn, SSLNeg, TTFB, RXTime
        
    return
    
def main():

    FTime = open("../results/DomainsTime.txt","w")
    FTime.close()

    fin = open("../results/CDN_BASED.txt","r")
    DomainsOwner=[]
    i=0
    OwnersMeasures={}
    for line in fin:
        ls=line.split()
        if(ls[1] not in OwnersMeasures):
            OwnersMeasures[ls[1]]=[0,0,0,0,0,0,0,0]

        DomainsOwner.append((ls[0],ls[1]))

    for DomainOwner in DomainsOwner:
        i += 1
        Domain=DomainOwner[0]
        Owner = DomainOwner[1]
        print i, Domain, Owner
        Result,DNSTime, TCPConn, SSLNeg, TTFB, RXTime = TimeAnalysis(Domain,"https")
        Protocol="HTTPS"
        if(Result==-1):
            Protocol="HTTP"
            Result,DNSTime, TCPConn, SSLNeg, TTFB, RXTime = TimeAnalysis(Domain,"http")
            print "Retry:", i, Domain, Owner, "http", Result  
        
        Errors=open("../results/logs/DNSErrorHost.txt","w")
        if(Result!=-1):
            OwnersMeasures[Owner][0]+=1
            OwnersMeasures[Owner][1]+=DNSTime
            OwnersMeasures[Owner][2]+=TCPConn
            OwnersMeasures[Owner][3]+=SSLNeg
            OwnersMeasures[Owner][4]+=TTFB-SSLNeg
            OwnersMeasures[Owner][5]+=RXTime
            OwnersMeasures[Owner][6]+=TTFB
            
            
            
            DumpResult(Domain,Owner,Protocol,DNSTime, TCPConn, SSLNeg, TTFB, RXTime)
        else:
            Errors.write(Domain +" "+Owner+"\n")

    fout = open("../results/AggregateValues.txt","w")
    fout.write("CDNOwner #Samples MeanDNS MeanTCP MeanSSL MeanWait MeanRX MeanTTFB\n")
    for Owner in OwnersMeasures:
        NSamples=float(OwnersMeasures[Owner][0])
        if(NSamples>0):
            MeanDNSTime=OwnersMeasures[Owner][1]/NSamples
            MeanTCPConn=OwnersMeasures[Owner][2]/NSamples
            MeanSSLNeg=OwnersMeasures[Owner][3]/NSamples
            MeanTTFB=OwnersMeasures[Owner][4]/NSamples
            MeanRXTime=OwnersMeasures[Owner][5]/NSamples
            MeanGlobalTTFB=OwnersMeasures[Owner][6]/NSamples
            
            
            fout.write(Owner + " %d %.2f %.2f %.2f %.2f %.2f %.2f\n"%(NSamples, MeanDNSTime, MeanTCPConn, MeanSSLNeg, MeanTTFB, MeanRXTime,MeanGlobalTTFB))
    return

if __name__ == "__main__":
    main()