import pymel.core as pm
import maya.cmds as cmds
import mtoa.utils as mutils

def CreateAreaLight(name, scale, position, rotation):
    
    # Create aiAreaLight as a locator (transform node)
    areaLight = mutils.createLocator("aiAreaLight", asLight=True)
    
    # Rename the light
    areaLight = cmds.rename(name)

    # Set attributes for the light
    cmds.setAttr(areaLight + '.intensity', 2.0)
    cmds.setAttr(areaLight + '.color', 1, 1, 1)
    cmds.setAttr(areaLight + '.normalize', False)

    # Set transform attributes
    cmds.scale(scale[0], scale[1], scale[2], name)
    cmds.move(position[0], position[1], position[2], name)
    cmds.rotate(rotation[0], rotation[1], rotation[2], name)


def CreateStudioScene():
    # Create area lights
    leftLight = CreateAreaLight('leftLight', (5, 5, 5), (-10, 7, 0), (0, -90, 0))
    rightLight = CreateAreaLight('rightLight', (5, 5, 5), (10, 7, 0), (0, 90, 0))
    topLight = CreateAreaLight('topLight', (5, 5, 5), (0, 12, 0), (-90, 0, 0))
    
    # Create a floor plane
    floorPlane = pm.polyPlane(name='floor', width=50, height=25, subdivisionsX=1, subdivisionsY=1)[0]
    
    # Create a backdrop plane
    backdropPlane = pm.polyPlane(name='backdrop', width=20, height=20, subdivisionsX=1, subdivisionsY=1)[0]
    pm.move(backdropPlane, 0, 0.25, 0)
    
    # Extrude and bevel the plane to create the backdrop
    backdropPlane = pm.ls(selection=True)[0]
    pm.select(backdropPlane.e[3])
    pm.polyExtrudeEdge(ltz = 15.0)
    pm.select(backdropPlane.e[3])
    pm.polyBevel(oaf=0.4, sg=12) # fractions, segments
    
    # Delete faces on the sides.
    pm.select(backdropPlane.f[-1])
    pm.delete()
    pm.select(backdropPlane.f[-1])
    pm.delete()
    
    # Put some thickness on it
    pm.select(backdropPlane)
    pm.polyExtrudeFacet(thickness=0.2)
    
    # Create left wall
    leftWallPlane = pm.polyPlane(name='leftWall', width=15, height=15, subdivisionsX=1, subdivisionsY=1)[0]
    pm.rotate(leftWallPlane, 0, 0, 90)
    pm.move(leftWallPlane, -10.5, 7.5, 0)
    
    # Create right wall
    rightWallPlane = pm.polyPlane(name='rightWall', width=15, height=15, subdivisionsX=1, subdivisionsY=1)[0]
    pm.rotate(rightWallPlane, 0, 0, -90)
    pm.move(rightWallPlane, 10.5, 7.5, 0)

    # Create SkyDome light
    skyLight = mutils.createLocator("aiSkyDomeLight", asLight=True)
    
    skyLight = cmds.rename('skyLight')
    cmds.setAttr(skyLight + '.intensity', 0.25)
    cmds.setAttr(skyLight + ".aiNormalize", False)

    print("Studio scene created successfully!")

# Run function
CreateStudioScene()