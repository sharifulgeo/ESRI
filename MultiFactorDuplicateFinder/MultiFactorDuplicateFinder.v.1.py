#!/usr/bin/python
# -*- #################
#Author:Shariful Islam
#Contact: msi_g@yahoo.com
'''
This tool generates duplicates based on two fields for instance

Input layer is land parcel boundary and

Say two fields are:

1. County
2. Last name of a person



After defining these two fields you will be able to find the duplicate
shapes (smaller than county say land parcels) that have two or more common last name in for each county

In a nutshell under this circumstances this tool finds all land parcels that have more than one last name in common for each county.
It will ommit dupplicate last name across county and that is the benefit of the multifactor duplicater finder.

or

It identifies those land parcels that have common key generated by concatenating field 1 and field 2 i.e. County+Last name of a person

'''

# Import system modules
import arcpy
import os
from collections import Counter
from collections import defaultdict
arcpy.env.overwriteOutput = True

use = 'T'#'S'
inp = (arcpy.GetParameterAsText(0) if use == 'T' else 
       r"C:\Users\Winrock\Desktop\Chota\Spatial Join\NewFileGeodatabase.gdb\Data\TX_STATE_ABSTRACTS_NAD27_Intsct_1")

out = (arcpy.GetParameterAsText(1) if use == 'T' else 
       r"C:\Users\Winrock\Desktop\Chota\Spatial Join\NewFileGeodatabase.gdb\Data\dupllocation")


filter_field1 = (arcpy.GetParameterAsText(2) if use == 'T' else 
          'County')

filter_field2 = (arcpy.GetParameterAsText(3) if use == 'T' else 
          'ANUM')

          
arcpy.MakeFeatureLayer_management(inp,"myinp")

flds = ['OID@','SHAPE@']#,'County','ANUM']
flds.append(str(filter_field1))
flds.append(str(filter_field2))

fldvalues = []
featurs = []

#Get all unique values for first filter field
with arcpy.da.SearchCursor("myinp", flds) as scur:
    for f in scur:
        fldvalues.append(f[2])
unq_fldvalues = list(set(fldvalues))

d = defaultdict(list)
for county in unq_fldvalues[0:10]:
    with arcpy.da.SearchCursor("myinp", flds, where_clause="{0} = '{1}'".format(filter_field1,county)) as scur:
        l = list(scur)
        tmp = {f[0]:f[3] for f in l}#OID+ASUN
        dupes = {k:v for k,v in Counter(tmp.values()).items() if v>1}#ASUM+Counts>1
        bad_OID = [i for i,j in tmp.items() if j in dupes.keys()]
        if len(dupes.items())>1:#just a filter to avoid the blak dupes
            d[county].append(bad_OID)
        if use == 'T':
            arcpy.AddMessage('Completed %s'%county)
        else:
            print 'Completed %s'%county
        

for k,v in d.items():   
    with arcpy.da.SearchCursor("myinp", flds, where_clause="{0} = '{1}'".format(filter_field1,k)) as scur:
        if use == 'T':
            arcpy.AddMessage('\nWriting features...')
            arcpy.AddMessage('Completed %s'%k)
        else:
            print '\nWriting features...'
            print '\nCompleted %s'%k
            
        dt = [f[1] for f in scur if f[0] in v[0]]
        if len(dt)>0:
            featurs.append(dt)

featurs = [it for sb in featurs for it in sb]
arcpy.CopyFeatures_management(featurs, out)
