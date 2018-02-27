# -*- coding: utf-8 -*-
"""
@author: Alex Seitz, Alex Lang
"""
from PyQt4 import QtGui, QtCore, uic, Qwt5
import sys
import random
from time import strftime
import time
QUADR = "²".decode('utf8')

''' --Program Variables-- '''
states = 8
active = 60
div = 10
basic = 2
field = 40
table = {}
hasStarted = False
frames_done = 0
stats = {}

''' --UI Initialization-- '''
app = QtGui.QApplication(sys.argv)
myWindow =QtGui.QMainWindow()
uic.loadUi('interface_1_1.ui', myWindow)

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

def drawPlot():
    myWindow.qwtPlot.setAxisScale(Qwt5.QwtPlot.yLeft, 0, field * field)
    myWindow.qwtPlot.setAxisScale(Qwt5.QwtPlot.xBottom, frames_done-20, frames_done)
    myWindow.qwtPlot.enableAxis(0, False)
    myWindow.qwtPlot.clear()
    i = 0
    
    while  i <= states:
        points = QtGui.QPolygonF()
        j = 0
        while j < frames_done:
            points.append(QtCore.QPoint(j, stats[j,i]))
            j += 1       
        curve = Qwt5.QwtPlotCurve()
        curve.setData(points)
        curve.setPen(getColor(i))
        if i == states:
            curve.setPen(QtGui.QColor(0,0,255))   
        curve.attach(myWindow.qwtPlot)
        i += 1
        
    #Gesamtkurve für alle Infektionszustände
    points = QtGui.QPolygonF()
    j = 0
    while j < frames_done:
        sum = 0
        k = 1
        while k < states:
            sum += stats[j,k]
            k += 1
        points.append(QtCore.QPoint(j, sum))
        j += 1
    curve = Qwt5.QwtPlotCurve()
    curve.setData(points)
    curve.setPen(QtGui.QColor(180,0,190))
    curve.attach(myWindow.qwtPlot)
    
    
    myWindow.qwtPlot.replot()
drawPlot()


def happens(probability, size):
    n = random.randint(0,size)
    if n <= probability:
        return True
    else:
        return False

def updateStats(n):
    s = 0
    while s <= states:
        stats[n,s] = 0
        s += 1
    i = 0
    while i < field:
        j = 0
        while j < field:
            stats[n,table[i,j]] += 1
            j += 1
        i += 1

def getStatsforLog(n):
    statsForLog = "[ |"
    s = 0
    while s <= states:
        statsForLog = statsForLog + str(s) + ":" + str(stats[n,s]) + " | "
        s += 1
    statsForLog += "]"
    return statsForLog

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
    updateStats(n)
    drawPlot()
    log("Frame " + str(n+1) +  ": " + "\n" + getStatsforLog(n))



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
    drawPlot()
myWindow.slField.valueChanged.connect(fieldSizeChanged)

def framesChanged():
    drawPlot()
myWindow.leFrames.textChanged.connect(framesChanged)
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
        time.sleep(0.1)
        
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
    myWindow.qwtPlot.setAxisScale(Qwt5.QwtPlot.yLeft, 0, field * field)
    myWindow.qwtPlot.setAxisScale(Qwt5.QwtPlot.xBottom, frames_done-20, frames_done)
    myWindow.qwtPlot.clear()
    myWindow.qwtPlot.replot()
    
    
myWindow.bStart.clicked.connect(startPressed)
myWindow.bReset.clicked.connect(resetPressed)
myWindow.bNext.clicked.connect(nextPressed)
''' --Launch Phrase-- '''
myWindow.show()
sys.exit(app.exec_())

