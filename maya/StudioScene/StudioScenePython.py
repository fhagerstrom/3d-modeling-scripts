import pymel.core as pm
import mtoa.utils as mutils

def CreateAreaLight(name, intensity, color, position):
    areaLight = pm.createNode('aiAreaLight', name=name)

    # Get the transform node for the area light
    transformNode = areaLight.getParent()

    # Set attributes for the area light
    areaLight.intensity.set(intensity)
    areaLight.color.set(color)
    transformNode.translate.set(position)


def CreateStudioScene():
    # Create a cube
    cube = pm.polyCube()[0]

    leftLight = CreateAreaLight('leftLight', 2.0, (1, 1, 1), (-5, 5, 0))
    rightLight = CreateAreaLight('rightLight', 2.0, (1, 1, 1), (5, 5, 0))
    roofLamp = CreateAreaLight('roofLamp', 2.0, (1, 1, 1), (0, 10, 0))

    # Create a plane
    backdropPlane = pm.polyPlane(name='backdrop', width=20, height=15, subdivisionsX=1, subdivisionsY=1)[0]
    pm.rotate(backdropPlane, 90, 0, 0)
    pm.move(backdropPlane, 0, 7, -9)
    
    backdropPlane = pm.ls(selection=True)[0]
    pm.select(backdropPlane.e[0])
    pm.polyExtrudeEdge(ltz = 15.0)
    pm.select(backdropPlane.e[0])
    pm.polyBevel(sg = 6, o = 1.4)
    
    pm.select(backdropPlane.f[-1])
    pm.delete()
    pm.select(backdropPlane.f[-1])
    pm.delete()

    # Create an Arnold skydome light for environment lighting
    environmentLight = pm.createNode('aiSkyDomeLight', name='environmentLight')

    # Set attributes for skydome light
    environmentLight.color.set(1, 1, 1)
    environmentLight.intensity.set(0.5)

    # Set render settings to use Arnold
    pm.setAttr('defaultRenderGlobals.currentRenderer', 'arnold', type='string')

    print("Studio scene created successfully!")

# Run function
CreateStudioScene()