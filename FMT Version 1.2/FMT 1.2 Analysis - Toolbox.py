# Floodplain Mapper Toolbox 1.2 for ArcGIS 10x
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
Stages = arcpy.GetParameterAsText(7).split(";")
delete_intermediate_data = bool(arcpy.GetParameterAsText(8))

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
for stage in Stages:
    
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
    
    # Reclassify raster
    arcpy.AddMessage("Reclassifing the subtracted raster for {0}".format(stage))
    arcpy.Reclassify_3d(Subtracted, "Value", "-999 0.01 1;0.01 999 0", Reclassified, "DATA")
    
    # Extract by Attributes
    arcpy.AddMessage("Extracting by attributes for {0}".format(stage))
    arcpy.gp.ExtractByAttributes_sa(Reclassified, "\"Value\" = 0", ExtractedRaster)
    
    # Create depth grid
    arcpy.AddMessage("Creating depthgrid for {0}".format(stage))
    depth_grid_name = "{0}_DepthGrid".format(stage)
    outExtractByMask = arcpy.sa.ExtractByMask(Subtracted, ExtractedRaster)
    outExtractByMask.save(depth_grid_name)
    
    # Convert Raster to Polygon
    arcpy.AddMessage("Converting depthgrid to polygon for {0}".format(stage))
    converted_polygon = "{0}_ConvertedPolygon".format(stage)
    arcpy.RasterToPolygon_conversion(ExtractedRaster, converted_polygon, "SIMPLIFY", "VALUE")

    # Intersect Polygon with Reaches layer
    arcpy.AddMessage("Intersecting Polygon layer with Reaches layer for {0}".format(stage))
    polygon_name = "{0}_Polygon".format(stage)
    arcpy.Intersect_analysis([converted_polygon, Reaches], polygon_name, "NO_FID")

    # Create Output Table
    arcpy.AddMessage("Creating output table for {0}".format(stage))
    table_name = "{0}_Statistics".format(stage)
    arcpy.CreateTable_management(arcpy.env.workspace, table_name)
    table_field_name1 = "ReachID"
    table_field_name2 = "Total_Area"
    table_field_name3 = "Inundated_Area"
    table_field_name4 = "Percent_Inundated"
    table_field_name5 = "Inundation_Volume"
    table_field_name6 = "Max_Depth"
    table_field_name7 = "Mean_Depth"
    arcpy.AddField_management(table_name, table_field_name1, "TEXT")
    arcpy.AddField_management(table_name, table_field_name2, "FLOAT")
    arcpy.AddField_management(table_name, table_field_name3, "FLOAT")
    arcpy.AddField_management(table_name, table_field_name4, "FLOAT")
    arcpy.AddField_management(table_name, table_field_name5, "FLOAT")
    arcpy.AddField_management(table_name, table_field_name6, "FLOAT")
    arcpy.AddField_management(table_name, table_field_name7, "FLOAT")
    
    # Compute zonal statistics as a table
    ReachID = "ReachID"
    inZoneData = Reaches
    zoneField = ReachID
    inValueRaster = depth_grid_name
    outTable = "ZonalStats_{0}".format(stage)
    arcpy.sa.ZonalStatisticsAsTable(inZoneData, zoneField, inValueRaster, outTable, "DATA", "ALL")
    
    # Use Search Cursor to get values for table
    ReachIDs = [row[0] for row in arcpy.da.SearchCursor(outTable, ReachID)]
    Total_Areas_Raw = [row[0] for row in arcpy.da.SearchCursor(Reaches, "Shape_Area")]
    Inundated_Areas = [row[0] for row in arcpy.da.SearchCursor(outTable, "AREA")]
    Inundation_Volumes_Raw = [row[0] for row in arcpy.da.SearchCursor(outTable, "SUM")]
    Max_Depths = [row[0] for row in arcpy.da.SearchCursor(outTable, "MAX")]
    Mean_Depths = [row[0] for row in arcpy.da.SearchCursor(outTable, "MEAN")]
    
    # Round values for total areas
    Total_Areas = []
    for i in Total_Areas_Raw:
        rounded = round(i)
        Total_Areas.append(rounded)
    
    # Calculate percent of total area inundated
    zipped_area = zip(Inundated_Areas, Total_Areas)
    Percent_inundated = []
    for i in zipped_area:
        percent = i[0]/i[1]
        Percent_inundated.append(round(percent, 4))
    
    # Process sum values into volumes
    Inundation_Volumes = []
    for i in Inundation_Volumes_Raw:
        volume = i * Cell_Size * Cell_Size
        Inundation_Volumes.append(round(volume, 2))
    
    # Zip data into a list
    zipped_data = zip(ReachIDs, Total_Areas, Inundated_Areas, Percent_inundated, Inundation_Volumes, Max_Depths, Mean_Depths)
    
    # Use insert cursor to add rows
    rows = arcpy.InsertCursor(table_name)
    for i in zipped_data:
        row = rows.newRow()
        row.setValue(table_field_name1, i[0])
        row.setValue(table_field_name2, i[1])
        row.setValue(table_field_name3, i[2])
        row.setValue(table_field_name4, i[3])
        row.setValue(table_field_name5, i[4])
        row.setValue(table_field_name6, i[5])
        row.setValue(table_field_name7, i[6])
        rows.insertRow(row)
    del row
    del rows
    
    # Export files to new geodatabase
    arcpy.FeatureClassToGeodatabase_conversion(polygon_name, output_gdb_path)
    arcpy.RasterToGeodatabase_conversion(depth_grid_name, output_gdb_path)
    arcpy.TableToGeodatabase_conversion(table_name, output_gdb_path)
    
    # Delete files from workspace
    arcpy.Delete_management(polygon_name)
    arcpy.Delete_management(table_name)
    arcpy.Delete_management(depth_grid_name)
    
    #Delete temporary files and variables
    if delete_intermediate_data == True:
        arcpy.AddMessage("Deleting temporary files for {0}".format(stage))
        arcpy.Delete_management(TIN)
        del TIN
        arcpy.Delete_management(RasterFromTIN)
        del RasterFromTIN
        arcpy.Delete_management(Subtracted)
        del Subtracted
        arcpy.Delete_management(Reclassified)
        del Reclassified
        arcpy.Delete_management(ExtractedRaster)
        del ExtractedRaster
        arcpy.Delete_management(converted_polygon)
        del converted_polygon
        arcpy.Delete_management(outTable)
        del outTable
    else:
        export_rasters_temp = [RasterFromTIN, Subtracted, Reclassified, ExtractedRaster]
        arcpy.FeatureClassToGeodatabase_conversion(converted_polygon, output_gdb_path)
        arcpy.RasterToGeodatabase_conversion(export_rasters_temp, output_gdb_path)
        arcpy.TableToGeodatabase_conversion(outTable, output_gdb_path)
        arcpy.Delete_management(TIN)
        del TIN
        arcpy.Delete_management(RasterFromTIN)
        del RasterFromTIN
        arcpy.Delete_management(Subtracted)
        del Subtracted
        arcpy.Delete_management(Reclassified)
        del Reclassified
        arcpy.Delete_management(ExtractedRaster)
        del ExtractedRaster
        arcpy.Delete_management(converted_polygon)
        del converted_polygon
        arcpy.Delete_management(outTable)
        del outTable

# Remove join
arcpy.RemoveJoin_management(New_CrossSections, Table)
arcpy.Delete_management(New_CrossSections)
del New_CrossSections
arcpy.AddMessage("")
arcpy.AddMessage("Script finished")