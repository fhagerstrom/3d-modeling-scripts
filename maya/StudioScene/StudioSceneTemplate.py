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


def CreateStudioScene():
    # Create a cube as a model placeholder. Replace cube with own model(s) for rendering showcase
    cube = pm.polyCube(name="modelPlaceholder", width=5, height=5, depth=5)[0]

    leftLight = CreateAreaLight('leftLight', 2.0, (1, 1, 1), (5, 5, 5), (-9, 6, 0), (0, -90, 0))
    rightLight = CreateAreaLight('rightLight', 2.0, (1, 1, 1), (5, 5, 5), (9, 6, 0), (0, 90, 0))
    roofLamp = CreateAreaLight('roofLamp', 2.0, (1, 1, 1), (5, 5, 5), (0, 10, 0), (-90, 0, 0))

    # Create a plane as a backdrop
    backdropPlane = pm.polyPlane(name='backdrop', width=30, height=15, subdivisionsX=1, subdivisionsY=1)[0]
    pm.rotate(backdropPlane, 90, 0, 0)
    pm.move(backdropPlane, 0, 7, -9)

    # Select the plane, store it in the backdropPlane variable
    # Extrude the bottom edge, then bevel it in 6 segments and put an offset of 1.4
    backdropPlane = pm.ls(selection=True)[0]
    pm.select(backdropPlane.e[0])
    pm.polyExtrudeEdge(ltz=30.0)
    pm.select(backdropPlane.e[0])
    pm.polyBevel(sg = 6, o = 1.4)

    # Select and delete two corner faces that is created after beveling the plane edge
    pm.select(backdropPlane.f[-1])
    pm.delete()
    pm.select(backdropPlane.f[-1])
    pm.delete()
    
    # Create SkyDome light
    mutils.createLocator("aiSkyDomeLight", asLight=True)

    # Rename the light and set attributes
    skyLight = cmds.rename('skyLight')
    pm.setAttr(skyLight + '.intensity', 0.25)
    pm.setAttr(skyLight + ".aiNormalize", False)

    print("Studio scene created successfully!")

# Run function
CreateStudioScene()
