#!/usr/bin/env python

from selenium import webdriver
from browsermobproxy import Server
import json
import requests
import radix
import argparse
import csv


CacheEnabled=False
CDNTrashold=0.5

CDNSignatures = {".akamai.net" : "Akamai", ".akamaized.net" : "Akamai", ".akamaiedge.net" : "Akamai", ".akamaihd.net" : "Akamai", ".edgesuite.net" : "Akamai", ".edgekey.net" : "Akamai", 
           ".srip.net" : "Akamai", ".akamaitechnologies.com" : "Akamai", ".akamaitechnologies.fr" : "Akamai", ".tl88.net" : "Akamai China CDN", ".llnwd.net" : "Limelight", 
           "edgecastcdn.net" : "Edgecast", ".systemcdn.net" : "Edgecast", ".transactcdn.net" : "Edgecast", ".v1cdn.net" : "Edgecast", ".v2cdn.net" : "Edgecast", 
           ".v3cdn.net" : "Edgecast", ".v4cdn.net" : "Edgecast", ".v5cdn.net" : "Edgecast", "hwcdn.net" : "Highwinds", ".simplecdn.net" : "Simple CDN", ".kxcdn.com" : "KeyCDN", 
           ".instacontent.net" : "Mirror Image", ".footprint.net" : "Level 3", ".fpbns.net" : "Level 3", ".b.yahoo.com" : "Yahoo", ".yimg." : "Yahoo", ".yahooapis.com" : "Yahoo",
            ".google." : "Google", "googlesyndication." : "Google", "youtube." : "Google", ".googleusercontent.com" : "Google", "googlehosted.com" : "Google", 
            ".gstatic.com" : "Google", ".doubleclick.net" : "Google", ".insnw.net" : "Instart Logic", ".inscname.net" : "Instart Logic", ".internapcdn.net" : "Internap", 
            ".cloudfront.net" : "Amazon CloudFront", ".netdna-cdn.com" : "NetDNA", ".netdna-ssl.com" : "NetDNA", ".netdna.com" : "NetDNA", ".hosting4cdn.com" : "Hosting4CDN",
            ".cotcdn.net" : "Cotendo CDN", ".cachefly.net" : "Cachefly", "bo.lt" : "BO.LT", ".cloudflare.com" : "Cloudflare", ".afxcdn.net" : "afxcdn.net", 
            ".lxdns.com" : "ChinaNetCenter", ".wscdns.com" : "ChinaNetCenter", ".wscloudcdn.com" : "ChinaNetCenter", ".ourwebpic.com" : "ChinaNetCenter", ".att-dsa.net" : "AT&T", 
            ".vo.msecnd.net" : "Microsoft Azure", ".azureedge.net" : "Microsoft Azure", ".voxcdn.net" : "VoxCDN", ".bluehatnetwork.com" : "Blue Hat Network", 
            ".swiftcdn1.com" : "SwiftCDN", ".cdngc.net" : "CDNetworks", ".gccdn.net" : "CDNetworks", ".panthercdn.com" : "CDNetworks", ".fastly.net" : "Fastly", 
            ".fastlylb.net" : "Fastly", ".nocookie.net" : "Fastly", ".gslb.taobao.com" : "Taobao", ".gslb.tbcache.com" : "Alimama", ".mirror-image.net" : "Mirror Image", 
            ".yottaa.net" : "Yottaa", ".cubecdn.net" : "cubeCDN", ".cdn77.net" : "CDN77", ".cdn77.org" : "CDN77", ".incapdns.net" : "Incapsula", ".bitgravity.com" : "BitGravity", 
            ".r.worldcdn.net" : "OnApp", ".r.worldssl.net" : "OnApp", "tbcdn.cn" : "Taobao", ".taobaocdn.com" : "Taobao", ".ngenix.net" : "NGENIX", ".pagerain.net" : "PageRain", 
            ".ccgslb.com" : "ChinaCache", "cdn.sfr.net" : "SFR", ".azioncdn.net" : "Azion", ".azioncdn.com" : "Azion", ".azion.net" : "Azion", ".cdncloud.net.au" : "MediaCloud", 
            ".rncdn1.com" : "Reflected Networks", ".cdnsun.net" : "CDNsun", ".mncdn.com" : "Medianova", ".mncdn.net" : "Medianova", ".mncdn.org" : "Medianova", 
            "cdn.jsdelivr.net" : "jsDelivr", ".nyiftw.net" : "NYI FTW", ".nyiftw.com" : "NYI FTW", ".resrc.it" : "ReSRC.it", ".zenedge.net" : "Zenedge", 
            ".lswcdn.net" : "LeaseWeb CDN", ".lswcdn.eu" : "LeaseWeb CDN", ".revcn.net" : "Rev Software", ".revdn.net" : "Rev Software", ".caspowa.com" : "Caspowa", 
            ".twimg.com" : "Twitter", ".facebook.com" : "Facebook", ".facebook.net" : "Facebook", ".fbcdn.net" : "Facebook", ".cdninstagram.com" : "Facebook", 
            ".rlcdn.com" : "Reapleaf", ".wp.com" : "WordPress", ".aads1.net" : "Aryaka", ".aads-cn.net" : "Aryaka", ".aads-cng.net" : "Aryaka", ".squixa.net" : "section.io", 
            ".bisongrid.net" : "Bison Grid", ".cdn.gocache.net" : "GoCache", ".hiberniacdn.com" : "HiberniaCDN", ".cdntel.net" : "Telenor", ".raxcdn.com" : "Rackspace", 
            ".unicorncdn.net" : "UnicornCDN", ".optimalcdn.com" : "Optimal CDN", ".kinxcdn.com" : "KINX CDN", ".kinxcdn.net" : "KINX CDN", ".stackpathdns.com" : "StackPath"}

    
    
# Cut a domain after 3 levels
# e.g. www.c3.google.it -> c3.google.it
def get3LD(FQDN):
    if FQDN[-1] == ".":
        FQDN = FQDN[:-1]
    names = FQDN.split(".")
    tln_array = names[-3:]
    tln = ""
    for s in tln_array:
        tln = tln + "." + s
    return tln[1:]


def getGood2LD(FQDN):
       
    bad_domains=set("co.uk co.jp co.hu co.il com.au co.ve .co.in com.ec com.pk co.th co.nz com.br com.sg com.sa \
    com.do co.za com.hk com.mx com.ly com.ua com.eg com.pe com.tr co.kr com.ng com.pe com.pk co.th \
    com.au com.ph com.my com.tw com.ec com.kw co.in co.id com.com com.vn com.bd com.ar \
    com.co com.vn org.uk net.gr".split())
    
    if FQDN[-1] == ".":
        FQDN = FQDN[:-1]    
    names = FQDN.split(".")
    if ".".join(names[-2:]) in bad_domains:
        return get3LD(FQDN)
    tln_array = names[-2:]
    tln = ""
    for s in tln_array:
        tln = tln + "." + s
    return tln[1:]



def QueryDNS(domain, record_type):

    payload = {'name': domain, 'type': record_type} 
    r = requests.get('https://dns.google.com/resolve', params=payload)
    response = json.loads(r.content)
    
    return response

def FQDNToOwner(FQDN):
    
    CDNOwner="-"

    #print canon
    snd=getGood2LD(FQDN)
    
    dom=snd.split(".")[0]
    frst=snd.replace(dom,"")
    
    
    FQDN_split=FQDN.split(".")
    
    dom_index=FQDN_split.index(dom)
    check=FQDN_split[dom_index]

    for j in range(dom_index,-1,-1):
        if(j!=dom_index):
            check=FQDN_split[j]+"."+check
        #print "URL "+FQDN + " CHECK " +check       
        
        if("."+check+frst in CDNSignatures):
            #print "FOUND " + "."+check+frst
            CDNOwner = CDNSignatures["."+check+frst]
            break
        if("."+check+"." in CDNSignatures):
            #print "FOUND " + "."+check+"."
            CDNOwner = CDNSignatures["."+check+"."]
            break
        if(check+frst in CDNSignatures):
            #print "FOUND " + check+frst
            CDNOwner = CDNSignatures[check+frst]
            break
        if(check+"." in CDNSignatures):
            #print "FOUND " + check+"."
            CDNOwner = CDNSignatures[check+"."]
            break
    
    return CDNOwner
    

def DNSSearchOwner(FQDN,lvl,FoutDNSQuery):
    
    Owner="-"
    lvl+=1
    FoutDNSQuery.write("Asking: LVL "+str(lvl)+" "+str(FQDN)+"\n")

    response = QueryDNS(FQDN, 'CNAME')
    if 'Authority' in response:
        for val in response['Authority']:
            canon = val['name']
            FoutDNSQuery.write("Authority: LVL "+ str(lvl) +" " +canon+"\n")
            Owner=FQDNToOwner(canon)
            if(Owner!="-"):
                return Owner

    
    if 'Answer' in response:
        for Answer in response['Answer']:
            AnswerFQDN = Answer['data']
            FoutDNSQuery.write("Answer: LVL "+ str(lvl) +" " +AnswerFQDN+"\n")
            Owner=FQDNToOwner(AnswerFQDN)            
            if(Owner!="-"): 
                return Owner
            
            Owner = DNSSearchOwner(AnswerFQDN,lvl,FoutDNSQuery)                
    return Owner

def SearchOwner(FQDN,FoutDNSQuery):

    CDNOwner = FQDNToOwner(FQDN)
        
    if(CDNOwner!= "-"):
        return CDNOwner

    CDNOwner = DNSSearchOwner(FQDN,0,FoutDNSQuery)

    return CDNOwner

    
def FillDB(pfx_record,FQDN,FoutDNSQuery):
       
    CDNOwner = SearchOwner(FQDN, FoutDNSQuery)
    
    pfx_record.data["Owner"] = CDNOwner

    return CDNOwner

def EvalObjets(Proxy,NetworkOwner,FOutFQDN,ForceDump,Domain,DomainsObjetsServerIP,FoutDNSQuery):
    
    FOutDomainCDN = open("../results/CDN_BASED.txt","a")
    TotObjects=0
    OwnersObjets = {}

    for entry in Proxy.har['log']['entries']:
        FullUrl=entry["request"]["url"]
        FQDN=FullUrl.split("/")[2].split(":")[0].strip()
        
        if(len(FQDN) > 0 and "serverIPAddress" in entry):
            
            TotObjects+=1
            
            Owner=""                
            if(CacheEnabled):                    
                ObjIP=entry["serverIPAddress"]
                NetObj=""
                if("." in ObjIP):
                    NetObj=ObjIP+"/24"
                else:
                    NetObj=ObjIP+"/64"
    
                pfx_record = NetworkOwner.add(NetObj)
                if "Owner" in pfx_record.data and pfx_record.data["Owner"]!="-":
                    Owner = pfx_record.data['Owner']
                else:
                    FillDB(pfx_record,FQDN,FoutDNSQuery) 
                    DomainsObjetsServerIP[Domain][FullUrl]=ObjIP

            else:
                Owner = SearchOwner(FQDN, FoutDNSQuery)
                if(Owner not in OwnersObjets): OwnersObjets[Owner]=0
                OwnersObjets[Owner]+=1
                FOutFQDN.write(str(FQDN) +" " +str(entry["serverIPAddress"])+" "+Owner +"\n")
    
    if(CacheEnabled==False and ForceDump==True):
        for Owner in OwnersObjets:
            if(Owner != "-" and OwnersObjets[Owner]>CDNTrashold*TotObjects): 
                FOutDomainCDN.write(Domain + " "+ Owner +" "+ str(OwnersObjets[Owner])+" "+ str(TotObjects)+"\n")
    
    FOutDomainCDN.close()
    
    return TotObjects
    

def getObjects(Proxy,Driver,NetworkOwner,Domain,DomainsObjetsServerIP,ForceDump,FoutDNSQuery):
    
    Proxy.new_har()
    FOutFQDN=""

    if(CacheEnabled == False):
        FOutFQDN = open("../results/domainsobjets/"+Domain,"w")
        
    try:
        Driver.get('http://'+Domain)    
        
        TotObjects = EvalObjets(Proxy,NetworkOwner,FOutFQDN,True,Domain,DomainsObjetsServerIP,FoutDNSQuery)
        
        return [1,TotObjects]
    
    except:
        print "EXCEPT: "+Domain
        TotObjects = EvalObjets(Proxy,NetworkOwner,FOutFQDN,ForceDump,Domain,DomainsObjetsServerIP,FoutDNSQuery)        
        return [-1,TotObjects]

    if(CacheEnabled==False):
        FOutFQDN.close()
                
    return



def EvaluateCDNs(DomainsObjetsServerIP,NetworkOwner):
 
    FOutDomainCDN = open("../results/CDN_BASED.txt","w")
    OwnerObjects={}
    TotalObjets=0
    for Domain in DomainsObjetsServerIP:
        FOutFQDN = open("../results/domainsobjets/"+Domain,"w")
        for Objecti in DomainsObjetsServerIP[Domain]:
            FQDN=Objecti.split("/")[2].split(":")[0].strip()
            ServerIP= DomainsObjetsServerIP[Domain][Objecti]
            pfx_record = NetworkOwner.add(ServerIP)   
            Owner=pfx_record.data["Owner"]
            FOutFQDN.write(str(FQDN) +" " +str(ServerIP)+" "+Owner +"\n")
            if(Owner not in OwnerObjects):
                OwnerObjects[Owner]=0
            OwnerObjects[Owner]+=1
            TotalObjets+=1
        
        for Owner in OwnerObjects:
            if(Owner != "-" and OwnerObjects[Owner]>CDNTrashold*TotalObjets): 
                FOutDomainCDN.write(Domain + " "+ Owner +" "+ str(OwnerObjects[Owner])+" "+ str(TotalObjets)+"\n")
        
        FOutFQDN.close()
        OwnerObjects.clear()
        TotalObjets=0

    FOutDomainCDN.close()


    return

def ReadAlexa():
    

    DomainsObjetsServerIP={}
    Domains=[]
    i=0
    with open('../data/top-500.csv', 'rb') as csvfile:
        AlexaFile = csv.reader(csvfile, delimiter=',')
        for row in AlexaFile:
            if(i<=100):
                Domain=row[1]
                Domains.append(Domain)
                DomainsObjetsServerIP[Domain]={}
            i+=1
            #if(i>3): break
    
    return Domains, DomainsObjetsServerIP

def DomainAanalysis():

    FoutDNSQuery = open("../results/logs/DNSQuery.txt","w")
    
    FOutDomainCDN = open("../results/CDN_BASED.txt","w")
    FOutDomainCDN.close()
    
    Domains, DomainsObjetsServerIP = ReadAlexa()

    server = Server("../proxy/browsermob-proxy-2.1.2/bin/browsermob-proxy")
    server.start()
    Proxy = server.create_proxy({'captureHeaders': True, 'captureContent': True, 'captureBinaryContent': True})
    service_args = ["--proxy=%s" % Proxy.proxy, '--ignore-ssl-errors=yes']


    # Create a new tree
    NetworkOwner = radix.Radix()
    Exceptions=[]        

    i=0
    for Domain in Domains:
        try:
            Driver = webdriver.PhantomJS(service_args=service_args, executable_path="../PhantomJS/phantomjs-2.1.1-linux-x86_64/bin/phantomjs")
            Driver.set_page_load_timeout(15)
            i+=1
            print str(i)+" "+Domain
            result =  getObjects(Proxy,Driver,NetworkOwner,Domain,DomainsObjetsServerIP,False,FoutDNSQuery)
            if(result[0] == -1):
                Exceptions.append(Domain)
            Driver.close()
        except:
            Exceptions.append(Domain)
            


    print "#Exceptions: "+str(len(Exceptions))    
    Unsolved=[]
    MaxTimeout=35
    for Domain in Exceptions:
        try:
            Driver = webdriver.PhantomJS(service_args=service_args, executable_path="/home/dgiordan/Scaricati/phantomjs-2.1.1-linux-x86_64/bin/phantomjs")
            result=[-1,0]
    
            CurrentTimeout=25
            FourceDump = False
            while(CurrentTimeout<=MaxTimeout):
                print Domain + " "+str(CurrentTimeout)
                Driver.set_page_load_timeout(CurrentTimeout)    
                result =  getObjects(Proxy,Driver,NetworkOwner,Domain,DomainsObjetsServerIP,FourceDump,FoutDNSQuery)
                if(result[0] == 1): break
                CurrentTimeout+=5
                if(CurrentTimeout==MaxTimeout): FourceDump=True
            if(CurrentTimeout>MaxTimeout and result[1]==0):
                print "Problem "+str(Domain)
                Unsolved.append(Domain)
            Driver.close()
        except:
            print "Retry"

    FoutDNSQuery.close()
    server.stop()                
    ##TODO DUMP
    if(CacheEnabled == True):
        EvaluateCDNs(DomainsObjetsServerIP,NetworkOwner)
     
    return

def main():
    
    '''parser = argparse.ArgumentParser(description="""
    Script that uses CNAME chain to identify domains based on CDNs.
    """)
    parser.add_argument('-C',  '--cache-enabled', nargs='?', required=False,
                        type=int,
                        help='Define if user want to use the /24 for IPv4 or /64 for IPv6 cache role. Default is disabled')
    parser.add_argument('-T',  '--CDN-trashold', nargs='?', required=False, default=0.5,
                        help='Define % of elements that a Domain must have to use a CDN. Default 0.5 (50%)')
    opts = vars(parser.parse_args())

    CacheEnabled=opts[0]
    CDNTrashold=opts[0]'''

            
    DomainAanalysis()


if __name__ == "__main__":
    main()
