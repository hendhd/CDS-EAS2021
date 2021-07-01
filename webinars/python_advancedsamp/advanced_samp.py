#! /usr/bin/ python
# -*- coding=utf-8 -*- 

# A demo program on how to use the CDS services from within Python. 
# Here we use the astropquery package to resolve a name to a position,
# then we send a cone search query to the Gaia EDR3 on the Vizier
# service to retrieve positions, proper motions and colours.
# Eventually we send everything to topcat via SAMP to do further
# analysis of the data. 
#
# Make sure you have topcat installed and open before starting the
# script. 


import pyvo
import warnings 
import sys
import time

from astropy import units as u
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
from astropy.coordinates.name_resolve import get_icrs_coordinates as Sesame
from astropy.samp import SAMPIntegratedClient
from astropy.table import Table



# Keep the output of this example "sane".
if not sys.warnoptions:
  warnings.simplefilter("ignore")


class SAMP_Receiver(object):

  def __init__(self, client):
    self.client = client
    self.received = False

  def receive_call(self, private_key, sender_id, msg_id, mtype, params, extra):
    self.params = params
    self.received = True
    self.client.reply(msg_id, {"samp.status": "samp.ok", "samp.result": {}})
    
  def receive_notification(self, private_key, sender_id, mtype, params, extra):
    self.params = params
    self.received = True


def listen_SAMP ():

  # Make the client Object and connect to SAMP.
  client = SAMPIntegratedClient()
  client.connect()

  r = SAMP_Receiver(client)
  client.bind_receive_call("table.load.votable", r.receive_call)
  client.bind_receive_notification("table.load.votable", r.receive_notification)

  try:

    # We test every 0.1s to see if the hub has sent a message
    while True:
      time.sleep(0.1)
      if r.received:
        table = Table.read(r.params['url'])
        break
        
  finally:
    client.disconnect()
    
    return table

def query_gaiacone(pos):

  # Set the service url
  access_url = "https://gaia.ari.uni-heidelberg.de/cone/search?"

  # Query the Gaia DR2 catalogue on ARI Gaia Service
  result = pyvo.conesearch(access_url, pos, radius=1.0)

  return result

def query_simbad(localtable):

  service = pyvo.dal.TAPService ("http://simbad.u-strasbg.fr:80/simbad/sim-tap")

  simbad_query = """
  SELECT b.oid, b.ra, b.dec, b.otype_txt, mine.* 
  FROM basic AS b
  JOIN tap_upload.localtable AS mine
  ON 
      1=CONTAINS(POINT('ICRS', b.ra, b.dec),
                 CIRCLE('ICRS', mine.ra, mine.dec, 10./3600.))            
                 
                 """
                
  result = service.search(query=simbad_query, uploads={"localtable":localtable})

  return result

def main():

  # Keep the output of this example "sane".
  if not sys.warnoptions:
    warnings.simplefilter("ignore")
  
  # Resolve the name to position
  position=Sesame("pleiades")
  print ("Name resolved. Starting Cone Search.")

  # Query ARI Cone Search on Gaia
  table=query_gaiacone(position)
  print ("Received Data from ARI Service. Sending to topcat")

  # Send the table to topcat
  table.broadcast_samp("topcat")
  print ("Awating Action in TOPCAT")
  
    # Wait for an answer from topcat
  peculiar_objects = listen_SAMP()
  print ("Good objects, query Simbad")
  
  # Get info from SIMBAD...
  print ("Querying Simbad")
  table = query_simbad(peculiar_objects)
  
  # ... and sent it to Aladin
  print ("Sending to Aladin")
  table.broadcast_samp("Aladin")
  
if __name__=="__main__":
  main()


