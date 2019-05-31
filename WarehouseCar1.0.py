#Import all necessary libraries
import time, gopigo3, easysensors, cv2, socket, json, requests
import easygopigo3 as easy
import numpy as np
import matplotlib.pyplot as plt
import pyzbar.pyzbar as pyzbar
import random as r
import numpy as np
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
from requests_oauthlib import OAuth1

#Define client server info
IP_address = '10.245.159.131' 
PORT_num = 2460 
BUFFER = 1024

def sendData(msg):
    #This function connects to a server Pi, sends a message and waits for a reply
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP_address, PORT_num))
    s.sendall(msg) 
    data = s.recv(BUFFER) 
    s.close() 
    return data

#GoPiGo Motor setup
gpg = gopigo3.GoPiGo3()
egpg = easy.EasyGoPiGo3()
gpg.reset_all()
motorL = gpg.MOTOR_LEFT
motorR = gpg.MOTOR_RIGHT

#Line Follower setup
LINE_PORT = gpg.GROVE_1
LINE_PIN = gpg.GROVE_1_1
gpg.set_grove_type(LINE_PORT, gpg.GROVE_TYPE.CUSTOM)
gpg.set_grove_mode(LINE_PORT, gpg.GROVE_INPUT_DIGITAL)
LINE    = 0
NO_LINE = 1
l_eye = gpg.LED_LEFT_EYE
r_eye = gpg.LED_RIGHT_EYE

#Ultrasonic Sensor setup
US_PORT = gpg.GROVE_2
US_TYPE = gpg.GROVE_TYPE.US
gpg.set_grove_type(US_PORT, US_TYPE)

def stopinmid():
    #This function orients the car to the middle of whatever room it's currently in
    distance = 255
    while distance >= 220:
        try:
            distance = gpg.get_grove_value(US_PORT)
        except gopigo3.SensorError:
            pass
        except gopigo3.ValueError:
            pass
        if gpg.get_grove_state(LINE_PIN) == LINE:
            gpg.set_motor_power(motorL, 50)
            gpg.set_motor_power(motorR, 75)
        if gpg.get_grove_state(LINE_PIN) == NO_LINE:
            gpg.set_motor_power(motorL, 75)
            gpg.set_motor_power(motorR, 50)  
    gpg.set_motor_power(motorL, 0)
    gpg.set_motor_power(motorR, 0)

def directionturn(start):
    #This function orients the car to a specific cardinal direction given starting direction
    if start == 'N' and turnto == 'E':
        start = turnto
        return 'right'
    if start == 'N' and turnto == 'W':
        start = turnto
        return 'left'
    if start == 'N' and turnto == 'S':
        start = turnto
        return 'around'
    if start == 'N' and turnto == 'N':
        start = turnto
        return 'straight'
    if start == 'E' and turnto == 'E':
        start = turnto
        return 'straight'
    if start == 'E' and turnto == 'W':
        start = turnto
        return 'around'
    if start == 'E' and turnto == 'S':
        start = turnto
        return 'right'
    if start == 'E' and turnto == 'N':
        start = turnto
        return 'left'
    if start == 'S' and turnto == 'E':
        start = turnto
        return 'left'
    if start == 'S' and turnto == 'W':
        start = turnto
        return 'right'
    if start == 'S' and turnto == 'S':
        start = turnto
        return 'straight'
    if start == 'S' and turnto == 'N':
        start = turnto
        return 'around'
    if start == 'W' and turnto == 'E':
        start = turnto
        return 'around'
    if start == 'W' and turnto == 'W':
        start = turnto
        return 'straight'
    if start == 'W' and turnto == 'S':
        start = turnto
        return 'left'
    if start == 'W' and turnto == 'N':
        start = turnto
        return 'right'
    
#Defines turning directions as angles    
right = -45
left = 45
straight = 0
around = 150

def spinline(amount):
    #This function rotates the car a given amount of degrees. Positive angles are counterclockwise.
    motor_degrees = (amount*320)//180
    start = gpg.get_motor_encoder(gpg.MOTOR_RIGHT)
    if amount > 0:
        while True:
            gpg.set_motor_power(motorL, -50)
            gpg.set_motor_power(motorR, 50)
            end = gpg.get_motor_encoder(gpg.MOTOR_RIGHT)
            if end-start == motor_degrees:
                gpg.set_motor_power(motorL, 0)
                gpg.set_motor_power(motorR, 0)
                break
        while True:
            if gpg.get_grove_state(LINE_PIN) == NO_LINE:
                gpg.set_motor_power(motorL, 0)
                gpg.set_motor_power(motorR, 0)
                break
            if gpg.get_grove_state(LINE_PIN) == LINE:
                gpg.set_motor_power(motorL, -50)
                gpg.set_motor_power(motorR, 50)
    elif amount < 0:
        while True:
            gpg.set_motor_power(motorL, 50)
            gpg.set_motor_power(motorR, -50)
            end = gpg.get_motor_encoder(gpg.MOTOR_RIGHT)
            if end-start == motor_degrees:
                gpg.set_motor_power(motorL, 0)
                gpg.set_motor_power(motorR, 0)
                break
        while True:
            if gpg.get_grove_state(LINE_PIN) == NO_LINE:
                gpg.set_motor_power(motorL, 0)
                gpg.set_motor_power(motorR, 0)
                break
            if gpg.get_grove_state(LINE_PIN) == LINE:
                gpg.set_motor_power(motorL, 50)
                gpg.set_motor_power(motorR, -50)
    elif amount == 0:
        while True:
            gpg.set_motor_power(motorL, 0)
            gpg.set_motor_power(motorR, 0)
            break
            
def turn():
    #This function turns the car depending onw what direction is returned from directionturn() function.
    if direction == 'right':
        spinline(right)
    elif direction == 'left':
        spinline(left)
    elif direction == 'straight':
        spinline(straight)
    elif direction == 'around':
        spinline(around)
        
def throughdoor():
    #This function moves car forward through the door it's currently facing
    distance = 245
    while distance <= 280:#280:
        try:
            distance = gpg.get_grove_value(US_PORT)
        except gopigo3.SensorError:
            pass
        except gopigo3.ValueError:
            pass
        if gpg.get_grove_state(LINE_PIN) == LINE:
            gpg.set_motor_power(motorL, 50)
            gpg.set_motor_power(motorR, 75)
        if gpg.get_grove_state(LINE_PIN) == NO_LINE:
            gpg.set_motor_power(motorL, 75)
            gpg.set_motor_power(motorR, 50)
    gpg.set_motor_power(motorL, 0)
    gpg.set_motor_power(motorR, 0)
    
def capture_image():
    #This functionm opens the camera and captures an image
    cam = cv2.VideoCapture(0)
    _,img = cam.read()
    cam.release()
    return img

def convertToRGB(img):
    #This function converts camera image to RGB
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

def decode_barcode(img):
    #This function scans for any barcodes in the and returns its data as barcodeobj
    barcodeobj = pyzbar.decode(img) 
    return barcodeobj

def decode_barcode_data(barcode_obj):
    #This function decodes barcode object and returns the data as a string
    for obj in barcode_obj:
        type = obj.type
        mystring = obj.data
        mystring = mystring.decode("utf-8")
        return mystring

def scan_barcode(img):
    #This function uses the two previous functions to return all relevant data
    barcode_obj = decode_barcode(img)
    barcode_string = decode_barcode_data(barcode_obj)
    print('barcode string: ' + str(barcode_string))
    room_number = barcode_string[:2]
    cardinal_direction = barcode_string[2]
    img = convertToRGB(img)
    data = str(room_number) + str(cardinal_direction)
    return data

def crop(img):
    #This function crops the camera image wherever it sees a green box
    min_x = 700
    min_y = 700
    max_x = -1
    max_y = -1
    minx = True
    miny = True
    maxx = True
    maxy = True
    for i in range (480):
        for j in range (640):
            if img[i,j,1] > min_green and img[i,j,0] < max_blue and img[i,j,2] < max_red:
                if i < min_y:
                    min_y = i
                if i > max_y: 
                    max_y = i
                if j > max_x:
                    max_x = j
                if j < min_x:
                    min_x = j
    if min_x > 640: 
        minx = False 
        max_x = 639 
    if min_y > 480:
        miny = False
        max_y = 479
    if max_x < 0: 
        maxx = False
        min_x = 1
    if max_y < 0:
        maxy = False
        min_y = 1
    cv2.rectangle(img, (min_x,min_y), (max_x,max_y), (255,0,0), 5)
    img2 = img[min_y:max_y, min_x:max_x] 
    if not minx and miny and maxx and maxy:
        plt.figure()
        plt.imshow(img)
        plt.show()
        return False
    else: 
        plt.figure()
        plt.imshow(img)
        plt.show()
        return img2

def check_green(img):
    #This function checks to see if there is any green in a camera image
    count = 0
    for i in range (480):
        for j in range (640):
            if img[i,j,1] > min_green and img[i,j,0] < max_blue and img[i,j,2] < max_red:
                count +=1
    if count > 5:
        return True
    else: 
        return False
    
def getKey(filename):
    #This function returns the AzureFile key needed for posting to Twitter
    fin = open(filename)
    for line in fin:
        key = line.strip()
    return key

def getTwitterKeys(filename):
    #This function returns the Twitter API key from local file
    fin = open(filename)
    consumer_key = fin.readline().strip() # read line 1
    consumer_secret = fin.readline().strip() # read line 2
    access_token = fin.readline().strip() # read line 3
    access_secret = fin.readline().strip() # read line 4
    fin.close()
    return consumer_key, consumer_secret, access_token, access_secret

#Twitter API setup
apikeyfile = 'TwitterKey.txt' 
consumer_key, consumer_secret, access_token, access_secret = getTwitterKeys(apikeyfile)
twitter_auth = OAuth1(consumer_key, client_secret=consumer_secret,
                      resource_owner_key=access_token, resource_owner_secret=access_secret)
image_path = "startroom.png"
media_base_url = 'https://upload.twitter.com/'
media_post_url = '{}1.1/media/upload.json'.format(media_base_url)
image_data = open(image_path, "rb").read() #read byte data of image
files = {'media': image_data}
response = requests.post(media_post_url, files=files, auth=twitter_auth)
media_id = json.loads(response.text)['media_id']
base_url = 'https://api.twitter.com/'
post_url = '{}1.1/statuses/update.json'.format(base_url)
message = '@TuftsES2Bot Team Emerald starting in room ' + str(starting_room) + '!'
post = {"status": message, "media_ids": media_id} 
response = requests.post(post_url, data=post, auth=twitter_auth)


#Start of warehouse run 
stopinmid() 
print('capturing image')
img = capture_image()
barcode_data = scan_barcode(img)
filename = 'startroom.png'
cv2.imwrite(filename, img)
start_direction = barcode_data[2] #get starting direction from barcode image
print('Start direction: ' + str(start_direction))
starting_room = str(barcode_data[0:2]) #formats the barcode data into usable string
print('Starting room: ' + str(starting_room))
print('Sending starting room to Server')
path = sendData(starting_room.encode("utf-8")).decode("utf-8") 
print('Server response: path to product is ' + str(path))

if path == 'P':
    print('Product already in room')
    turnto = 'S'
    direction = directionturn(start_direction)
    turn()
else:
    for i in range(1):
        for letter in path:
            stopinmid() #stops in middle of room
            turnto = letter
            direction = directionturn(start_direction)  #translates cardinal direction to left/right
            turn() #turns given direction
            throughdoor() 
            stopinmid()
            start_direction = letter#goes through door
        turnto = 'S'
        direction = directionturn(start_direction)
        turn()    
min_green = 100
max_red = 75
max_blue = 75
img_0 = capture_image()
img = convertToRGB(img_0)
print('Cropping image...')
img2 = crop(img)
plt.figure()
plt.imshow(img2)
plt.show()
filename = 'testimage.png'
cv2.imwrite(filename, img2)
print('Tweeting @Tufts ES2')
Azurekeyfile = 'AzureKey.txt'
subscription_key = getKey(Azurekeyfile)
vision_base_url = "https://eastus2.api.cognitive.microsoft.com/vision/v2.0/"
analyze_url = vision_base_url + "analyze"
image_path = "testimage.png"
image_data = open(image_path, "rb").read()
headers    = {'Ocp-Apim-Subscription-Key': subscription_key,
              'Content-Type': 'application/octet-stream'}
params     = {'visualFeatures': 'Categories,Description,Color'}
response = requests.post(analyze_url, headers=headers, params=params, data=image_data)
metadata = json.loads(response.text) #dictionary 
print(metadata.get('description').get('tags'))

apikeyfile = 'TwitterKey.txt'
consumer_key, consumer_secret, access_token, access_secret = getTwitterKeys(apikeyfile)
twitter_auth = OAuth1(consumer_key, client_secret=consumer_secret,
                      resource_owner_key=access_token, resource_owner_secret=access_secret)
image_path = "testimage.png"
media_base_url = 'https://upload.twitter.com/'
media_post_url = '{}1.1/media/upload.json'.format(media_base_url)
image_data = open(image_path, "rb").read() #read byte data of image
files = {'media': image_data}
response = requests.post(media_post_url, files=files, auth=twitter_auth)
media_id = json.loads(response.text)['media_id']
base_url = 'https://api.twitter.com/'
post_url = '{}1.1/statuses/update.json'.format(base_url)
message = '@TuftsES2Bot Team Emerald started in room ' + str(starting_room) + ' and found Product!'
post = {"status": message, "media_ids": media_id} # media_id from above!
response = requests.post(post_url, data=post, auth=twitter_auth)
