﻿# Maya Tools and Scripts
This repo contains Maya scripts mostly written for developers and artists I'm working with for a game project - Kyber Initiative.
## Material ID Tool

### Installation

The script for the Material Id Tool is inside the scripts folder - ```materialId.py```

To utilize the script with Maya:
1. Save python file to your "scripts" folder in your project. For Windows users, this is usually in C:\Users\\[yourUser]\Documents\maya
2. Open the script editor in your scene. There are several ways: [MayaHelpScriptEditor](https://help.autodesk.com/view/MAYAUL/2023/ENU/?guid=GUID-7C861047-C7E0-4780-ACB5-752CD22AB02E)
3. Open the materialId.py script in the script editor and run

The script can also be saved to your shelf for easy access. Here is some Maya Documentation to save scripts to shelf: [MayaHelpSaveToShelf](https://help.autodesk.com/view/MAYAUL/2024/ENU/?guid=GUID-C693E884-F81A-4858-B5D6-3856EB8F394E)

When you run the script for the first time, it will generate all the materials and shader groups defined in the list. It will assign random colors to each material. There is a random seed defined so each artist that runs the script will generate the same random colors for each material. This can be edited in the code if desired.


