import time
from datetime import datetime,date
import serial
import RPi.GPIO as GPIO
import io
import time
import csv
import pytz
import os
import sqlite3
from array import *
from flask import Flask, render_template, request, redirect, url_for, send_file, make_response
app = Flask(__name__)
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(11, GPIO.OUT, initial=GPIO.LOW)

ser = serial.Serial(
    port='/dev/serial0',
    baudrate = 9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=0
)

confirm = ''
terminate = ''
percent = 0
s = ''
j = 0
today = ''
time_now = ''
s1 = 'AUTO'
s2 = 'AUTO'
s3 = 'AUTO'
thread = 0
status = 0
over = False
# numSamples = 10
address_now = 2001
k = 0
modes = array('i',[20010,20020,20030])
percents = array('i',[0,0,0])
recur = False
graph_label = "SLAVE 1"
# conn = sqlite3.connect('../../bak/rubber.db')

# c = conn.cursor()


def getHistData ():
    global today
    global address_now
    conn = sqlite3.connect('../../bak/rubber.db')
    c = conn.cursor()

    c.execute("SELECT * FROM percent_humidity WHERE slave_id=? and date=? ORDER BY time DESC LIMIT 20",(address_now,today))
    data = c.fetchall()
    times = []
    percents = []
    for row in reversed(data):
        times.append(row[3])
        percents.append(row[4])
    return times, percents

@app.route('/plot/hum')
def plot_hum():
    global numSamples
    global address_now
    times, hums = getHistData()
    ys = hums
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_title(graph_label+" Soil Moisture [%]")
    axis.set_xlabel("Samples")
    axis.grid(True)
    # xs = range(numSamples)
    xs = range(times)
    axis.set_xticklabels(xs, rotation=45)
    axis.plot(xs, ys)
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

@app.route("/")
def hello():
    # global conn
    # global c
    # conn = sqlite3.connect('../../bak/rubber.db')
    # c = conn.cursor()
    global s1
    global s2
    global s3
    global percents
    global j
    global thread
    global over
    global k
    global recur
    k = j
    if(thread!=0):
        while recur:
            print("aaaaaaaaaaaaaaaaa")
        time.sleep(3)
        k = j
        # percents[k] = percent
        templateData = {
            'percent1': percents[0],
            'percent2': percents[1],
            'percent3': percents[2],
            'percent': percent,
            's1' : s1,
            's2' : s2,
            's3' : s3
        }
        return render_template('index.html', **templateData)
    
    # if not over:
    transceive()
    # templateData = {
    #     'percent1': percents[0],
    #     'percent2': percents[1],
    #     'percent3': percents[2],
    #     'percent': percent,
    #     's1' : s1,
    #     's2' : s2,
    #     's3' : s3
    # }
    # if over:
    #     over = False
    #     return 'a'
    print(thread)
    if(thread==0):
        print(str(modes[j])+' '+str(percent))
        # k = j
        percents[k] = percent
        over = False
        # return render_template('index.html', **templateData)
        # times, percents = getHistData()
        # plot_hum()

    now = datetime.now()
    timeString = now.strftime("%Y-%m-%d %H:%M")
    templateData = {
        'percent1': percents[0],
        'percent2': percents[1],
        'percent3': percents[2],
        'percent': percent,
        's1' : s1,
        's2' : s2,
        's3' : s3
    }
    recur = False
    return render_template('index.html', **templateData)
    # , redirect(url_for('hello'), code=302)
#    transceive()

@app.route("/<deviceName>/<action>")
def action(deviceName, action):
    global s1
    global s2
    global s3
    global j
    global percents
    global status
    # k = j
    b = int(deviceName)
    modes[b] = int(str(int(modes[b]/10)*10+int(action)))
    status = int(action)
    if b==0:
        if status==0:
            s1 = 'AUTO'
        elif status==1:
            s1 = 'ON'
        elif status==2:
            s1 = 'OFF'
    elif b==1:
        if status==0:
            s2 = 'AUTO'
        elif status==1:
            s2 = 'ON'
        elif status==2:
            s2 = 'OFF'
    elif b==2:
        if status==0:
            s3 = 'AUTO'
        elif status==1:
            s3 = 'ON'
        elif status==2:
            s3 = 'OFF'

    # transceive()
    # percents[k] = percent
    templateData = {
        'percent1': percents[0],
        'percent2': percents[1],
        'percent3': percents[2],
        's1' : s1,
        's2' : s2,
        's3' : s3
    }
    return render_template('index.html', **templateData)
    # render_template('index.html', **templateData)
    # redirect(url_for('hello'), code=302)

@app.route("/plot/<slave>")
def plot_slave(slave):
    global address_now
    global graph_label
    address_now = int(slave)
    if address_now == 2001:
        graph_label = "SLAVE 1"
    elif address_now == 2002:
        graph_label = "SLAVE 2"
    elif address_now == 2003:
        graph_label = "SLAVE 3"
    return redirect(url_for('hello'), code=302)

def changeIndex():
    global modes
    global j
    if j<2:
        j = j + 1
        print(modes[j])
    else:
        j = 0
        print(modes[j])

def changeTime():
    global time_now
    global today
    today = str(date.today())
    tz_BKK = pytz.timezone('Asia/Bangkok')
    datetime_BKK = datetime.now(tz_BKK)
    time_now = datetime_BKK.strftime("%H:%M:%S")
    time_split = time_now.split(":")

def transceive():
    global confirm
    global percent
    global percents
    global terminate
    global s
    global j
    global today
    global time_now
    global modes
    global conn
    global c
    global thread
    global recur
    # global over

    thread = thread + 1
    # conn = sqlite3.connect('../../bak/rubber.db')
    # c = conn.cursor()
    # start = time.time()
    if(thread>1):
        thread = thread - 1
        # over = True
        recur = True
        return
    time.sleep(3)
    while(confirm!='1'.strip() or terminate!='2'.strip()):
        # if(time.time()-start>20):
        #     return
        # if(thread>1):
        #     thread = thread - 1
        #     return
        time.sleep(0.1)
        GPIO.output(7, GPIO.HIGH)
        now = time.time()
        while(time.time()-now<1):
            ser.write(str.encode(str(modes[j]).strip()))
            print(str(modes[j]).strip())
            time.sleep(1.5)
            ser.flush()
        GPIO.output(7, GPIO.LOW)
        now = time.time()
        while(time.time()-now<1):
            try:
                s = ser.readline().decode('ascii').strip()
                keep = s.split(',')
                confirm = keep[0]
                percent = int(keep[1])
                terminate = keep[2]
            except:
                print('no data')

            time.sleep(0.5)

        print(s+'\n')
        ser.flushInput()

    now = datetime.now()
    GPIO.output(7, GPIO.HIGH)
    now = time.time()
    while(time.time()-now<1.5):
        ser.write(str.encode(("9").strip()))
        time.sleep(1)

    confirm = '0'
    terminate = '0'
    address = str(modes[j])[0:4].strip()
    mode = str(modes[j])[4].strip()
    # if j==0:
    #     percent=7
    # elif j==1:
    #     percent=18
    changeTime()
    print(today+' '+time_now)
    print('\n')
    
    try:
        connl = sqlite3.connect('../../bak/rubber.db')
        cl = connl.cursor()
        with connl:
            cl.execute("INSERT INTO percent_humidity VALUES (:slave_id, :slave_mode, :date, :time, :percent)", {'slave_id': address, 'slave_mode': mode, 'date': today, 'time': time_now, 'percent': percent})

        connl.commit()
        changeIndex()
        thread = 0
        # over = True
    except:
        print('database error')
        thread = 0
        return


# def main():
    # while True:
        # transceive()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
    # main()
