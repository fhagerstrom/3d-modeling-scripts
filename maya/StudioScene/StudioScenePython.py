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

    left_light = CreateAreaLight('leftLight', 2.0, (1, 1, 1), (-5, 5, 0))
    right_light = CreateAreaLight('rightLight', 2.0, (1, 1, 1), (5, 5, 0))
    roof_lamp = CreateAreaLight('roofLamp', 2.0, (1, 1, 1), (0, 10, 0))

    # Create a plane
    plane = pm.polyPlane(width=20, height=10, subdivisionsX=1, subdivisionsY=1)[0]

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