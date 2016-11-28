#!/usr/bin/env python

import json
import requests
from _pybgpstream import BGPStream, BGPRecord
import radix
import re
import csv

def QueryDNS(domain, record_type):

    payload = {'name': domain, 'type': record_type} 
    r = requests.get('https://dns.google.com/resolve', params=payload)
    response = json.loads(r.content)
    
    return response

def ReadAlexa():
    
    Domains=[]
    i=0
    with open('../data/top-500.csv', 'rb') as csvfile:
        AlexaFile = csv.reader(csvfile, delimiter=',')
        for row in AlexaFile:
            Domain=row[1]
            Domains.append(Domain)
            i+=1
            #if(i>3): break
    
    return Domains


def DomainPrefixFinder():
    

    Domains = ReadAlexa()
    
    DomainsPfxs={}
    for Domain in Domains:
        DomainsPfxs[Domain]=set()
        response = QueryDNS(Domain, 'A')
        if("Answer" in response):
            for answer in response["Answer"]:
                DomainsPfxs[Domain].add(answer['data'])    
        
    return DomainsPfxs




def BGPInformation():
        
    collector="route-views2"
    # initialize and configure BGPStream
    stream = BGPStream()
    rec = BGPRecord()
    stream.add_filter('collector', collector)
    
    # NB: BGPStream uses inclusive/inclusive intervals, so subtract one off the
    # end time since we are using inclusive/exclusive intervals
    stream.add_interval_filter(1479715200, 1479715501)
    stream.add_filter('record-type', 'ribs')
    
    stream.start()
    
    # Create a new tree
    PfxOrigins = radix.Radix()
        
    # loop over all records in the stream
    while stream.get_next_record(rec):
        elem = rec.get_next_elem()
        # loop over all elems in the record
        while elem:
            if('as-path' in elem.fields):
                path_split=elem.fields['as-path'].split()       
                if(len(path_split)>0):
                    origin=path_split[-1]
                    pfx = elem.fields['prefix']
                    if(pfx!="0.0.0.0/0" and pfx!="::/0" ):
                        pfx_record = PfxOrigins.add(pfx)
                        if "origin" not in pfx_record.data:
                            pfx_record.data["origin"]=set()
                        pfx_record.data["origin"].add(origin)
            elem = rec.get_next_elem()
    
    return PfxOrigins

def EvaluateOrigins(DomainsPrefixs,PfxOrigins):
    
    
    OriginsDomains={}
    fout = open("../results/DomainNetworkOrigin.txt","w")
    for Domain in DomainsPrefixs:
        for Pfx in DomainsPrefixs[Domain]:
            if(re.search('[a-zA-Z]', Pfx)==None):
                pfx_record = PfxOrigins.search_best(Pfx)
                if pfx_record:
                    origins = pfx_record.data["origin"]
                    for origin in origins:
                        if origin not in OriginsDomains:
                            OriginsDomains[origin]=set()
                        OriginsDomains[origin].add(Domain)
                        fout.write(Domain +" " +pfx_record.network+" "+origin+"\n")

    fout.close()
    fout = open("../results/OriginDomains.txt","w")
    fout_count = open("../results/OriginDomainsCount.txt","w")
    for origin in OriginsDomains:
        fout_count.write(origin +" %d\n"%len(OriginsDomains[origin]))
        for domain in OriginsDomains[origin]:
            fout.write(origin +" "+domain + "\n")
            
    return

def DumpBGPInfo(PfxOrigins):
    
    fout = open("../results/Pfxs_origin.txt","w")
    for pfx_record in PfxOrigins:
        for origin in  pfx_record.data["origin"]:
            fout.write(pfx_record.prefix +" "+ origin+"\n")    
    
    fout.close()
    
    return


def main():
    
    print "Finding Networks"
    DomainsPrefixs = DomainPrefixFinder()
    print "Downloading BGP data"
    PfxOrigins = BGPInformation()
    DumpBGPInfo(PfxOrigins)

    print "Evaluate Origins"
    EvaluateOrigins(DomainsPrefixs,PfxOrigins)        
    
    return


main()