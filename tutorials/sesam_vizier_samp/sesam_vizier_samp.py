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

from astropy import units as u
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord

# Keep the output of this example "sane".
if not sys.warnoptions:
  warnings.simplefilter("ignore")

def resolve_name(name):

  # Query SIMBAD and resolve name to positions. 
  table = Simbad.query_region(name, radius=0.1 * u.deg)

  # Make an astropy SkyCoordinate object from position given by 
  # the first row in the table.
  pos = SkyCoord (table[0]["RA"], table[0]["DEC"], frame='icrs', unit=(u.hourangle, u.degree))

  return pos

def query_vizier(pos):

  # Set the service url
  access_url = "http://vizier.u-strasbg.fr/viz-bin/conesearch/I/350/gaiaedr3?"

  # Query the Gaia DR2 catalogue on Vizier
  result = pyvo.conesearch(access_url, pos, radius=5.0)

  return result

def main():

  # Resolve the name to position
  position=resolve_name("pleiades")

  # Query Vizier
  table=query_vizier(position)

  # Send the table to topcat
  table.broadcast_samp("topcat")

if __name__=="__main__":
  main()


