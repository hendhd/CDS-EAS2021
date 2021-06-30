#! /usr/bin/ python
# -*- coding=utf-8 -*- 

# A demo program on how to explore the SIMBAD TAP service with PyVO

import pyvo


service = pyvo.dal.TAPService ("http://simbad.u-strasbg.fr:80/simbad/sim-tap")


def get_tapschema_columns (service, tablename):

  result = service.search ("""
    SELECT * FROM TAP_SCHEMA.columns
    WHERE table_name='{tablename}' """.format(tablename=tablename)
    )
  return result


def get_tapschema_tables (service):

  result = service.search("""
    SELECT * FROM TAP_SCHEMA.tables"""
  )

  return result


def main():

  tables = get_tapschema_tables(service).to_table()
  print (tables["table_name"])
  
  columns = get_tapschema_columns (service, "basic")


if __name__=="__main__":
  main()

