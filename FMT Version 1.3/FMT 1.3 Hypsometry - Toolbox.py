# Floodplain Mapper Toolbox 1.3 for ArcGIS 10x
# Adapted for Python from the Barr-NCED Floodplain Mapper

import arcpy
import datetime

# Inputs
input_geodatabase = arcpy.GetParameterAsText(0)
output_file_path = arcpy.GetParameterAsText(1)
DEM = arcpy.Describe(arcpy.GetParameterAsText(2)).name 
Cell_Size = float(arcpy.GetParameterAsText(3))
Reaches = arcpy.Describe(arcpy.GetParameterAsText(4)).name
CrossSections = arcpy.Describe(arcpy.GetParameterAsText(5)).name
Table = arcpy.Describe(arcpy.GetParameterAsText(6)).name
stage = arcpy.GetParameterAsText(7) 
delete_intermediate_data = str(arcpy.GetParameterAsText(8))

# Switch boolean values
if delete_intermediate_data == "true":
    delete_intermediate_data = True
if delete_intermediate_data == "false":
    delete_intermediate_data = False

# Check for extensions
if arcpy.CheckOutExtension("3D") != "CheckedOut":
    arcpy.AddMessage("3D Analyst not available")
else:
    arcpy.AddMessage("3D Analyst checked out")

if arcpy.CheckOutExtension("spatial") != "CheckedOut":
    arcpy.AddMessage("Spatial Analyst not available")
else:
    arcpy.AddMessage("Spatial Analyst checked out")

# Get current time
time = datetime.datetime.now()
month = time.month
day = time.day
year = time.year
hour = time.hour
minute = time.minute
if hour > 12:
    hour = hour - 12
    am_pm = "PM"
else:
    am_pm = "AM"
if hour < 10:
    hour_string = str(hour)
    hour = "0{0}".format(hour_string)
if minute < 10:
    minute_string = str(minute)
    minute = "0{0}".format(minute_string)    
time_output = "{0}{1}{2}_{3}{4}{5}".format(month, day, year, hour, minute, am_pm)

# Create output geodatabase
output_gdb_name = "FMT_{0}".format(time_output)
output_gdb_path = output_file_path + "\{0}{1}".format(output_gdb_name, ".gdb")
arcpy.CreateFileGDB_management(output_file_path, output_gdb_name)

# Set path to filegeodatabase containing the tutorial data
arcpy.env.workspace = input_geodatabase

# Set overwrite to true
arcpy.env.overwriteOutput = True

# Validate inputs
with arcpy.da.SearchCursor(Reaches, "ReachID") as cursor:  
    for row in cursor:  
        if row[0] == "" or row[0] == None:
            arcpy.AddError("Reaches feature class has Null values in the ReachID field")
            raise RuntimeError

with arcpy.da.SearchCursor(CrossSections, "XS_ID") as cursor:  
    for row in cursor:  
        if row[0] == "" or row[0] == None:
            arcpy.AddError("Cross_Sections feature class has Null values in the XS_ID field")
            raise RuntimeError

# Get DEM's spatial reference object
spatial_ref = arcpy.Describe(DEM).spatialReference

# Make feature layer for cross sections that can be joined
arcpy.AddMessage("Creating temporary feature layer for {0}".format(CrossSections))
New_CrossSections = "New_Cross_Sections"
arcpy.MakeFeatureLayer_management(CrossSections, New_CrossSections)

# Add Join
arcpy.AddMessage("Joining {0} and {1}".format(New_CrossSections, Table))
JoinField = "XS_ID"
arcpy.AddJoin_management(New_CrossSections, JoinField, Table, JoinField, "KEEP_ALL")

# Perform analysis for each stage
    
arcpy.AddMessage("")
# Temporary Data
TIN = "TIN"
RasterFromTIN = "RasterFromTIN_{0}".format(stage)
Subtracted = "Subtracted_{0}".format(stage)
Reclassified = "Reclassified_{0}".format(stage)
ExtractedRaster = "ExtractedRaster_{0}".format(stage)
    
# Create TIN
arcpy.AddMessage("Creating TIN for {0}".format(stage))
if stage == "MIN_Z_Value":
    stage_name_for_table = "MIN_Z_Value"    
else:
    stage_name_for_table = "{0}.{1}".format(Table, stage)
expression = "{0} <None> Soft_Clip <None>;{1} {2} Mass_Points <None>;{3} {4} Hard_Line <None>".format(Reaches, New_CrossSections, stage_name_for_table, New_CrossSections, stage_name_for_table)
arcpy.CreateTin_3d(TIN, spatial_ref, expression, "CONSTRAINED_DELAUNAY")
    
# TIN to Raster
arcpy.AddMessage("Converting TIN to raster for {0}".format(stage))
input_cell_size = "CELLSIZE {0}".format(Cell_Size)
arcpy.TinRaster_3d(TIN, RasterFromTIN, "FLOAT", "LINEAR", input_cell_size, "1")
    
# Raster subtraction
arcpy.AddMessage("Subtracting the raster from TIN with the input DEM for {0}".format(stage))
arcpy.Minus_3d(RasterFromTIN, DEM, Subtracted)

# Reverse values
depth_grid_name = "{0}_Normalized".format(stage)
arcpy.Times_3d(Subtracted, -1, depth_grid_name)

# Slice DEM
arcpy.Slice_3d(depth_grid_name, "Hypsometry", 100, "EQUAL_INTERVAL", 1)

# Percent of elevation
arcpy.AddField_management("Hypsometry", "Percent_Elevation", "FLOAT", 2, "", "", "Percent_Elevation")
arcpy.CalculateField_management("Hypsometry", "Percent_Elevation", "!Value! * 0.01", "PYTHON_9.3")

# Cummulative Area
arcpy.AddField_management("Hypsometry", "Cumulative", "LONG", 9, "", "", "Cumulative")
freq = 0
with arcpy.da.UpdateCursor("Hypsometry", ("COUNT", "CUMULATIVE")) as cursor:
    for row in cursor:
        row[1] = row[0] + freq
        cursor.updateRow(row) 
	freq += row[0]

# Percent of area
arcpy.AddField_management("Hypsometry", "Percent_Area", "FLOAT", 2, "", "", "Percent_Area")
with arcpy.da.UpdateCursor("Hypsometry", ("CUMULATIVE", "PERCENT_AREA")) as cursor:
    for row in cursor:
        row[1] = row[0] / freq
        cursor.updateRow(row) 

# Calculate each reach's hypsometry
if arcpy.GetCount_management(Reaches) > 1:
    reach_list = []
    with arcpy.da.SearchCursor(Reaches, "ReachID") as rows:
	for row in rows:
	    reach_list.append(row[0])
    for reach in reach_list:
	arcpy.MakeFeatureLayer_management(Reaches, "NewFeatureLayer1")
	SQL = "\"{0}\" = '{1}'".format("ReachID", reach)
	arcpy.SelectLayerByAttribute_management("NewFeatureLayer1", "NEW_SELECTION", SQL)
	arcpy.CopyFeatures_management("NewFeatureLayer1", "CopiedFeature")
	outExtractByMask = arcpy.sa.ExtractByMask(depth_grid_name, "CopiedFeature")
	outExtractByMask.save("{0}_raster".format(reach))

	# Slice DEM
	arcpy.Slice_3d(outExtractByMask, "{0}_Hypsometry".format(reach), 100, "EQUAL_INTERVAL", 1)

	# Percent of elevation
	arcpy.AddField_management("{0}_Hypsometry".format(reach), "Percent_Elevation", "FLOAT", 2, "", "", "Percent_Elevation")
	arcpy.CalculateField_management("{0}_Hypsometry".format(reach), "Percent_Elevation", "!Value! * 0.01", "PYTHON_9.3")

	# Cummulative Area
	arcpy.AddField_management("{0}_Hypsometry".format(reach), "Cumulative", "LONG", 9, "", "", "Cumulative")
	freq = 0
	with arcpy.da.UpdateCursor("{0}_Hypsometry".format(reach), ("COUNT", "CUMULATIVE")) as cursor:
    	    for row in cursor:
        	row[1] = row[0] + freq
        	cursor.updateRow(row) 
		freq += row[0]

	# Percent of area
	arcpy.AddField_management("{0}_Hypsometry".format(reach), "Percent_Area", "FLOAT", 2, "", "", "Percent_Area")
	with arcpy.da.UpdateCursor("{0}_Hypsometry".format(reach), ("CUMULATIVE", "PERCENT_AREA")) as cursor:
    	    for row in cursor:
        	row[1] = row[0] / freq
        	cursor.updateRow(row) 

	arcpy.Delete_management("CopiedFeature")

# Create master hypsometry table
arcpy.CreateTable_management(arcpy.env.workspace, "Hypsometry_all")
arcpy.AddField_management("hypsometry_all", "Percent_Elevation", "FLOAT")
arcpy.AddField_management("hypsometry_all", "Total_Percent_Area", "FLOAT")
if arcpy.GetCount_management(Reaches) > 1:
    for reach in reach_list:
	arcpy.AddField_management("hypsometry_all", "{0}_Percent_Area".format(reach), "FLOAT")

# Get Percent Elevation Values
PercentElevations = [row[0] for row in arcpy.da.SearchCursor("Hypsometry", "Percent_Elevation")]
PercentArea = [row[0] for row in arcpy.da.SearchCursor("Hypsometry", "Percent_Area")]
zipped_data = zip(PercentElevations, PercentArea)
rows = arcpy.InsertCursor("hypsometry_all")
for i in zipped_data:
    row = rows.newRow()
    row.setValue("Percent_Elevation", i[0])
    row.setValue("Total_Percent_Area", i[1])
    rows.insertRow(row)
del row
del rows

if arcpy.GetCount_management(Reaches) > 1:
    for reach in reach_list:
	PercentArea = [row[0] for row in arcpy.da.SearchCursor("{0}_Hypsometry".format(reach), "Percent_Area")]
	with arcpy.da.UpdateCursor("hypsometry_all", ["{0}_Percent_Area".format(reach)]) as cursor:
	    n = 0
	    for row in cursor:
                row[0] = PercentArea[n]
            	cursor.updateRow(row)	
		n += 1

# Export files to new geodatabase
arcpy.TableToGeodatabase_conversion("Hypsometry_all", output_gdb_path)
arcpy.RasterToGeodatabase_conversion(depth_grid_name, output_gdb_path)
arcpy.RasterToGeodatabase_conversion("Hypsometry", output_gdb_path)
for reach in reach_list:
    arcpy.RasterToGeodatabase_conversion("{0}_Hypsometry".format(reach), output_gdb_path)	
    
# Delete files from workspace
arcpy.Delete_management("Hypsometry_all")
arcpy.Delete_management(depth_grid_name)
arcpy.Delete_management("Hypsometry")
for reach in reach_list:
    arcpy.Delete_management("{0}_Hypsometry".format(reach))	

# Delete temporary files and variables
if delete_intermediate_data == True:
    arcpy.AddMessage("Deleting temporary files for {0}".format(stage))
    arcpy.Delete_management(TIN)
    arcpy.Delete_management(RasterFromTIN)
    arcpy.Delete_management(Subtracted)
    for reach in reach_list:
	arcpy.Delete_management("{0}_Raster".format(reach))	

# Remove join
arcpy.RemoveJoin_management(New_CrossSections, Table)
arcpy.Delete_management(New_CrossSections)
del New_CrossSections
arcpy.AddMessage("")
arcpy.AddMessage("Script finished")