import pymel.core as pm
import maya.cmds as cmds
import mtoa.utils as mutils

def CreateAreaLight(name, intensity, color, scale, position, rotation):
    
    # Create aiAreaLight as a locator (transform node)
    areaLight = mutils.createLocator("aiAreaLight", asLight=True)
    
    # Rename the light
    areaLight = cmds.rename(name)

    # Set attributes for the light
    cmds.setAttr(areaLight + '.intensity', intensity)
    cmds.setAttr(areaLight + '.color', color[0], color[1], color[2])
    cmds.setAttr(areaLight + '.normalize', False)

    # Set transform attributes
    cmds.scale(scale[0], scale[1], scale[2], name)
    cmds.move(position[0], position[1], position[2], name)
    cmds.rotate(rotation[0], rotation[1], rotation[2], name)

def CreateSkyDomeSetting():
    # Create a floor plane
    floorPlane = pm.polyPlane(name='floor', width=50, height=50, subdivisionsX=1, subdivisionsY=1)[0]

    # Create SkyDome light
    skyLight = mutils.createLocator('aiSkyDomeLight', asLight=True)
    
    skyLight = cmds.rename('skyLight')
    cmds.setAttr(skyLight + ".intensity", 0.2)
    cmds.setAttr(skyLight + ".aiNormalize", False)
    
    warmLight = CreateAreaLight('warmLight', 4.0, (1, 1, 1), (9, 5, 9), (0, 15, 20), (-40, 0, 0))
    coolLight = CreateAreaLight('coolLight', 4.0, (1, 1, 1), (4, 3, 4), (15, 15, 5), (-40, 90, 0))
    midLight = CreateAreaLight('midLight', 4.0, (1, 1, 1), (7, 4, 9), (0, 10, 0), (-60, -90, 0))
    
    
CreateSkyDomeSetting()
    