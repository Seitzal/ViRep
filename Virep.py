# -*- coding: utf-8 -*-
"""
@author: Alex Seitz, Alex Lang
"""
from PyQt4 import QtGui, QtCore, uic
import sys
import random
from time import strftime
import time
QUADR = "sq"

''' --Program Variables-- '''
states = 8
active = 60
div = 10
basic = 2
field = 40
table = {}
hasStarted = False
frames_done = 0

''' --UI Initialization-- '''

app = QtGui.QApplication(sys.argv)
myWindow =QtGui.QMainWindow()
uic.loadUi('interface.ui', myWindow)

def happens(probability, size):
    n = random.randint(0,size)
    if n <= probability:
        return True
    else:
        return False


def log(text):
    print(text)
    time = strftime("[%H:%M:%S] ")
    myWindow.pteLog.appendPlainText(time + text)

''' --Initial generation-- '''
def init():
    i = 0
    while i < field:
        j = 0
        while j < field:
            isCell = random.randint(0,1)
            if isCell == 1:
                table[i,j] = states
            if isCell == 0:
                table [i,j] = 0
            j = j + 1
        i = i + 1
  
''' --Generation of each frame-- '''  
def nextframe(n):
    global states, active, div, basic, field, table, hasStarted
    i = 0
    while i < field:
        j = 0
        while j < field:
            
            #Initial Infection chance for healthy cells
            if table[i,j] == states:
                spontaneous = happens(basic, 100000)
                if spontaneous:
                    table[i,j] = states -1
                    
            #Division chance for healthy cells
            if table[i,j] == states:
                    #try all neighbor cells. if they are empty, add them to a list of candidates
                    candidates = []
                    if i > 0:
                        if table[i-1, j] == 0:
                            candidates.append([i-1,j])
                    if j > 0:
                        if table[i, j-1] == 0:
                            candidates.append([i,j-1])
                    if i > 0 and j > 0:
                        if table[i-1, j-1] == 0:
                            candidates.append([i-1,j-1])
                    if i < field - 2:
                        if table[i+1, j] == 0:
                            candidates.append([i+1,j])
                    if j < field - 2:
                        if table[i, j+1] == 0:
                            candidates.append([i,j+1])
                    if i < field - 2 and j < field - 1:
                        if table[i+1, j+1] == 0:
                            candidates.append([i+1,j+1])
                    if i < field - 2 and j > 0:
                        if table[i+1, j-1] == 0:
                            candidates.append([i+1,j-1])
                    if i > 0 and j < field - 2:
                        if table[i-1, j+1] == 0:
                            candidates.append([i-1,j+1])
                    

                    
                    #decide if cell will divide
                    if len(candidates) > 0 and happens(div, 100):
                        #Choose a random candidate location to be the location where the cell divides to
                        target = candidates[random.randint(0, len(candidates)-1)]
                        #Set the target location to be a new, healthy cell
                        table[target[0], target[1]] = states
                        
            #Degradation of infected cells
            if table[i,j] != states and table[i,j] > 0:
                newstate = table[i,j] - 1
                #Infection spreads if the cell dies
                if newstate == 0:
                    if i > 0:
                        if table[i-1, j] == states and happens(active, 100):
                            table[i-1,j] = states -1
                    if j > 0:
                        if table[i, j-1] == states and happens(active, 100):
                            table[i,j-1] = states -1 
                    if i > 0 and j > 0:
                        if table[i-1, j-1] == states and happens(active, 100):
                            table[i-1,j-1] = states -1
                    if i < field - 1:
                        if table[i+1, j] == states and happens(active, 100):
                            table[i+1,j] = states -1
                    if j < field - 1:
                        if table[i, j+1] == states and happens(active, 100):
                            table[i,j+1] = states -1
                    if i < field - 1 and j < field - 1:
                        if table[i+1, j+1] == states and happens(active, 100):
                            table[i+1,j+1] = states -1
                    if i < field - 2 and j > 0:
                        if table[i+1, j-1] == states and happens(active, 100):
                            table[i+1,j-1] = states -1
                    if i > 0 and j < field - 1:
                        if table[i-1, j+1] == states and happens(active, 100):
                            table[i-1,j+1] = states -1
                table[i,j] = newstate
                    
            j = j + 1
        i = i + 1
    log("Frame " + str(n+1) + " berechnet.")

''' --Color generation based on state-- '''
def getColor(state):
    if state == 0:
        return QtGui.QColor(0,0,0)
    if state == states:
        return QtGui.QColor(255,255,255)
    if state != states and state != 0 and myWindow.rbColors.isChecked():
        return QtGui.QColor(255-((255/states)*state),(255/states)*state, 0)
    if state != states and state != 0 and myWindow.rbGrey.isChecked():
        return QtGui.QColor((255/states)*state,(255/states)*state, (255/states)*state)



''' --Draw Cells, called every frame-- '''
def PaintFrame(event):
        if hasStarted:
            painter = QtGui.QPainter(myWindow.wCanvas) 
            x = 0
            while x < field:
                y = 0
                while y < field:
                    painter.setPen(getColor(table[x,y]))
                    painter.setBrush(getColor(table[x,y]))
                    painter.drawEllipse(QtCore.QPointF(x*14+7,y*14+7),6,6)
                    y=y+1
                x=x+1
    

''' --GUI Functionality, Input handling-- '''

#Slider functionality code
def statesChanged():
    global states
    states = myWindow.slStates.value()
    myWindow.lStates.setText(str(myWindow.slStates.value()))
myWindow.slStates.valueChanged.connect(statesChanged)

def activeRateChanged():
    global active
    active = myWindow.slActive.value()
    myWindow.lActive.setText(str(myWindow.slActive.value()) + "%")
myWindow.slActive.valueChanged.connect(activeRateChanged)

def divisionRateChanged():
    global div
    div = myWindow.slDiv.value()
    myWindow.lDiv.setText(str(myWindow.slDiv.value()) + "%")
myWindow.slDiv.valueChanged.connect(divisionRateChanged)

def fieldSizeChanged():
    global field
    field = myWindow.slField.value()
    myWindow.lField.setText(str(myWindow.slField.value()) + QUADR)
myWindow.slField.valueChanged.connect(fieldSizeChanged)
#Slider functionality code ends here

myWindow.wCanvas.paintEvent = PaintFrame

''' --Function for starting automatic generation-- '''
def startPressed():
    global hasStarted, basic, frames_done
    basic = int(myWindow.leBasic.text())
    log("Starte Simulation mit folgenden Einstellungen:")
    log("Zustaende:" + str(states))
    log("Aktive Infektionsrate:" + str(active) + "%")
    log("Teilungsrate:" + str(div) + "%")
    log("Basisinfektionsrate:" + str(basic) + "%")
    log("Feldgroesse: " + str(field) + "x" + str(field) + " Zellen")
    myWindow.gb1.setEnabled(False)
    myWindow.gb2.setEnabled(False)
    myWindow.bStart.setEnabled(False)
    init()
    hasStarted = True
    while frames_done < int(myWindow.leFrames.text()):
        nextframe(frames_done)
        myWindow.wCanvas.repaint()
        frames_done = frames_done + 1
        time.sleep(0.1)

''' --Function for manually generating frames-- '''        
def nextPressed():
    global hasStarted, frames_done
    if hasStarted:
        nextframe(frames_done)
        frames_done += 1
        myWindow.wCanvas.repaint()
    else:
        basic = int(myWindow.leBasic.text())
        log("Starte Simulation mit folgenden Einstellungen:")
        log("Zustaende:" + str(states))
        log("Aktive Infektionsrate:" + str(active) + "%")
        log("Teilungsrate:" + str(div) + "%")
        log("Basisinfektionsrate:" + str(basic) + "%")
        log("Feldgroesse: " + str(field) + "x" + str(field) + " Zellen")
        myWindow.gb1.setEnabled(False)
        myWindow.gb2.setEnabled(False)
        myWindow.bStart.setEnabled(False)
        init()
        hasStarted = True
        myWindow.wCanvas.repaint()
        
def resetPressed():
    global hasStarted, table, frames_done
    hasStarted = False
    frames_done = 0
    table = {}
    myWindow.gb1.setEnabled(True)
    myWindow.gb2.setEnabled(True)
    myWindow.bStart.setEnabled(True)
    myWindow.repaint()
    log("Simulation zurueckgesetzt.")
    
    
myWindow.bStart.clicked.connect(startPressed)
myWindow.bReset.clicked.connect(resetPressed)
myWindow.bNext.clicked.connect(nextPressed)
''' --Launch Phrase-- '''
myWindow.show()
sys.exit(app.exec_())

