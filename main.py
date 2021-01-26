#Libraries
##########################################################################################
import tkinter as tk
from tkinter import *
from tkinter import ttk
from threading import Thread 

import sys
import serial
import serial.tools.list_ports
from serial import *
from serial import Serial

from tkinter import Scale, Tk, Frame, Label, Button
from tkinter.ttk import Notebook,Entry

from playsound import playsound

#Root window
##########################################################################################
root = Tk()
root.title("Drone Time Attack")
root.geometry("900x500")
#root.resizable(0, 0)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

style = ttk.Style()
style.configure("Main.TLabel", font="Signboard")
style.theme_use('vista')

#Main Frame
##########################################################################################
mainframe = ttk.Frame(root, padding="10 10 10 10")
mainframe.grid(column=0, row=0, sticky=(W, N, N, N))

statisticsHeadingLabel = ttk.Label(mainframe, text="Statistics")
statisticsHeadingLabel.grid(column=1, row=1, columnspan=2, sticky=N)
statisticsHeadingLabel['font'] = "TkHeadingFont:"

timeLabel = ttk.Label(mainframe, text="Time:", style="Main.TLabel")
timeLabel.grid(column=1, row=2, sticky=N)
timeValue = ttk.Label(mainframe, text="00:00:00")
timeValue.grid(column=2, row=2, sticky=N)

#Serial
##########################################################################################
serialThreadBoolean = False
line = "0"
state = False

def playBruh():
	playsound('bruh.mp3', False)

def playDing():
	playsound('ding.mp3', False)

def serialInit():
	global serialPort
	serialPort = serial.Serial()
	serialPort.baudrate = 9600
	serialPort.port = COMPortCombobox.get()
	serialPort.open()
	main()

def serialClose():
	serialPort.close()

def main():
	if serialThreadBoolean:
		global line
		global currentColumn
		global state
		global isConnected
		global isStarted
		global timer
		global resetTimer
	#Input from receiver
		bLine = serialPort.readline()
		line = str(bLine)
		line = line[2:len(line)-5]

		if line != "":
	#Ready
			if line == "connected":
				playDing()
				isConnected = True
				startButton.configure(text="Ready")
	#Liftoff		 	
			elif line == "0":
				playBruh()
				state = True
				isStarted = True
				startButton.configure(text="Running")
				timeStringToTimesArray()
	#Passing trough gate
			else:
				playBruh()
				timeStringToTimesArray()
				if int(line) == int(gateNumberComboBox.get()):
					timeStringToLaptimesArray()
			if state:
				generateTable()

	#Last colummn and row generate best times
			if currentColumn >= int(lapNumberComboBox.get()):
				if int(line) == int(gateNumberComboBox.get()):
					bestCurrentLap()
					bestOverallLap()
					bestOverallTime()
					stopSerialThread()
					serialClose()
					startButton.configure(text="Finished")
					finalMin = int(times[int(line)-1][currentColumn-1][0:2])
					finalSec = int(times[int(line)-1][currentColumn-1][3:5])
					finalMsc = int(times[int(line)-1][currentColumn-1][6:8])
					timer = [finalMin, finalSec, finalMsc]
					resetTimer = False
					resetData()

		time.sleep(.01)
		main()
	else:
		print("not refreshing from arduino")

def serialPorts():
	return [p.device for p in serial.tools.list_ports.comports()]

def startSerialThread():
	global serialThreadBoolean
	serialThreadBoolean = True
	serialThread = Thread(target=serialInit, daemon=True)
	serialThread.start()

def stopSerialThread():
	global serialThreadBoolean
	serialThreadBoolean = False
			

#Stopwatch
##########################################################################################
timer = [0, 0, 0]
global pattern
pattern = '{0:02d}:{1:02d}.{2:02d}'
isConnected = False
isStarted = False

def resetData():
	global isConnected
	isConnected = False
	global isStarted
	isStarted = False
	global startSecondsBuffer
	startSecondsBuffer = 0
	global startMinutesBuffer
	startMinutesBuffer = 0
	global currentColumn
	currentColumn = 0
	global state
	state = False
	global laptimes
	laptimes = ["00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00"]
	global times
	times = [["00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00"], ["00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00"], ["00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00"], ["00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00"], ["00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00"], ["00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00"], ["00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00"], ["00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00"]]
	if resetTimer:
		global timer
		timer = [0, 0, 0]

def updateStopwatchTimeText():
	if state and isStarted:
		timer[2] += 1

		if (timer[2] >= 100):
		    timer[2] = 0
		    timer[1] += 1
		if (timer[1] >= 60):
		    timer[0] += 1
		    timer[1] = 0

	else:
		pass

	global timeString
	timeString = pattern.format(timer[0], timer[1], timer[2])
	timeString = timeString
	timeValue.configure(text=timeString)

	root.after(10, updateStopwatchTimeText)

def startStopwatch():
	global state
	if not state and not (COMPortCombobox.get() == 'None' or COMPortCombobox.get() == ''):
		state = True
		startSerialThread()		

def resetStopwatch():
	global resetTimer
	resetTimer = True
	resetData()
	if serialThreadBoolean:
		stopSerialThread()
		serialClose()
	generateTable()
	startButton.configure(text="Start")

startButton = tk.Button(mainframe, text='Start', command=startStopwatch)
startButton.grid(row=4, column=1, columnspan=2)

resetButton = tk.Button(mainframe, text='Reset', command=resetStopwatch)
resetButton.grid(row=5, column=1, columnspan=2)

stopwatchThread = Thread(target=updateStopwatchTimeText, daemon=True)


for child in mainframe.winfo_children(): 
    child.grid_configure(padx=5, pady=3)

#Table Frame
##########################################################################################
global startSecondsBuffer
startSecondsBuffer = 0
global startMinutesBuffer
startMinutesBuffer = 0
global currentColumn
currentColumn = 0
global createTable
createTable = True
global times
times = [["00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00"], ["00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00"], ["00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00"], ["00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00"], ["00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00"], ["00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00"], ["00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00"], ["00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00","00:00.00"]]
global laptimes
laptimes = ["00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00", "00:00.00"]
global bestLap
bestLap = 9999999
global bestLapStr
bestLapStr = "NA"
global bestTimeStr
bestTimeStr = ["NA", "NA", "NA", "NA", "NA"]


def tableFrameInit():
	global tableframe
	tableframe = ttk.Frame(root, padding="10 10 10 10")
	tableframe.grid(column=0, row=0, sticky=(S, N, N, N))

def timeStringToTimesArray():
	global times
	times[int(line)-1][currentColumn] = timeString

def timeStringToLaptimesArray():
	global timeString
	global currentColumn
	global startSecondsBuffer
	global startMinutesBuffer

	minutes = int(timeString[0:2]) - startMinutesBuffer
	secondsAndMilisecond = str(float(timeString[3:8]) - startSecondsBuffer).split('.')
	if len(secondsAndMilisecond[1]) == 1:
		secondsAndMilisecond[1] += "0"
	elif len(secondsAndMilisecond[1]) > 2:
		secondsAndMilisecond[1] = secondsAndMilisecond[1][0:2]
	laptimes[currentColumn] = pattern.format(minutes, int(secondsAndMilisecond[0]), int(secondsAndMilisecond[1]))
	startSecondsBuffer = float(timeString[3:8])
	startMinutesBuffer = int(timeString[0:2])
	currentColumn += 1

def bestCurrentLap():
	global bestLap
	bestLapThisRace = 99999999
	bestLapIndex = 0

	for r in range(currentColumn):
		currentMinutes = int(laptimes[r][0:2]) * 60
		currentSeconds = float(laptimes[r][3:8])
		currentBestLap = currentMinutes + currentSeconds
		if currentBestLap <= bestLapThisRace:
			bestLapThisRace = currentBestLap
			bestLapIndex = r

	currentBestLapStr = laptimes[bestLapIndex]

def bestOverallLap():
	global bestLap
	global bestLapStr

	for r in range(currentColumn):
		currentMinutes = int(laptimes[r][0:2]) * 60
		currentSeconds = float(laptimes[r][3:8])
		currentBestLap = currentMinutes + currentSeconds
		if currentBestLap <= bestLap:
			bestLap = currentBestLap
			bestLapStr = laptimes[r]

def bestOverallTime():
	global bestTimeStr
	global lapNuberEnum

	lapNuberEnum = 0
	if int(lapNumberComboBox.get()) == 1:
		lapNuberEnum = 0
	if int(lapNumberComboBox.get()) == 3:
		lapNuberEnum = 1
	if int(lapNumberComboBox.get()) == 5:
		lapNuberEnum = 2
	if int(lapNumberComboBox.get()) == 7:
		lapNuberEnum = 3
	if int(lapNumberComboBox.get()) == 10:
		lapNuberEnum = 4

	for x in range(8):
		if times[int(line)-1][currentColumn-1][x] != bestTimeStr[lapNuberEnum][x]:
			if times[int(line)-1][currentColumn-1][x] < bestTimeStr[lapNuberEnum][x]:
				bestTimeStr[lapNuberEnum] = times[int(line)-1][currentColumn-1]
			break

def highscoreNameWindow():
	global nameWindow
	nameWindow = tk.Toplevel()
	global userName
	userName = tk.StringVar(nameWindow)

	title = tk.Label(nameWindow, text="New Highscore!")
	title.grid(row=0, column=0)

	name = tk.Label(nameWindow, text="Please write your name")
	name.grid(row=1, column=0)

	nameEntry = tk.Entry(nameWindow, textvariable=userName)
	nameEntry.grid(row=2, column=0)

	submitButton = tk.Button(nameWindow, text="Submit and close", command=usernameToHighscore)
	submitButton.grid(row=3, column=0)

def usernameToHighscore():
	print(userName.get())
	nameWindow.destroy()

def highscoreWindow():
	hsWindow = tk.Toplevel()

	blLabel = tk.Label(hsWindow, text="Best lap: " + bestLapStr, relief=RIDGE)
	blLabel.grid(row=0, column=0)

	cnt = 1
	for x in range(5):
		if cnt == 1:	
			btLabel = tk.Label(hsWindow, text="Best time for " + str(cnt) + " lap: " + bestTimeStr[x], relief=RIDGE)
			btLabel.grid(row=x+1, column=0)
		else:
			btLabel = tk.Label(hsWindow, text="Best time for " + str(cnt) + " laps: " + bestTimeStr[x], relief=RIDGE)
			btLabel.grid(row=x+1, column=0)
		
		if cnt == 7:
			cnt += 3
		else:
			cnt += 2

	closeButton = tk.Button(hsWindow, text="Close", command=hsWindow.destroy, relief=RIDGE)
	closeButton.grid(row=x+2, column=0)

#Todo
##########################################################################################

def generateTable():
	global tableframe
	global createTable

	if createTable:
		createTable = False
	else:
		tableframe.destroy()
	
	tableFrameInit()

	for i in range(int(gateNumberComboBox.get())+1):
		for j in range(int(lapNumberComboBox.get())):
			if i == 0:
				l = Label(tableframe, text="Lap "+ str(j+1), relief=RIDGE)
				l.grid(row=i, column=j, sticky=NSEW)	
			else:
				l = Label(tableframe, text=times[i-1][j], relief=RIDGE)
				l.grid(row=i+2, column=j, sticky=NSEW)


	for z in range(int(lapNumberComboBox.get())):
		t = Label(tableframe, text=laptimes[z], relief=RIDGE)
		t.grid(row=int(gateNumberComboBox.get())+3, column=z, sticky=NSEW)

#Settings Frame
##########################################################################################
def selectionClear(*args):
	root.focus()

settingsframe = ttk.Frame(root, padding="10 10 10 10")
settingsframe.grid(column=0, row=0, sticky=(E, N, N, N))

settingsHeadingLabel = ttk.Label(settingsframe, text="Settings")
settingsHeadingLabel.grid(column=1, row=1, columnspan =2, sticky=N)
settingsHeadingLabel['font'] = "TkHeadingFont:"

COMPortLabel = ttk.Label(settingsframe, text="COM port")
COMPortLabel.grid(column=1, row=2, sticky=N)

COMPortCombobox = ttk.Combobox(settingsframe, values=serialPorts())
COMPortCombobox.grid(column=2, row=2, sticky=N)
COMPortCombobox.set('None')
COMPortCombobox.state(["readonly"])
COMPortCombobox.bind('<<ComboboxSelected>>', selectionClear)


gateNumberLabel = ttk.Label(settingsframe, text="Number Of Gates")
gateNumberLabel.grid(column=1, row=3, sticky=N)

gateNumberVariable = StringVar()
gateNumberComboBox = ttk.Combobox(settingsframe, textvariable=gateNumberVariable)
gateNumberComboBox.grid(column=2, row=3, sticky=N)
gateNumberComboBox['values'] = ('2', '3', '4', '5', '6', '7', '8')
gateNumberComboBox.set('3')
gateNumberComboBox.state(["readonly"])
gateNumberComboBox.bind('<<ComboboxSelected>>', selectionClear)


lapNumberLabel = ttk.Label(settingsframe, text="Number Of Laps")
lapNumberLabel.grid(column=1, row=4, sticky=N)

lapNumberVariable = StringVar()
lapNumberComboBox = ttk.Combobox(settingsframe, textvariable=lapNumberVariable)
lapNumberComboBox.grid(column=2, row=4, sticky=N)
lapNumberComboBox['values'] = ('1', '3', '5', '7', '10')
lapNumberVariable.set('1')
lapNumberComboBox.state(["readonly"])
lapNumberComboBox.bind('<<ComboboxSelected>>', selectionClear)

genTableButton = tk.Button(settingsframe, text='Generate table', command=generateTable)
genTableButton.grid(row=5, column=1, columnspan=2)

newHighscoreButton = tk.Button(settingsframe, text='New highscore', command=highscoreNameWindow)
newHighscoreButton.grid(row=6, column=1, columnspan=2)

showHighscoresButton = tk.Button(settingsframe, text='Show highscore', command=highscoreWindow)
showHighscoresButton.grid(row=7, column=1, columnspan=2)

closeButton = tk.Button(settingsframe, text="Close", command=root.destroy, relief=RIDGE)
closeButton.grid(row=8, column=1, columnspan=2)

for child in settingsframe.winfo_children(): 
    child.grid_configure(padx=5, pady=3)

stopwatchThread.start()
root.mainloop() 
#serialThread.join()
#stopwatchThread.join()