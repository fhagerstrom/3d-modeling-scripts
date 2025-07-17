import pymel.core as pm
import pymel.core.datatypes as dt
import maya.cmds as cmds
from random import randint, uniform, choices

from PySide6 import QtCore
from PySide6 import QtWidgets
from pymel.internal.plogging import pymelLogger as log
import pymel.util.mathutils as math

# WINDOW DIMENSIONS
winWidth = 640
winHeight = 480

# Placeholder variables for nodes
branchNode = 0
twigNode = 0
twigNodes = []
leafNodes = []

# Slider globals
branchHeightSlider = None
branchRadiusSlider = None
subdivsHeightSlider = None
twigCountSlider = None
leafCountSlider = None

# Material globals
woodMaterial = None
leafMaterial = None

''' 
Function to create a branch with a set number of edge loops / subdivs 
The height and amount of subdivs is set between a certain range by the user inside the UI.
'''
def createBranch():
    global branchNode
    
    # Delete previously created branch if there's one
    if branchNode:
        tempBranchP = pm.listConnections(branchNode)[0]
        tempBranchT = pm.listConnections(tempBranchP)[2]
        pm.delete(tempBranchT)
        branchNode = 0
    
    branchHeight = branchHeightSlider.value()
    branchRadius = uniform(0.6, 0.9)
    subdivsHeight = subdivsHeightSlider.value()
    
    # Create a cylinder as base for the branch
    branchNode = pm.nodetypes.PolyCylinder(h=branchHeight, r=branchRadius, sh=subdivsHeight)
    branchT = pm.listConnections(branchNode)[0]
    
    # UV mapping
    cmds.UVCylindricProjection()
    cmds.polyEditUV(pu=3, pv=0.5, su=1, sv=4) # su / sv - Texture scaling
    cmds.dR_DoCmd('modeObject') # Go back to object selection mode
    
    # Get amount of faces on the transform node of the branch.
    # Select the top face to move and rotate the branch to deform the branch.
    numFaces = branchT.numFaces()
    pm.select(branchT + ".f[" + str(numFaces - 1) + "]")
    
    pm.softSelect(softSelectEnabled=True, ssd=15)
    
    randomX = uniform(0, 6)
    randomY = uniform(0, 6)
    randomZ = uniform(0, 6)
    randomRotation = uniform(30, 90)
    
    cmds.move(randomX, randomX, randomZ, r=True)
    pm.rotate(0, 0, randomRotation)
    cmds.scale(0.4, 1, 0.4, r=True)
        
    log.info("Created branch successfully!")
    
    
''' GET CENTER POINTS FROM BRANCH '''
def generatePoints(node, pointList):
    # Get branchNode transform
    # List connections twice since the transform component changes index 
    # after performing UV mapping
    nodeP = pm.listConnections(node)[0]
    nodeT = pm.listConnections(nodeP)[2]
    
    # Get amount of subdivs on the height and on the axis
    subdivsH = node.getSubdivisionsHeight()
    subDivsA = node.getSubdivisionsAxis()
    
    # Define amount of edge loops, create an empty list to append center points of edge loops
    # and get the vertices of the entire mesh.
    loops = subdivsH + 1
    loopCenterPoints = []
    vertices = nodeT.getPoints(space="world")
    
    # For all the edge loops on the branch...
    for x in range(loops):
        # Create an empty list for all vertices per edge loop
        loopVertices = []
        # Keep track of the index per loop
        index = int(subDivsA * x)
        # For every subdiv on the axis...
        for y in range(subDivsA):
            # Append the vertices on each edge loop
            loopVertices.append(vertices[index + y])
        # Define a center point vector
        cPoints = [0, 0, 0]
        # For every edge loop vertice
        for z in loopVertices:
            # Add edge loop vertice vector to the center point vector
            cPoints += z
        # Calculate center points per edge loop
        cPoints = cPoints / subDivsA
        loopCenterPoints.append(cPoints)
        pointList.append(cPoints)

   
''' CREATE TWIGS '''
def createTwig(centerPoints):
    global branchNode
    global twigNodes
    
    pointList = []
    
    generatePoints(branchNode, pointList)
    
    # Get the transform node of the branch
    # Is used to to a lerp on twig radius depending on branch height
    branchP = pm.listConnections(branchNode)[0]
    branchT = pm.listConnections(branchP)[2]
    
    # Delete twigs if there are any in the scene already
    deleteTwigs()
    
    # Create twig at current center point
    for x in range(twigCountSlider.value()):
       
        # Set a random value between the center points on the branch
        randomPoint = randint(int(branchNode.getSubdivisionsHeight() / 3), len(centerPoints) - 2) # Randomize all center points except the bottom and top of branch
        
        # Create a weightlist for random choices
        # So the twigs are not created at the bottom and top edge loops
        weightList = list(range(3, branchNode.getSubdivisionsHeight() + 3))
        
        weightList[0] = 0
        weightList[1] = 0
        
        centerPointList = range(0, branchNode.getSubdivisionsHeight())
            
        randomPointIndex = choices(centerPointList, weightList, k=1)[0]
        
        randomPointIndex = min(randomPointIndex, branchNode.getSubdivisionsHeight() - 2)
        
        # print("RAND POINT CHOICES: " + str(randomPointIndex))
        
        # Randomize twig size snd subdivs for twisting and deformation
        twigRadius = 0.5
        twigLength = uniform(4, 8)
        twigSubdivs = uniform(int(twigLength)-1, int(twigLength))
        
        # Create the twig and get it's transform
        twigNode = pm.nodetypes.PolyCylinder(r=twigRadius, h=twigLength, sh=twigSubdivs)
        twigT = pm.listConnections(twigNode)[0]
         
        # UV mapping
        cmds.UVCylindricProjection()
        cmds.polyEditUV(pu=3, pv=0.5, su=1, sv=4) # su / sv - Texture repeat
        cmds.dR_DoCmd('modeObject') # Go back to object selection mode
        
        # Move pivot of the twig to it's bottom. Moving it negative half it's height.
        # Moving it positive it's height will put the pivot on the top 
        cmds.move(0, -twigLength * 0.5, 0, twigT + ".scalePivot", twigT + ".rotatePivot", r=True)
        cmds.BakeCustomPivot(twigT)
        
        # Move the twig to a random center point
        cmds.move(centerPoints[randomPointIndex].x, centerPoints[randomPointIndex].y, centerPoints[randomPointIndex].z)
        
        # Get the twig position on the Y axis
        twigPosY = pm.xform(twigT, query=True, t=True, ws=True)[1]
        
        # Get the branches' bounding box to make twigs smaller if they are higher up on the branch
        branchBox = branchT.boundingBox()
        
        minPoint = branchBox.min()[1] # Get the Y axis
        maxPoint = branchBox.max()[1] # Get the Y axis
        
        # Lerp the points in relation to the branch height and twig's position on the Y axis
        lerp = math.linmap(maxPoint, minPoint, twigPosY)
        
        # Force the lerp to be at least a set value
        if lerp < 0.2:
            lerp = 0.2
        
        twigRadius *= lerp
        
        twigNode.setRadius(twigRadius)
        
        # Rotate the twigs in random positions
        # Forcing rotation order to z, x, y
        pm.xform(twigT, ro=(0, uniform(0, 359), 0), roo='zxy', eu=True, ws=True, r=True)
        pm.xform(twigT, ro=(0, 0, 30), roo='zxy', eu=True, ws=True, r=True)   
        
        # Get amount of faces on the transform node of the twig.
        # Select the top face and deform the twig.
        numFaces = twigT.numFaces()
        pm.select(twigT + ".f[" + str(numFaces - 1) + "]")
        
        # Soft select for deformation
        pm.softSelect(softSelectEnabled=True, ssd=7.5)
        
        deformFactor = uniform(0.2, 0.5)
        scaleFactor = uniform(0.3, 0.5)
        
        cmds.move(0, deformFactor, deformFactor, r=True)
        cmds.rotate(0, 0, uniform(0, 75), r=True)
        
        # Reset pivot point on twig for scaling
        cmds.CenterPivot(twigT)
        
        cmds.scale(scaleFactor, 1, scaleFactor, r=True)

        # Append the twig node to the twig node list
        twigNodes.append(twigNode)
    
    log.info("Created twigs successfully!")
    print(centerPoints)

''' Generate twigs from branch center point data '''  
def generateTwigs():
    
    global branchNode
    
    pointList = []
    
    generatePoints(branchNode, pointList)
    
    # Check if the pointList is not empty
    if pointList:
        # Create twigs
        createTwig(pointList)
    else:
        log.info("No center points found on branch. Have you created a branch at all?")

''' Delete all twigs - Called when creating twigs to simply replace them 
    if there are any in the scene already '''   
def deleteTwigs():
    global twigNodes
    
    # If twigs are deleted manually, this wont find anything in the list and throw an error
    # Not necessary to take into account for
    for twigNode in twigNodes:
        tempTwigP = pm.listConnections(twigNode)[0]
        tempTwigT = pm.listConnections(tempTwigP)[2]
        pm.delete(tempTwigT)
        
    # Clear list
    twigNodes = []
    
def createLeaves():
    global branchNode
    global twigNodes
    global leafNodes
    
    if not twigNodes:
        log.info("No twigs found. Generate twigs first.")
        return
       
        
    # Delete previously generated leaves if there are any   
    deleteLeaves()
    
    # Get the transform node of the branch
    branchP = pm.listConnections(branchNode)[0]
    branchT = pm.listConnections(branchP)[2]
    
    # Get the value of leaves from slider    
    leafCount = leafCountSlider.value()
    
    leafWidth = 0.75
    leafHeight = uniform(1.0, 1.5)
    
    # Loop through all elements in twig node list
    for twigNode in twigNodes:
        
        # print(twigNode)

        # Create an empty list for the twigs center points.
        twigPoints = []
        
        # Calculate the center points for the twigs.
        # For placement of leaves, in the same way twigs are placed in the branch
        generatePoints(twigNode, twigPoints)
        
        # Get the transform node of the twig
        twigP = pm.listConnections(twigNode)[0]
        twigT = pm.listConnections(twigP)[2]
        
        # Get the rotation of the twig in world space
        twigRotation = pm.xform(twigT, query=True, rotation=True, worldSpace=True)
        
        # print("TWIG ROTATION: ", str(twigRotation))
        
        # Exclude the bottom edge loop from the selection
        validPoints = twigPoints[1:]
        
        # Loop through every leaf
        for _ in range(leafCount):
            
            # Randomly select a center point on the twig
            randomPoint = choices(validPoints, k=1)[0]
            
            # Perform a random transform within a small range
            offset = uniform(1.25, 1.75)

            twigRadius = twigNode.getRadius()
            
            offsetXZ = uniform(-twigRadius * offset, twigRadius * offset)
            offsetY = uniform(0.6, 1.0) * twigRadius
      
            # Set the leaf position around the twig's top
            leafPosition = [randomPoint.x + offsetXZ, randomPoint.y + offsetY, randomPoint.z + offsetXZ]
       
            # print(leafPosition)
            
            # Create leaf
            leafNode = pm.nodetypes.PolyPlane(w=leafWidth, h=leafHeight, sw=1, sh=1)
            leafT = pm.listConnections(leafNode)[0]
            # print(leafT)
            # print(leafNode)
            
            # Move it to calculated position
            cmds.move(leafPosition[0], leafPosition[1], leafPosition[2])
            
            # Rotate the leaf to align with the twig's rotation
            pm.rotate(leafT, twigRotation[0], twigRotation[1], twigRotation[2], r=True)

            # Parent leaves to twig
            pm.parent(leafT, twigT)
            
            # Rotate after parenting to get variation
            pm.rotate(leafT, uniform(30, 60), uniform(60, 120), -twigRotation[2])
            
            # Append leaves to leaf node list
            leafNodes.append(leafNode)
        
        # Parent twig to branch   
        pm.parent(twigT, branchT)
           
            
    log.info("Created leaves successfully!")
                     
def deleteLeaves():
    global leafNodes
    
    # If leaves are deleted manually, this wont find anything in the list and throw an error
    # Not necessary to take into account for
    for leafNode in leafNodes:
        tempLeafT = pm.listConnections(leafNode)[0]
        pm.delete(tempLeafT)
        
    # Clear list
    leafNodes = []
            
''' Delete all objects in the scene '''          
def clearScene():
    global branchNode, twigNodes, leafNodes
    
    # Get all deleteable objects in the scene.
    cmds.select(all=True)
    cmds.delete()
    branchNode = 0
    twigNodes.clear()
    leafNodes.clear()
    
    
    log.info("Cleared all objects in scene!")
    
''' Create a material for the loaded texture '''  
def createMaterial(name, texturePath, transparent):
    sNode = cmds.shadingNode('lambert', name='%s_lambert' % name, asShader=True)
    sNodeSG = cmds.sets(name='%sSG' % sNode, empty=True, renderable=True, noSurfaceShader=True)
    cmds.connectAttr('%s.outColor' % sNode, '%s.surfaceShader' % sNodeSG)
    #cmds.sets('leaf', e=True, forceElement=sNodeSG)
        
    baseName = os.path.basename(texturePath)
    prefix = baseName.split('.')[0]
        
    fileNode = cmds.shadingNode('file', asTexture=True)
    cmds.setAttr(fileNode+'.fileTextureName', texturePath, type='string')
        
    placeNode = cmds.shadingNode('place2dTexture',asUtility=True,n=prefix+'_place2dTexture')
    cmds.connectAttr(placeNode+'.coverage',fileNode+'.coverage',f=True)
    cmds.connectAttr(placeNode+'.translateFrame',fileNode+'.translateFrame',f=True)
    cmds.connectAttr(placeNode+'.rotateFrame',fileNode+'.rotateFrame',f=True)
    cmds.connectAttr(placeNode+'.mirrorU',fileNode+'.mirrorU',f=True)
    cmds.connectAttr(placeNode+'.mirrorV',fileNode+'.mirrorV',f=True)
    cmds.connectAttr(placeNode+'.stagger',fileNode+'.stagger',f=True)
    cmds.connectAttr(placeNode+'.wrapU',fileNode+'.wrapU',f=True)
    cmds.connectAttr(placeNode+'.wrapV',fileNode+'.wrapV',f=True)
    cmds.connectAttr(placeNode+'.repeatUV',fileNode+'.repeatUV',f=True)
    cmds.connectAttr(placeNode+'.offset',fileNode+'.offset',f=True)
    cmds.connectAttr(placeNode+'.rotateUV',fileNode+'.rotateUV',f=True)
    cmds.connectAttr(placeNode+'.noiseUV',fileNode+'.noiseUV',f=True)
    cmds.connectAttr(placeNode+'.vertexUvOne',fileNode+'.vertexUvOne',f=True)
    cmds.connectAttr(placeNode+'.vertexUvTwo',fileNode+'.vertexUvTwo',f=True)
    cmds.connectAttr(placeNode+'.vertexUvThree',fileNode+'.vertexUvThree',f=True)
    cmds.connectAttr(placeNode+'.vertexCameraOne',fileNode+'.vertexCameraOne',f=True)
    cmds.connectAttr(placeNode+'.outUvFilterSize',fileNode+'.uvFilterSize',f=True)
    cmds.connectAttr(placeNode+'.outUV',fileNode+'.uv',f=True)

    cmds.connectAttr(fileNode+'.outColor', sNode+'.color', f=True)
    if transparent == True:
        cmds.connectAttr(fileNode+'.outTransparency', sNode+'.transparency', f=True)
    log.info('Material created!')  
    return sNodeSG
    
''' Load texture for the branch and the twigs '''    
def loadWoodTexture():
    global woodMaterial
    filename, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Load wood texture", "")
    if filename:
        woodMaterial = createMaterial("mWood", filename, transparent=False)
        
    else:
        log.info("Wood texture file is missing or not loaded!")
        
''' Load texture for the leaves '''     
def loadLeafTexture():
    global leafMaterial
    filename, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Load leaf texture", "")
    if filename:
        leafMaterial = createMaterial("mLeaf", filename, transparent=True)
        
    else:
        log.info("Leaf texture file is missing or not loaded!")
        
''' Generate all the steps in one go '''
def generateEntireTree():
    
    clearScene()
    
    createBranch()

    generateTwigs()

    createLeaves()
    
    log.info("Generated all parts of the tree!")
           

''' Create UI '''
def createUI():
    global win, branchHeightSlider, subdivsHeightSlider, twigCountSlider, leafCountSlider
    
    win = QtWidgets.QWidget()
    win.resize(winWidth, winHeight)
    win.setWindowTitle("Branch Generator")
    win.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

    layout = QtWidgets.QVBoxLayout()
    win.setLayout(layout)
    
    # LOAO TEXTURE BUTTONS
    woodTextureBtn = QtWidgets.QPushButton("Load wood texture")
    leafTextureBtn = QtWidgets.QPushButton("Load leaf texture")
    
    layout.addWidget(woodTextureBtn)
    layout.addWidget(leafTextureBtn)
    
    woodTextureBtn.clicked.connect(loadWoodTexture)
    leafTextureBtn.clicked.connect(loadLeafTexture)

    # BRANCH SLIDERS
    branchHeightSlider = addSliderWithLabel(layout, "Branch Height", 1, 25, 15)
    subdivsHeightSlider = addSliderWithLabel(layout, "Branch Subdivisions", 1, 20, 10)
    
    # BRANCH BUTTON
    btn = QtWidgets.QPushButton("Generate branch")
    layout.addWidget(btn)
    btn.clicked.connect(createBranch) 
    
    # TWIG SLIDER
    twigCountSlider = addSliderWithLabel(layout, "Twig Count", 1, 30, 15)
    
    # TWIG BUTTON
    twigBtn = QtWidgets.QPushButton("Generate Twigs")
    layout.addWidget(twigBtn)
    twigBtn.clicked.connect(generateTwigs)
    
    # LEAF SLIDER
    leafCountSlider = addSliderWithLabel(layout, "Leaf Count", 1, 50, 20)
    
    # LEAF BUTTON
    twigBtn = QtWidgets.QPushButton("Generate leaves")
    layout.addWidget(twigBtn)
    twigBtn.clicked.connect(createLeaves)
    
    generateAllBtn = QtWidgets.QPushButton("Generate Entire Tree")
    layout.addWidget(generateAllBtn)
    generateAllBtn.clicked.connect(generateEntireTree)
    
    # CLEAR SCENE BUTTON
    clearBtn = QtWidgets.QPushButton("Clear Scene")
    layout.addWidget(clearBtn)
    clearBtn.clicked.connect(clearScene)

    win.show()

''' Separate function for adding sliders and labels '''
def addSliderWithLabel(layout, labelText, minValue, maxValue, defaultValue):
    label = QtWidgets.QLabel(labelText)
    slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
    slider.setMinimum(minValue)
    slider.setMaximum(maxValue)
    slider.setValue(defaultValue)
    
    # Create label to display slider value
    rangeLabel = QtWidgets.QLabel(f"Min:  {minValue}, Max: {maxValue}")
    
    layout.addWidget(label)
    layout.addWidget(slider)
    layout.addWidget(rangeLabel)
    return slider

createUI()