#! /usr/bin/ python
# -*- coding=utf-8 -*- 

# A demo program for PyVO

import pyvo
import os
import warnings
import sys

# Keep the output of this example "sane".
if not sys.warnoptions:
  warnings.simplefilter("ignore")

def get_galaxies():
  """Get information of galaxies in the fornax cluster from SIMBAD"""

  # Make the TAP service object
  service = pyvo.dal.TAPService ("http://simbad.u-strasbg.fr:80/simbad/sim-tap")

  # Query the TAP service with a simple ADQL query.
  result = service.search ("""
    SELECT TOP 15
    oid,ra,dec,galdim_majaxis
    FROM basic
    WHERE 1=CONTAINS(
    POINT('',ra, dec),
    CIRCLE('',54.81426, -35.4652, 0.6))
    AND galdim_majaxis>0.4 """
  )

  return result

def main():
  # get galaxies from SIMBAD
  galaxies=get_galaxies()

  # Sent the table to topcat
  galaxies.broadcast_samp('topcat')


if __name__=="__main__":
  main()

