## Introduction##

The Floodplain Mapper Toolbox is a collection of Python scripts for ArcGIS 10.1, 10.2, and 10.3 that preserve and extend the functionality of the Barr-NCED Floodplain Mapper, a tool that was developed in collaboration between Patrick Belmont at the National Center for Earth-Surface Dynamics (NCED) and Barr Engineering as part of the NCED Stream Restoration Toolbox (http://www.nced.umn.edu/content/stream-restoration-toolbox). Beginning with version 10.0 of ArcGIS, ESRI discontinued support for tools written in the proprietary VBA programming language as a means to encourage adoption of the open-source Python programming language for tool development. The Floodplain Mapper Toolbox is currently maintained by Patrick Belmont and Bruce Call at Utah State University. If you encounter any issues while using the toolbox, or have suggestions for a future update, please email Bruce at bruce.call@aggiemail.usu.edu.

## How it Works ##

The analysis employed by the Floodplain Mapper Toolbox measures floodplain inundation as a function of elevation above the geomorphic top of bank (also referred to as the elevation of the bankfull channel). This is accomplished by specifying this elevation at user-defined cross-sections (Figure 1), which are then used to interpolate a three-dimensional surface which models the channel's gradient (Figure 2). This surface can then be raised above the floodplain's surface by user-defined values in order to measure inundated areas as a function of simulated water surface elevations (Figure 3). The measured areas of inundation are derived only as a function of water surface elevation and do not take any hydraulic calculations into consideration. 

![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%201.png)

>Figure 1: Defined cross-sections, represented as black lines, intersect the floodplain perpendicular to the channel's direction of flow. The upstream cross-section (upper-left) has a defined top of bank elevation of 233.22 m, and the downstream cross-section (lower-right) has a defined top of bank elevation of 232.33 m. 

![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%202.png)

>Figure 2: Three-dimensional surface interpolated between the upstream cross-section (upper-left) and the downstream cross-section (lower-right), which models the channel gradient. Lighter blue colors represent higher elevations and darker blue colors represent lower elevations.

![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%203.png)

>Figure 3: Output of the Floodplain Mapper tool for a simulated water surface 8 m above the geomorphic top of bank. The colored layer is the areal extent of inundation and the color scheme represents the spatial variability of depth. Red represents deepest areas and blue represents the shallowest. 

## Using the Floodplain Mapper Toolbox in ArcGIS ##

You can watch a video demonstration of the steps outlined in this guide at https://www.youtube.com/watch?v=doq8ITCVdSg.

The Floodplain Mapper Toolbox requires licenses for both the Spatial Analyst and 3D Analyst extensions for ArcGIS. Before using the toolbox, make sure that both extensions have been activated by browsing to "Extensions" under the "Customize" menu (Figure 4).

![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%204.png)

>Figure 4: The 3D Analyst and Spatial Analyst extensions must be activated to use the Floodplain Mapper toolbox.

To use the Floodplain Mapper Toolbox, open the Arc Toolbox window, right-click on the Arc Toolbox folder at the top of the window, and select "Add Toolbox" (Figure 5). Browse to the folder containing the downloaded toolbox and select the Floodplain Mapper Toolbox (Figure 6).

 ![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%205.png)

>Figure 5: Add the Floodplain Mapper Toolbox to the ArcToolbox window by selecting "Add Toolbox".

 ![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%206.png)

Figure 6: Browse to the folder containing the downloaded toolbox and select the Floodplain Mapper Toolbox.


## Creating a new project ##

The "Create New Project" script performs the following 5 procedures in order: 

1. Creates a new file-geodatabase as a container for all inputs and also acts as the workspace environment for all geoprocessing routines used in the analysis script. The user will define a name for each new project, and that will be used to name the new file geodatabase.

2. Imports the DEM that will be used in the analysis to the new file-geodatabase. The DEM used in the analysis MUST be imported to this location in order for the analysis script to run. 

3. Creates a hillshaded raster of the input DEM if specified in the script's user-interface. This is extremely helpful for visualization while setting up the analysis. 

4. Creates a polygon feature class in the new file-geodatabase named Reaches. This will be used to define the areal extent of the analysis and allows the user to define discrete areas for which areal and volumetric statistics will be calculated in an output table. This feature class contains a field in its attribute table titled ReachID. In order for the analysis script to run, the user will need to define a unique name in the ReachID field for each feature in the attribute table.

5. Creates a 3D-enabled polyline feature class in the new file-geodatabase named Cross_Sections. This will be used to create the three-dimensional surface that models the channel gradient. This feature class contains a field titled XS_ID. In order for the analysis script to run, the user will need to define a unique name in the XS_ID field for each feature in the attribute table.

To start a new project, open the "Create New Project" script from the Floodplain Mapper Toolbox in the ArcToolbox window (Figure 7).  The script's user-interface (Figure 8) contains 4 user-defined parameters:

1. The output path to the directory where the new file-geodatabase will be created.

2. The project's name, which will be used to name the new file-geodatabase.

3. The file path of the input DEM.

4. Checked or unchecked box indicating whether the script will create a hillshaded raster for the input DEM (checked) or skip the hillshading step (unchecked).

 ![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%207.png)

>Figure 7: Select the "Create New Project" script from the Floodplain Mapper Toolbox in the ArcToolbox window.

 ![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%208.png)

>Figure 8: The user-interface for the "Create New Project" script requires 4 user-defined parameters.


## Editing input feature classes ##

In order to edit the feature classes created for you in the "Create New Project" script, you will need to run ArcMap and have the Editor toolbar activated. It can be activated by clicking the "Customize" menu, moving your mouse over "Toolbars", and selecting "Editor" from the drop-down menu (Figure 9). The Editor toolbar should now appear within your ArcMap window (Figure 10).

 ![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%209.png)

>Figure 9: Activate the Editor toolbar by navigating to the "Toolbars" drop-down menu in the "Customize" menu.

 ![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2010.png)

>Figure 10: The activated Editor toolbar within ArcMap ready for use.

To begin editing, add the Reaches and Cross_Sections layers to the ArcMap table of contents (Figure 11), and select "Start Editing" in the Editor toolbar's "Editor" drop-down menu in order to begin an editing session (Figure 12). 

 ![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2011.png)

>Figure 11: Add the Reaches and Cross_Sections feature classes to the ArcMap Table of Contents in order to begin editing them.

 ![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2012.png)

>Figure 12: Select "Start Editing" to begin an editing session in ArcMap.

Select the "Create Features" button on the far right-hand side of the Editor toolbar (Figure 13). This opens the "Create Features" window which will allow you to select the Reaches or Cross_Sections feature class (Figure 14). At the bottom of the same window is a panel titled "Construction Tools". To edit the Reaches feature class, select "Polygon". For the Cross_Sections layer, select the "line" tool.

 ![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2013.png)

>Figure 13: The "Create Features" button is located on the far right-hand side of the Editor toolbar. 

![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2014.png) 

>Figure 14: The "Create Features" window allows the user to select either the Cross_Sections or Reaches feature classes for editing.

 ![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2015.png)

>Figure 15: To edit the Reaches feature class, make sure the "Polygon" construction tool is selected in the "Construction Tools" panel of the "Create Features" window.

 ![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2016.png)

>Figure 16: To edit the Cross_Sections feature class, make sure the "Polygon" construction tool is selected in the "Construction Tools" panel of the "Create Features" window.

Each polygon feature in the Reaches feature class defines a discrete area of analysis. The analysis will only be performed within the polygons defined in the Reaches feature class. The user should try to create polygons in a way that ensures they will encompass the range of water surface elevations possible. For example, in Figure 17a, the Reach polygon (in red) is drawn parallel to the floodplain with its edges sitting above both valley walls visible in the hillshade layer. 

 ![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2017a.png)

>Figure 17a: An example of a polygon feature in the Reaches feature class. The analysis will be confined to the area within the polygon.

Each line feature in the Cross_Sections feature class should intersect the areas defined in the Reaches feature class perpendicular to the downstream direction of the floodplain. The user may create as many cross section features as they wish within a polygon, but it is best practice to have a cross section drawn along each section of a polygon in the Reaches feature class that is perpendicular to the downstream direction of the floodplain (Figure 17b).

  ![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2017b.png)

>Figure 17b: Cross sections (in blue) drawn along the edges of the Reaches polygons that are perpendicular to the downstream direction of the floodplain.

In order for the analysis script to run, the user must define a name for each cross section feature in the attribute table of the Cross_Sections feature class in the XS_ID field (Figure 18). The user must also define a name for each polygon feature in the attribute table of the Reaches feature class (Figure 19). The user must be in an editing session in order to enter attributes into an attribute table, and must manually end an editing session when finished (Figure 20).

 ![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2018.png) 

>Figure 18: Each feature in the Cross_Sections feature class must be given a name in the XS_ID field in order for the analysis script to run. 

  ![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2019.png) 

>Figure 19: Each feature in the Reaches feature class must be given a name in the ReachID field in order for the analysis script to run. 

  ![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2020.png) 

>Figure 20: The user must manually end an editing session.


## Calculating water surface elevations from the DEM ##

Once the Reaches and Cross_Sections feature classes have been prepared, the "Get Water Surface Elevations" script will generate a table from which the user can generate simulated water surface elevations. To run the script, open the "Get Water Surface Elevations" script in the ArcToolbox (Figure 21) and supply the 3 user-defined parameters in the user-interface (Figure 22):

1. The path to the file-geodatabase created in the "Create New Project" script, which acts as the geoprocessing workspace.  

2. The project's DEM.

3. The Cross_Sections feature class.

  ![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2021.png) 

Figure 21: Select the "Get Water Surface Elevations" script from the ArcToolbox window.

   ![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2022.png) 

Figure 22: The user-interface for the "Get Water Surface Elevations" script requires 4 user-defined parameters. 

A table named "Stage_Data" will be saved to project's workspace. To access it within ArcMap, add the Stage_Data table to your document and open it by clicking on the "List Sources" tab in the ArcMap table of contents (Figure 23). You must use the "List Sources" tab to access it, since tables do not appear in the Table of Content's default "List by Drawing Order" tab.  

   ![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2023.png) 

Figure 23: The Stage_Data table will only be visible within the "List Sources" tab of the table of contents.

The Stage_Data table contains the name defined by the user for each feature in the Cross_Sections feature class in the XS_ID field, as well as a field titled "MIN_Z_Value" which contains the lowest elevation calculated from the project's DEM along each of the cross section features (Figure 24). This elevation is assumed to be the water surface elevation at the point where the cross section intersects the channel and is useful for calculating stage elevations for simulated water surface profiles. 

![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2024.png)  

Figure 24: The Stage_Data table contains the names of each cross section feature and an associated water surface elevation of the channel.


##Calculating stage elevations for analysis##

In order to measure the geomorphic top of bank from the project's DEM, open the 3D Analyst toolbar within your ArcMap document (Figure 25). In the drop-down menu, select the project's DEM. A common mistake is to have the hillshade selected while using items in the 3D Analyst toolbar. This will lead to inaccurate and confusing results from the tools. Once correctly set, select the "interpolate line" tool from the toolbar and draw along each cross section parallel to the channel (Figure 26). 

![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2025.png)  

Figure 25: Before using the "interpolate line" tool (in red), make sure the project's DEM is selected in the drop-down menu instead of the hillshade.

![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2026.png) 

Figure 26: Use the "interpolate line" to draw a line along each cross section perpendicular to the channel.

Once the line from the "interpolate line" tool has been drawn, click the "Profile Graph" button in the 3D Analyst toolbar (Figure 27). This produces a two-dimensional cross section of the DEM along the specified path (Figure 28). Measuring the geomorphic top of bank from this graph alone may be difficult. For precise measurements, right-click the graph and select "properties" (Figure 29), set the graph type to "Scatter Plot" (Figure 30), and set the "Y field" to "Z" (Figure 31). This shows each of the DEM's discrete elevations along the cross section as identifiable points. A precise measurement for each point can be obtained by right clicking on the point determined by the user to be the geomorphic top of bank, and clicking "Identify" (Figure 32). This opens a window that displays the point's elevation as the value for "Z" (Figure 33).

![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2027.png) 

Figure 27: Click the "Profile Graph" button to generate a two-dimensional view of the cross section.

![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2028.png) 

Figure 28: An example of a two-deimsional cross section graph generated by the "Profile Graph" button.

![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2029.png) 

Figure 29: Right-clicking the graph and select "properties". 

![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2030.png)  

Figure 30: Select the graph type to be "Scatter Plot".

![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2031.png)   

Figure 31: Set the "Y field" to "Z".

![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2032.png)   

Figure 32: Select the point determined to be the geomorphic top of bank, right click, and select "Identify".

![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2033.png)   

Figure 33: The elevation of the geomorphic top of bank is the value denoted by "Z".

To append values for the geomorphic top of bank to the Stage_Data table, click the Table menu button (Figure 34), and select "Add Field" (Figure 35). In the Add Field dialog box, give the field a name without spaces and select the data type as "Float" (Figure 36).

![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2034.png)   

Figure 34: Select the table menu button.

![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2035.png)   

Figure 35: Select "Add Field".

![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2036.png)   

Figure 36: After naming the field, change the data type to "Float".

Stage elevations can be calculated above and below the geomorphic top of bank by using the Field Calculator tool. It is accessed by right clicking on the field name and selecting "Field Calculator" (Figure 37). If you are not in an edit session, you may receive a message warning you that values calculated outside of an edit session cannot be undone (Figure 38). This should not be a problem if you are calculating values in a new field that contains null values.

![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2037.png)   

Figure 37: Select the Field Calculator by right clicking on the field name.

![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2038.png)   

Figure 38: You may receive a warning about calculating values outside of an editing session. This should not be a problem.

In the Field Calculator dialog, an expression for each field can be constructed by selecting the name of the field containing values for the geomorphic top of bank from the "Fields" box and adding or subtracting a desired increment from that value (Figure 39). This will calculate a value for each row of the field (Figure 40). 
 
![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2039.png)  

Figure 39: Values for each row in a field are calculated by constructing an expression with the name of the field containing values for the geomorphic top of bank and the addition or subtraction of a desired increment in stage.

![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2040.png)  

Figure 40: An example of calculated stage elevations for each cross section in the Stage_Data table.


## Running the Floodplain Mapper analysis script##

To run the floodplain mapper analysis, select the "Run Analysis" script from the Floodplain Mapper Toolbox in the ArcToolbox window (Figure 41). The script's user-interface (Figure 42) contains 9 user-defined parameters:

1. The path to the file-geodatabase containing the project's input files.

2. The path to the folder location where a geodatabase containing the output files will be created.

3. The project's DEM.

4. The resolution of the input DEM based on pixel size.

5. The Reaches feature class.

6. The Cross_Sections feature class.

7. The Stage_Data table

8. The stage fields from the Stage_Data table that the analysis will be performed (stage will be included if the box next to the field name is checked).

9. Check box indicating whether the intermediate files from the analysis will be saved along with the output files to the output geodatabase.

![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2041.png)   

Figure 41: Select the "Run Analysis" script from the Floodplain Mapper Toolbox.

![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2042.png)   

Figure 42: The user-interface for the "Get Water Surface Elevations" script requires 9 user-defined parameters.

When the script is finished, you can view the outputs by browsing the folder where you indicated the output file-geodatabase to be saved to. Each output file will be named "FMT" followed by a string containing the date and time the analysis was performed (Figure 43). Within the file-geodatabase, there will be three output files from each stage calculated in the analysis (Figure 44):

1. Depthgrid raster containing depth values for each pixel inundated by at a calculated stage.

2. Polygon feature class that represents the areal extent of inundation at a calculated stage.

3. Table containing areal and volumetric statistics for the calculated stage.

![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2043.png)   

Figure 43: The scripts outputs will be stored in a file-geodatabase named "FMT" followed by the date and time at which the analysis was performed.

![picture alt](https://github.com/brucecc88/Floodplain-Mapper-Toolbox/blob/master/User-guide%20Figures/Figure%2044.png)   

Figure 44: Output files from the "Run Analysis" script.





