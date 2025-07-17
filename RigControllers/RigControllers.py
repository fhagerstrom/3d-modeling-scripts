import pymel.core as pm
from PySide6 import QtWidgets, QtCore

# Global vars - UI
ctrlWindow = None
jointField = None
radiusSlider = None
prefixOption = None

def LoadSelectedJoint():
    selection = pm.ls(selection=True, type='joint')
    if selection:
        jointField.setText(selection[0].name())
      
''' Create a single controller at selected joint '''        
def CreateController():
    # Get joint name and apply chosen radius and prefix
    jointName = jointField.text()
    radius = radiusSlider.value()
    prefix = prefixOption.currentText()
    
    if not pm.objExists(jointName):
        pm.warning(f"Joint {jointName} does not exist")
        return
        
    joint = pm.PyNode(jointName)
    baseName = joint.nodeName().replace("joint", "ctrl")
    finalCtrlName = f"{prefix}{baseName}_CTRL" if prefix != "None" else f"{baseName}_CTRL"
    finalGrpName = finalCtrlName.replace("_CTRL", "_GRP")
    
    # Create controller
    ctrl = pm.circle(normal=(1, 0, 0), radius=radius, ch=False)[0]
    
    # Match pos and rotation
    ctrl.setMatrix(joint.getMatrix(worldSpace=True))
    
    # Rename controller and group depending on prefix chosen
    offsetGrp = pm.group(ctrl, name=finalGrpName)
    ctrl.rename(finalCtrlName)
    
     pm.orientConstraint(ctrl, joint, mo=True)
        
    print(f"Controller created for {jointName}")


''' Create multiple controllers in a chain for selected root joint '''    
def CreateControllerChain():
    # Get joint name and apply chosen radius and prefix
    jointName = jointField.text()
    radius = radiusSlider.value()
    prefix = prefixOption.currentText()
    
    if not pm.objExists(jointName):
        pm.warning(f"Joint {jointName} does not exist")
        return
    
    joint = pm.PyNode(jointName)
    
    # Include root joint and sort so the hierarchy is set correctly
    jointChain = sorted([joint] + joint.listRelatives(ad=True, type='joint'))
    
    previousCtrl = None
    
    for j in jointChain:
        baseName = j.nodeName().replace("joint", "ctrl")
        finalCtrlName = f"{prefix}{baseName}_CTRL" if prefix != "None" else f"{baseName}_CTRL"
        finalGrpName = finalCtrlName.replace("_CTRL", "_GRP")

        # Create controller
        ctrl = pm.circle(normal=(1, 0, 0), radius=radius, ch=False)[0]
        ctrl.setMatrix(j.getMatrix(worldSpace=True))
        ctrl.rename(finalCtrlName)

        # Create group for controller
        offsetGrp = pm.group(ctrl, name=finalGrpName)
        
        if previousCtrl:
            # Parent this group under the previous controller
            pm.parent(offsetGrp, previousCtrl)

        previousCtrl = ctrl
        
        pm.orientConstraint(ctrl, j, mo=True)
        

    print(f"Controller chain created starting from {jointName}")
    
    
def CreateWindow():
    global ctrlWindow
    global jointField
    global radiusSlider
    global prefixOption
    
    # Delete eventual existing window
    if ctrlWindow:
        ctrlWindow.close()
        ctrlWindow = None
        
    # Create window
    ctrlWindow = QtWidgets.QWidget()
    ctrlWindow.setWindowTitle("Rig Controller Creator")
    ctrlWindow.setFixedSize(480, 280) # SIZE HERE
    
    layout = QtWidgets.QVBoxLayout(ctrlWindow)
    
    # Joint name
    jointField = QtWidgets.QLineEdit()
    selectJointBtn = QtWidgets.QPushButton("Load Selected Joint")
    selectJointBtn.clicked.connect(LoadSelectedJoint)
    
    # Radius slider
    radiusSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
    radiusSlider.setMinimum(1)
    radiusSlider.setMaximum(20)
    radiusSlider.setValue(5)
    
    # Display radius value for clarification
    radiusLabel = QtWidgets.QLabel(f"Radius: {radiusSlider.value()}")
    radiusSlider.valueChanged.connect(lambda: radiusLabel.setText(f"{radiusSlider.value()}"))
    
    # Make sure radius slider shows on window load
    radiusLabel.setText(f"{radiusSlider.value()}")
    
    # Add widgets to layout
    layout.addWidget(QtWidgets.QLabel("Joint Name (select in outliner, or write name manually)"))
    layout.addWidget(jointField)
    layout.addWidget(selectJointBtn)
    
    layout.addWidget(QtWidgets.QLabel("Controller Radius"))
    layout.addWidget(radiusSlider)
    layout.addWidget(radiusLabel)
    
    # Prefix options
    layout.addWidget(QtWidgets.QLabel("Prefix"))
    prefixOption = QtWidgets.QComboBox()
    prefixOption.addItems(["None", "L_", "R_"])
    layout.addWidget(prefixOption)
    
    # Create button
    createBtn = QtWidgets.QPushButton("Create Controller")
    createBtn.clicked.connect(CreateController)
    layout.addWidget(createBtn)
    
    # Create chain button
    createChainBtn = QtWidgets.QPushButton("Create controllers on chain")
    createChainBtn.clicked.connect(CreateControllerChain)
    layout.addWidget(createChainBtn)
    
    ctrlWindow.show()
    
# Open window
CreateWindow()