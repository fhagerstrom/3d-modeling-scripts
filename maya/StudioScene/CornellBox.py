import pymel.core as pm
import maya.cmds as cmds
import mtoa.utils as mutils

def CreateCornellBox():
    # Create a cube and delete front face
    cornellCube = pm.polyCube(name="cornellCube", width=10, height=10, depth=10)[0]
    pm.select(cornellCube.f[4])
    pm.delete()
    
    # Create variable for materials
    redMaterialName = "redLambert"
    greenMaterialName = "greenLambert"
    
    # Check if hypershade material already exists. Creates the material if it does not
    if not pm.objExists(redMaterialName):
        redMaterial = pm.shadingNode("lambert", asShader=True, name=redMaterialName)
        redMaterial.color.set([1, 0, 0])  # Set the color to red
    else:
        redMaterial = pm.PyNode(redMaterialName)

    if not pm.objExists(greenMaterialName):
        greenMaterial = pm.shadingNode("lambert", asShader=True, name=greenMaterialName)
        greenMaterial.color.set([0, 1, 0])  # Set the color to green
    else:
        greenMaterial = pm.PyNode(greenMaterialName)
        
    # Red left
    pm.select(cornellCube.f[0])
    pm.hyperShade(assign=redMaterial)
    
    # Green right
    pm.select(cornellCube.f[2])
    pm.hyperShade(assign=greenMaterial)
    
    # Create two cubes to act as pedestal
    pedestalCube = pm.polyCube(name="pedestalCube", width=2, height=2, depth=2)[0]
    pm.move(pedestalCube, -0.6, -4.0, -2)
    pm.rotate(pedestalCube, 0, -20, 0)
    
    pedestalCube1 = pm.polyCube(name="pedestalCube1", width=2, height=4, depth=2)[0]
    pm.move(pedestalCube1, -1.5, -3.0, 2)
    pm.rotate(pedestalCube1, 0, 20, 0)
    
    # Create area light as a roof light
    roofLight = mutils.createLocator("aiAreaLight", asLight=True)
    
    # Rename the light
    roofLight = cmds.rename("roofLight")

    # Set attributes for the light
    cmds.setAttr(roofLight + ".intensity", 5.0)
    cmds.setAttr(roofLight + ".exposure", 2.0)
    cmds.setAttr(roofLight + ".color", 1, 1, 1)
    cmds.setAttr(roofLight + ".normalize", False)
    
    # Set transform attributes
    cmds.scale(1, 2.5, 3, "roofLight")
    cmds.move(0, 4.9, 0, "roofLight")
    cmds.rotate(-90, 0, 0, "roofLight")
    
    # Create SkyDome light
    skyLight = mutils.createLocator('aiSkyDomeLight', asLight=True)
    
    skyLight = cmds.rename("skyLight")
    cmds.setAttr(skyLight + ".intensity", 0.25)
    cmds.setAttr(skyLight + ".aiNormalize", False)
    
CreateCornellBox()