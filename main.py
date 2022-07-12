#-------------------------------------------------------------------------------
#                                                                              #
# Project:           Lightpainting with neopixel strip and Rpi Pico            #
# Module:            lm_pico.py (main module)                                  #
# Author:            swen (Swen Hopfe, dj)                                     #
# Created:           21-09-16                                                  #
# Last updated:      21-10-17                                                  #
#                                                                              #
# This is a "Lightpainting" script, using RPi Pico, Micropython and a          #
# 120 pieces neopixel strip for all your creativity...                         #     
#                                                                              #
#-------------------------------------------------------------------------------

import array, time
from machine import Pin
import random
import rp2
from rp2 import PIO, StateMachine, asm_pio

#-------------------------------------------------------------------------------

# onboard LED
onboardLED = Pin(25, Pin.OUT)

# start button
start = Pin(14, Pin.IN, Pin.PULL_DOWN)

# number of WS2812b LEDs
LEDS = 120

# pio assembly to control gpios and transfer data
@asm_pio(sideset_init=PIO.OUT_LOW, out_shiftdir=PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)

# define the ws2812
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    label("bitloop")
    out(x, 1) .side(0) [T3 - 1]
    jmp(not_x, "do_zero") .side(1) [T1 - 1]
    jmp("bitloop") .side(1) [T2 - 1]
    label("do_zero")
    nop() .side(0) [T2 - 1]

# create state machine with ws2812, output is gpio(15)
stm = StateMachine(0, ws2812, freq=8000000, sideset_base=Pin(15))

# start the state machine
stm.active(1)

# create an array of RGB values
pix_array = array.array("I", [0 for _ in range(LEDS)])

# create a list of brightness values
bn_list = list([0.5 for _ in range(LEDS)])

#-------------------------------------------------------------------------------

# warning before start
def ws():
    for t in range(8):
        time.sleep(1)
        onboardLED.toggle()
    for t in range(8):
        time.sleep(0.1)
        onboardLED.toggle()
    time.sleep(2)

# set pixel color (all LEDs with new color col)
def pix_color_all(col):
    for i in range(len(pix_array)):
        pix_array[i] = (col[1]<<16) + (col[0]<<8) + col[2]

# pixel update (all LEDs with new global brightness bn, bn_list untouched)
def pix_update_all(bn): 
    new_array = array.array("I", [0 for _ in range(LEDS)])
    for i,c in enumerate(pix_array):
        r = int(((c >> 8) & 0xFF) * bn) 
        g = int(((c >> 16) & 0xFF) * bn) 
        b = int((c & 0xFF) * bn) 
        new_array[i] = (g<<16) + (r<<8) + b 
    stm.put(new_array, 8) 
    
# pixel update (all LEDs with brightness against bn_list)
def pix_update_all_bn(): 
    new_array = array.array("I", [0 for _ in range(LEDS)])
    for i,c in enumerate(pix_array):
        r = int(((c >> 8) & 0xFF) * bn_list[i]) 
        g = int(((c >> 16) & 0xFF) * bn_list[i]) 
        b = int((c & 0xFF) * bn_list[i]) 
        new_array[i] = (g<<16) + (r<<8) + b 
    stm.put(new_array, 8) 

# set pixel brightness (single LED, brightness stored in bn_list)
def pix_bn(p, bn):
    bn_list[p] = bn

# set pixel color (single LED p with new color col)
def pix_color(p, col):
    pix_array[p] = (col[1]<<16) + (col[0]<<8) + col[2]

# pixel update (single LED p with brightness against bn_list)
def pix_update(p): 
    new_array = pix_array
    c = pix_array[p]
    r = int(((c >> 8) & 0xFF) * bn_list[p]) 
    g = int(((c >> 16) & 0xFF) * bn_list[p]) 
    b = int((c & 0xFF) * bn_list[p]) 
    new_array[p] = (g<<16) + (r<<8) + b 
    stm.put(new_array, 8) 

#-------------------------------------------------------------------------------

# testscene 
def testscene(): 
   
   for i in range(40):
      pix_color(i, white)
      pix_bn(i, 0.6/(i+1))
   
   for i in range(40):
      pix_color(LEDS-i-1, white)
      pix_bn(LEDS-i-1, 0.6/(i+1))
   
   for i in range(40):
      pix_color(i+40, green)
      pix_bn(i+40, 0.01)

   for i in range(40):
      if i & 1 :
          pix_color(i+40, black)

   pix_update_all_bn()
   
   time.sleep(50)     

   pix_color_all(black)
   pix_update_all(0)

# scene 01 (white bars)
def scene01(): 
   
   for i in range(LEDS):
      if (i & 4) :       
         pix_color(i, white)
   pix_update_all(0.5)
   
   time.sleep(16)     

   pix_color_all(black)
   pix_update_all(0)

# scene 02 (orange blue and waves)
def scene02(): 

   pix_color_all(black)
   pix_update_all(0)
   
   for p in range(LEDS-6):
      pix_bn(p+3, 0.01)

   pix_bn(0, 0.5)
   pix_bn(1, 0.5)
   pix_bn(2, 0.5)
   pix_bn(LEDS-1, 0.5)
   pix_bn(LEDS-2, 0.5)
   pix_bn(LEDS-3, 0.5)

   pix_bn(54, 0.5)
   pix_bn(56, 0.4)
   pix_bn(57, 0.3)
   pix_bn(58, 0.2)
   pix_bn(59, 0.2)
   pix_bn(60, 0.2)
   pix_bn(61, 0.2)
   pix_bn(62, 0.3)
   pix_bn(63, 0.4)
   pix_bn(65, 0.5)
   
   pix_color(0, red)
   pix_color(1, orange)
   pix_color(2, yellow)
   pix_color(LEDS-1, red)
   pix_color(LEDS-2, orange)
   pix_color(LEDS-3, yellow)

   pix_color(54, green)
   pix_color(56, greenblue)
   pix_color(57, greenblue)
   pix_color(58, greenblue)
   pix_color(59, blue)
   pix_color(60, blue)
   pix_color(61, greenblue)
   pix_color(62, greenblue)
   pix_color(63, greenblue)
   pix_color(65, green)
   
   pix_update(0) 
   pix_update(1) 
   pix_update(2) 
   pix_update(LEDS-1) 
   pix_update(LEDS-2) 
   pix_update(LEDS-3) 

   pix_update(54) 
   pix_update(56) 
   pix_update(57) 
   pix_update(58) 
   pix_update(59) 
   pix_update(60) 
   pix_update(61) 
   pix_update(62) 
   pix_update(63) 
   pix_update(65) 
 
   csw = 1
 
   for gc in range(28):

      for i1 in range(51):
         if((i1+gc+3) % 7 == False):
            pix_color(i1+3, (120-(gc*4),120-(gc*4),120+(gc*4)))
            pix_bn(i1+3, 0.02)
      for i2 in range(51):
         if((i2+gc+3) % 7 == False):
            pix_color(LEDS-(i2+3+1), (120-(gc*4),120+(gc*4),120+(gc*4)))
            pix_bn(LEDS-(i2+3+1), 0.02)
  
      if(gc % 3 == False):
         csw = (-1 * csw)
         if (csw == -1):
            pix_bn(54, 0.5)
            pix_bn(56, 0.4)
            pix_bn(63, 0.4)
            pix_bn(65, 0.5)
         else:
            pix_bn(54, 0)
            pix_bn(56, 0)
            pix_bn(63, 0)
            pix_bn(65, 0)
  
      pix_update_all_bn()
      time.sleep(0.5)     

      for i1 in range(51):
         if((i1+gc+3) % 7 == False):
            pix_color(i1+3, black)
            pix_bn(i1+3, 0)
      for i2 in range(51):
         if((i2+gc+3) % 7 == False):
            pix_color(LEDS-(i2+3+1), black)
            pix_bn(LEDS-(i2+3+1), 0)
      
      pix_update_all_bn()
   
   pix_color_all(black)
   pix_update_all(0)
 
# scene 03 (zickzack)
def scene03():
   
  m1 = 0
  m2 = 0
  m3 = 0
  m4 = 0
  m5 = 0
  gc = 0
 
  while gc < 6 :
   w = 0
   while w < 20 :
      for i in range(LEDS):
         if i == (10 + w) :       
             pix_color(m1, black)
             pix_color(i, white)
             m1 = i
         if i == (30 + w) :
             pix_color(m2, black)
             pix_color(i, white)
             m2 = i
         if i == (50 + w) :
             pix_color(m3, black)
             pix_color(i, white)
             m3 = i
         if i == (70 + w) :
             pix_color(m4, black)
             pix_color(i, white)
             m4 = i
         if i == (90 + w) :
             pix_color(m5, black)
             pix_color(i, white)
             m5 = i
      pix_update_all(0.5)
      w = w + 1
      time.sleep(0.05)  

   w = w - 1
   while w > 0 :
      for i in range(LEDS):
         if i == (10 + w) :       
             pix_color(m1, black)
             pix_color(i, white)
             m1 = i
         if i == (30 + w) :
             pix_color(m2, black)
             pix_color(i, white)
             m2 = i
         if i == (50 + w) :
             pix_color(m3, black)
             pix_color(i, white)
             m3 = i
         if i == (70 + w) :
             pix_color(m4, black)
             pix_color(i, white)
             m4 = i
         if i == (90 + w) :
             pix_color(m5, black)
             pix_color(i, white)
             m5 = i
      pix_update_all(0.5)
      w = w - 1
      time.sleep(0.05)  

   gc = gc + 1
  
  pix_color_all(black)
  pix_update_all(0)

# scene 04 (turning, swiping)
def scene04(): 
   
   ii = 0
   for i in range(LEDS):
      ii = ii + 1
      if (ii == 20) :       
         pix_color(i, yellow)
      if (ii == 22) :       
         pix_color(i, green)
      if (ii == 24) :       
         pix_color(i, blue)
      if (ii == 26) :       
         pix_color(i, white)
      if (ii == 28) :       
         pix_color(i, white)
         ii = 0
   pix_update_all(0.5)

   time.sleep(1.6)     

   ii = 0
   for i in range(LEDS):
      ii = ii + 1
      if (ii == 20) :       
         pix_color(i, red)
      if (ii == 21) :       
         pix_color(i, red)
      if (ii == 22) :       
         pix_color(i, red)
      if (ii == 23) :       
         pix_color(i, red)
      if (ii == 24) :       
         pix_color(i, red)
      if (ii == 25) :       
         pix_color(i, red)
      if (ii == 26) :       
         pix_color(i, red)
      if (ii == 27) :       
         pix_color(i, red)
      if (ii == 28) :       
         pix_color(i, red)
         ii = 0
   pix_update_all(0.5)
   
   time.sleep(0.8)     
 
   pix_color_all(black)
   pix_update_all(0)

   ii = 0
   for i in range(LEDS):
      ii = ii + 1
      if (ii == 20) :       
         pix_color(i, yellow)
      if (ii == 22) :       
         pix_color(i, green)
      if (ii == 24) :       
         pix_color(i, blue)
      if (ii == 26) :       
         pix_color(i, white)
      if (ii == 28) :       
         pix_color(i, white)
         ii = 0
   pix_update_all(0.5)

   time.sleep(1.6)     

   ii = 0
   for i in range(LEDS):
      ii = ii + 1
      if (ii == 20) :       
         pix_color(i, red)
      if (ii == 21) :       
         pix_color(i, red)
      if (ii == 22) :       
         pix_color(i, red)
      if (ii == 23) :       
         pix_color(i, red)
      if (ii == 24) :       
         pix_color(i, red)
      if (ii == 25) :       
         pix_color(i, red)
      if (ii == 26) :       
         pix_color(i, red)
      if (ii == 27) :       
         pix_color(i, red)
      if (ii == 28) :       
         pix_color(i, red)
         ii = 0
   pix_update_all(0.5)
   
   time.sleep(0.8)     

   pix_color_all(black)
   pix_update_all(0)

   ii = 0
   for i in range(LEDS):
      ii = ii + 1
      if (ii == 20) :       
         pix_color(i, yellow)
      if (ii == 22) :       
         pix_color(i, green)
      if (ii == 24) :       
         pix_color(i, blue)
      if (ii == 26) :       
         pix_color(i, white)
      if (ii == 28) :       
         pix_color(i, white)
         ii = 0
   pix_update_all(0.5)

   time.sleep(1.6)     

   ii = 0
   for i in range(LEDS):
      ii = ii + 1
      if (ii == 20) :       
         pix_color(i, red)
      if (ii == 21) :       
         pix_color(i, red)
      if (ii == 22) :       
         pix_color(i, red)
      if (ii == 23) :       
         pix_color(i, red)
      if (ii == 24) :       
         pix_color(i, red)
      if (ii == 25) :       
         pix_color(i, red)
      if (ii == 26) :       
         pix_color(i, red)
      if (ii == 27) :       
         pix_color(i, red)
      if (ii == 28) :       
         pix_color(i, red)
         ii = 0
   pix_update_all(0.5)
   
   time.sleep(0.8)     

   pix_color_all(black)
   pix_update_all(0)

   ii = 0
   for i in range(LEDS):
      ii = ii + 1
      if (ii == 20) :       
         pix_color(i, yellow)
      if (ii == 22) :       
         pix_color(i, green)
      if (ii == 24) :       
         pix_color(i, blue)
      if (ii == 26) :       
         pix_color(i, white)
      if (ii == 28) :       
         pix_color(i, white)
         ii = 0
   pix_update_all(0.5)

   time.sleep(1.6)     

   ii = 0
   for i in range(LEDS):
      ii = ii + 1
      if (ii == 20) :       
         pix_color(i, red)
      if (ii == 21) :       
         pix_color(i, red)
      if (ii == 22) :       
         pix_color(i, red)
      if (ii == 23) :       
         pix_color(i, red)
      if (ii == 24) :       
         pix_color(i, red)
      if (ii == 25) :       
         pix_color(i, red)
      if (ii == 26) :       
         pix_color(i, red)
      if (ii == 27) :       
         pix_color(i, red)
      if (ii == 28) :       
         pix_color(i, red)
         ii = 0
   pix_update_all(0.5)
   
   time.sleep(0.8)     

   pix_color_all(black)
   pix_update_all(0)

# scene 05 (XXX)
def scene05(): 

   for i in range(0, LEDS, 2):
      pix_color(i, blue)
      pix_bn(i, 0.2)
   pix_color(5, red)
   pix_bn(5, 0.2)
   pix_color(LEDS - 5, red)
   pix_bn(LEDS - 5, 0.2)
   pix_update_all_bn()

   time.sleep(0.5)

   pix_color_all(black)
   pix_update_all(0)

   for i in range(0, 38, 2):
      pix_color(i, blue)
      pix_bn(i, 0.01)
      pix_color(LEDS-1-i, blue)
      pix_bn(LEDS-1-i, 0.01)
   pix_color(5, red)
   pix_bn(5, 0.2)
   pix_color(LEDS - 5, red)
   pix_bn(LEDS - 5, 0.2)
   pix_update_all_bn()
   
   for g in range(4):

      time.sleep(0.2)

      if g == 0:
          col = white
          rcol = greenblue
          rb1 = 0.01
          rb2 = 0.3
      if g == 1:
          col = yellow
          rcol = blue
          rb2 = 0.01
          rb1 = 0.3
      if g == 2:
          col = white
          rcol = blue
          rb1 = 0.01
          rb2 = 0.3
      if g == 3:
          col = yellow
          rcol = greenblue
          rb2 = 0.01
          rb1 = 0.3

      d1 = 78
      d2 = 43
      
      while(d2 < 79):
          
         for i in range(38):
            pix_color(i, rcol)
            pix_bn(i, rb1)
            pix_color(LEDS-1-i, rcol)
            pix_bn(LEDS-1-i, rb2)      
          
         pix_color(d1, col)
         pix_color(d2, col)
         pix_bn(d1, 0.5)
         pix_bn(d2, 0.5)
         pix_color(d1 - 1, col)
         pix_color(d2 + 1, col)
         pix_bn(d1 - 1, 0.5)
         pix_bn(d2 + 1, 0.5)
         pix_update_all_bn()
         r1 = d1
         r2 = d2
         d1 -= 1
         d2 += 1
         time.sleep(0.02)
         pix_color(r1, black)
         pix_color(r2, black)   
         pix_bn(r1, 0.5)
         pix_bn(r2, 0.5) 
         pix_color(r1 - 1, black)
         pix_color(r2 + 1, black)   
         pix_bn(r1 - 1, 0.5)
         pix_bn(r2 + 1, 0.5) 
      pix_update_all_bn()
      
   pix_color_all(black)
   pix_update_all(0)

   for i in range(0, 38, 2):
      pix_color(i, blue)
      pix_bn(i, 0.01)
      pix_color(LEDS-1-i, blue)
      pix_bn(LEDS-1-i, 0.01)
   pix_color(5, red)
   pix_bn(5, 0.2)
   pix_color(LEDS - 5, red)
   pix_bn(LEDS - 5, 0.2)
   pix_update_all_bn()

   time.sleep(0.2)

   for i in range(0, LEDS, 2):
      pix_color(i, blue)
      pix_bn(i, 0.2)
   pix_color(5, red)
   pix_bn(5, 0.2)
   pix_color(LEDS - 5, red)
   pix_bn(LEDS - 5, 0.2)
   pix_update_all_bn()

   time.sleep(0.5)

   pix_color_all(black)
   pix_update_all(0)

# scene 06 (green)
def scene06(): 
   
  for gc in range(16):
   pix_color(1, (220,220,80))
   for i in range(32):
      if (i & 4) :       
         pix_color(i, (80+(gc*5),150-(gc*7),0))
   pix_update_all(0.5)
   time.sleep(1)     
   for i in range(20):
      if (i & 4) :       
         pix_color(i+16, (100,100,100))
   pix_update_all(0.02)
   time.sleep(0.2)     
   for i in range(10):
      if (i & 4) :       
         pix_color(i+16, (150,0,150))
   pix_update_all(0.5)
   time.sleep(0.1)     
   for i in range(20):
      if (i & 4) :       
         pix_color(i+16, (100,100,100))
   pix_update_all(0.02)
   time.sleep(0.2)     
   

  pix_color_all(black)
  pix_update_all(0)


#-------------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------------

# color definitions, brightness adjusted
white = (120,120,120)
red = (220,0,0)
orange = (200,55,0)
yellow = (180,110,0)
green = (0,200,0)
blue = (0,0,255)
greenblue = (0,100,155)
greenyellow = (80,150,0)
black = (0,0,0)

# color triple list
cl = list([red, yellow, green, blue])

# starting...

# waiting for button press
while not start.value():
   time.sleep(0.3)
   onboardLED.toggle()

# warning before processing
ws()

# doing the strip

scene06()
while not start.value():
   time.sleep(0.3)
   onboardLED.toggle()
ws()

scene04()
while not start.value():
   time.sleep(0.3)
   onboardLED.toggle()
ws()

scene05()
while not start.value():
   time.sleep(0.3)
   onboardLED.toggle()

#scene01()
#scene02()
#scene03()
#testscene()

#-------------------------------------------------------------------------------
# physical end
#-------------------------------------------------------------------------------


    