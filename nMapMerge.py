#!/usr/bin/env python

import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
print 'Debug On'

import os
import re
import time

from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument("-f", "--file", dest="filename",
                    help="parse FILE", metavar="FILE")
parser.add_argument("-d", "--dir", dest="directory",
                    help="Parse all xml in directory", metavar="DIR")
parser.add_argument("-q", "--quiet",
                    action="store_false", dest="verbose", default=True,
                    help="don't print status messages to stdout")

def merge_nMap(f, mf):
	HOSTS = 0
	try: 
		nMapXML = ET.ElementTree(file=f);
		
		for host in nMapXML.findall('host'):
			HOSTS = HOSTS + 1
			cHost = ET.tostring(host)  
			mFile = open(mf, "a")  
			mFile.write(cHost) 
			mFile.close()	

	except Exception, e:
		logging.warn("skipping: %r", f)
		logging.warn(str(e))

	return HOSTS

def addHeader(f):
	nMap_Header  = '<?xml version="1.0" encoding="UTF-8"?>\n'
	nMap_Header += '<!DOCTYPE nmaprun>\n'
	nMap_Header += '<?xml-stylesheet href="file:///usr/share/nmap/nmap.xsl" type="text/xsl"?>\n'
	nMap_Header += '<!-- Nmap Merged with nMapMergER.py https://github.com/CBHue/nMapMergER -->\n'
	nMap_Header += '<nmaprun scanner="nmap" args="nmap -iL hostList.txt" start="1" startstr="Wed Sep  0 00:00:00 0000" version="7.70" xmloutputversion="1.04">\n'
	nMap_Header += '<scaninfo type="syn" protocol="tcp" numservices="1" services="1"/>\n'
	nMap_Header += '<verbose level="0"/>\n'
	nMap_Header += '<debugging level="0"/>\n'

	mFile = open(f, "w")  
	mFile.write(nMap_Header) 
	mFile.close()

def addFooter(f, h):
	nMap_Footer  = '<runstats><finished time="1" timestr="Wed Sep  0 00:00:00 0000" elapsed="0" summary="Nmap done at Wed Sep  0 00:00:00 0000; ' + str(h) + ' IP address scanned in 0.0 seconds" exit="success"/>\n'
	nMap_Footer += '</runstats>\n'
	nMap_Footer += '</nmaprun>\n'

	mFile = open(f, "a")  
	mFile.write(nMap_Footer) 
	mFile.close()

def main(mf):
	args = parser.parse_args()
	HOSTS = 0

	if args.filename is not None:
		f = args.filename
		if f.endswith('.xml'):
			logging.debug("FILE: %r", f)
			H = merge_nMap(f,mf)
			HOSTS = HOSTS + H

	elif args.directory is not None:
		path = args.directory

		for f in os.listdir(path):
			# For now we assume xml is nMap
			if f.endswith('.xml'): 
				fullname = os.path.join(path, f)
				logging.debug("PATH: %r", fullname)
				H = merge_nMap(fullname,mf)
				HOSTS = HOSTS + H

	else :
		print "usage issues =("
		exit

	return HOSTS

if __name__ == "__main__":
	
	from datetime import datetime
	dt = datetime.now() 
	dt = re.sub(r"\s+", '-', str(dt))
	mergeFile = "nMap_Merged_" + dt + ".xml"

	# Create Header
	addHeader(mergeFile)

    # call main 
	H = main(mergeFile)

	# create Footer
	addFooter(mergeFile, H)

	print "Output XML File:", mergeFile

	import os
	cmd = '/usr/bin/xsltproc'
	if os.path.isfile(cmd):
		out = re.sub(r'.xml', '.html', mergeFile)
		cmd = cmd + " -o " + out + " " + mergeFile
		os.system(cmd)
		print "Output HTML File:", out
