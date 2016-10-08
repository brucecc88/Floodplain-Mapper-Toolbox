# Floodplain Mapper Toolbox 1.2 for ArcGIS 10x
# Adapted for Python from the Barr-NCED Floodplain Mapper

import arcpy

# Inputs
input_geodatabase = arcpy.GetParameterAsText(0)
DEM = arcpy.Describe(arcpy.GetParameterAsText(1)).name
CrossSections = arcpy.Describe(arcpy.GetParameterAsText(2)).name

# Set workspace
arcpy.env.workspace = input_geodatabase

# Check if another copy exists
if arcpy.ListTables("Stage_Data") != []:
    arcpy.AddError("Overwrite set to False, but Stage_Data table exists in workspace. Rename or delete the current table before recalculating water surface elevations")
    raise RuntimeError

# Check for extensions
if arcpy.CheckOutExtension("3D") != "CheckedOut":
    arcpy.AddMessage("3D Analyst not available")
else:
    arcpy.AddMessage("3D Analyst checked out")

# Validate Cross Sections
with arcpy.da.SearchCursor(CrossSections, "XS_ID") as cursor:  
    for row in cursor:  
        if row[0] == "" or row[0] == None:
            arcpy.AddError("Cross_Sections feature class has Null values in the XS_ID field")
            raise RuntimeError

# Create Stage_Data Table
arcpy.AddMessage("Creating Stage_Data table")
table_name = "Stage_Data"
arcpy.CreateTable_management(input_geodatabase, table_name)

# Add Z column to table
arcpy.AddZInformation_3d(CrossSections, 'Z_MIN', 'NO_FILTER')

# Get the Z_min value
arcpy.AddSurfaceInformation_3d(CrossSections, DEM, "Z_MIN")

# Extract XS_IDs
XS_IDs = [row[0] for row in arcpy.da.SearchCursor(CrossSections, "XS_ID")]

# Extract Min_Z Values
Min_Zs = [row[0] for row in arcpy.da.SearchCursor(CrossSections, "Z_min")]

# Insert values into Stage Data Table
zipped = zip(XS_IDs, Min_Zs)
arcpy.AddField_management(table_name, "XS_ID", "TEXT")
arcpy.AddField_management(table_name, "MIN_Z_Value", "FLOAT")

# Use insert cursor to add rows
rows = arcpy.InsertCursor(table_name)
for i in zipped:
    row = rows.newRow()
    row.setValue("XS_ID", i[0])
    row.setValue("MIN_Z_Value", i[1])
    rows.insertRow(row)
del row
del rows

arcpy.AddMessage("")
arcpy.AddMessage("Script finished")