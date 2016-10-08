# Floodplain Mapper Toolbox 1.2 for ArcGIS 10x
# Adapted for Python from the Barr-NCED Floodplain Mapper

import arcpy

# Inputs
out_location = arcpy.GetParameterAsText(0)
name = arcpy.GetParameterAsText(1)
input_raster = arcpy.GetParameterAsText(2)
create_hillshade = bool(arcpy.GetParameterAsText(3))

# Check for extensions
if arcpy.CheckOutExtension("spatial") != "CheckedOut":
    arcpy.AddMessage("Spatial Analyst not available")
else:
    arcpy.AddMessage("Spatial Analyst checked out")

# Concatenate path
path = out_location + "\{0}{1}".format(name, ".gdb")

# Create Geodatabase
arcpy.AddMessage("Creating File Geodatabase")
arcpy.CreateFileGDB_management(out_location, name)

# Set workspace to new geodatabase
arcpy.env.workspace = path

# Import Raster
arcpy.AddMessage("Importing DEM")
arcpy.RasterToGeodatabase_conversion(input_raster, path)

# Create hillshade
if create_hillshade == True:
    arcpy.AddMessage("Creating hillshade")
    hillshade_name = "Hillshade"
    outHillShade = arcpy.sa.Hillshade(input_raster)
    outHillShade.save(hillshade_name)
    
# Extract spatial reference object from raster
arcpy.AddMessage("Extracting spatial reference object from raster")    
spatial_reference = arcpy.Describe(input_raster).spatialReference

# Create Cross_Sections Feature Class
arcpy.AddMessage("Creating Cross_Sections feature class")
crosssections_name = "Cross_Sections"
arcpy.CreateFeatureclass_management(path, crosssections_name, "POLYLINE", "", "", "ENABLED", spatial_reference)
crosssections_field_name = "XS_ID"
arcpy.AddField_management(crosssections_name, crosssections_field_name, "TEXT")

# Create Reaches Feature Class
arcpy.AddMessage("Creating Reaches feature class")
reaches_name = "Reaches"
arcpy.CreateFeatureclass_management(path, reaches_name, "POLYGON", "", "", "", spatial_reference)
reaches_field_name = "ReachID"
arcpy.AddField_management(reaches_name, reaches_field_name, "TEXT")

arcpy.AddMessage("Script finished")