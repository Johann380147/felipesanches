#!/usr/bin/env python

import usb.core
import usb.util
import math
PI=3.1415
from random import random

def clamp(value, min, max):
  if value > max: return max
  if value < min: return min
  return int(value)

class LaserDisplay():
  # Configuration flags
  ALWAYS_ON = 1
  SOMETHING = 2

  # Shapes for our characher rendering routine
  GLYPHS = {"0": [[191, 130], [194, 194], [127, 191], [65, 191], [62, 129], [64, 62], [125, 62], [195, 65], [192, 131]],
  "1": [[178, 133], [130, 149], [119, 191], [118, 116], [121, 62]],
  "2": [[187, 131], [192, 189], [125, 192], [66, 190], [64, 149], [95, 97], [191, 66], [122, 63], [62, 64]],
  "3": [[189, 161], [192, 197], [120, 193], [12, 188], [111, 126], [21, 64], [120, 60], [189, 64], [189, 96]],
  "4": [[66, 127], [121, 128], [193, 125], [134, 156], [124, 194], [123, 128], [122, 64]],
  "5": [[65, 192], [122, 192], [192, 192], [192, 161], [190, 133], [64, 137], [63, 99], [65, 63], [192, 64]],
  "6": [[62, 160], [62, 193], [119, 194], [192, 194], [193, 133], [193, 65], [127, 62], [63, 64], [62, 99], [63, 130], [120, 131], [186, 125], [183, 93]],
  "7": [[194, 191], [124, 191], [64, 191], [146, 142], [188, 63]],
  "8": [[192, 164], [192, 193], [126, 195], [67, 192], [64, 165], [65, 137], [119, 133], [190, 134], [193, 102], [195, 64], [122, 60], [62, 64], [60, 89], [58, 119], [121, 132], [189, 134], [192, 166]],
  "9": [[65, 191], [191, 193], [193, 159], [190, 115], [131, 120], [75, 144], [62, 190], [64, 123], [66, 63]],
  ":": []}

  def __init__(self):  
    #self.ReplayInitLog()

    # find our device
    self.usbdev = usb.core.find(idVendor=0x9999, idProduct=0x5555)

    # was it found?
    if self.usbdev is None:
        raise ValueError('Device (9999:5555) not found')

    # set the active configuration. With no arguments, the first
    # configuration will be the active one
    self.usbdev.set_configuration()

    # get an endpoint instance
    self.ep = usb.util.find_descriptor(
            self.usbdev.get_interface_altsetting(),   # first interface
            # match the first OUT endpoint
            custom_match = \
                lambda e: \
                    usb.util.endpoint_direction(e.bEndpointAddress) == \
                    usb.util.ENDPOINT_OUT
        )

    assert self.ep is not None
    
    self.flags = self.ALWAYS_ON

    self.MaxNoise = 0

    self.ep.write([0xca, 0x2a]);

    self.set_color([0xFF,0x00,0x00])
    
    self.adjust_glyphs()
    
  def adjust_glyphs(self):
    for k in self.GLYPHS.keys():
      self.GLYPHS[k] = map(lambda(p):([p[0]/255.0,p[1]/255.0]),self.GLYPHS[k])

  def ReplayInitLog(self):
    # find our device
    self.usbdev=None
    for bus in usb.busses():
      for dev in bus.devices:
        if dev.idVendor == 0x3333:
          self.usbdev = dev
    
    # was it found?
    if self.usbdev is None:
        raise ValueError('Device (3333:5555) not found')

    handle = self.usbdev.open() 
  
    print "Initializing device using data collected with USBSnoop"
    snifferlog = open("usbinit.log")

    for line in snifferlog.readlines():
      setup_packet = line.split("|")[0]
      buf = line.split("|")[-1]
      if len(buf):
        values = setup_packet.strip().split(" ")
        reqType = int(values[0],16)
        req = int(values[1],16)
 
        value = int(values[3],16)*256+int(values[2],16)
        index = int(values[5],16)*256+int(values[4],16)
        length = int(values[7],16)*256+int(values[6],16)

        value = int(values[2],16)*256+int(values[3],16)
        index = int(values[4],16)*256+int(values[5],16)
        length = int(values[6],16)*256+int(values[7],16)
 
        print "=== sending ==="
        print "bmRequestType: "+hex(reqType)
        print "bRequest: "+hex(req)
        print "wValue: "+hex(value)
        print "wIndex: "+hex(index)
        print "buffer: "+buf

        buf = ""
        for byte in buf.strip().split(" "):
          buf+=chr(int(byte,16))

        handle.controlMsg(reqType,req,buf,value,index)   

    print "done."

  def set_noise(self, value):
    self.MaxNoise = value
    
  def set_flags(self, flags):
    self.flags = flags

  def set_color(self, c):
    self.color = {"R": c[0], "G": c[1], "B": c[2]}
  
  def line_message(self, x1,y1,x2,y2):
    x1+=random()*self.MaxNoise-self.MaxNoise/2
    y1+=random()*self.MaxNoise-self.MaxNoise/2
    x2+=random()*self.MaxNoise-self.MaxNoise/2
    y2+=random()*self.MaxNoise-self.MaxNoise/2

    x1 = clamp(x1,0,255)
    y1 = clamp(y1,0,255)
    x2 = clamp(x2,0,255)
    y2 = clamp(y2,0,255)
    return [x1, 0x00, y1, 0x00, self.color["R"], self.color["G"], self.color["B"], 0x03, x2, 0x00, y2, 0x00, self.color["R"], self.color["G"], self.color["B"], 0x02]

  def point_message(self, x, y):
    x+=random()*self.MaxNoise-self.MaxNoise/2
    y+=random()*self.MaxNoise-self.MaxNoise/2
    x = clamp(x,0,255)
    y = clamp(y,0,255)

    return [x, 0x00, y, 0x00, self.color["R"], self.color["G"], self.color["B"], self.flags]

  def draw_line(self, x1,y1,x2,y2):
    self.ep.write(self.line_message(x1, y1, x2, y2))

  def gen_glyph_data(self, char, x, y, rx, ry):
    glyph_data = []
    for i in range(len(self.GLYPHS[char])):
      glyph_data.append([(int)(x + (self.GLYPHS[char][i][0])*rx),(int)(y + (self.GLYPHS[char][i][1])*ry)]);
    return glyph_data

  def draw_text(self, string, x, y, size, kerning_percentage = -0.3):
    for char in string:
      glyph_curve = self.gen_glyph_data(char, x, y, size, size*2)
      self.draw_bezier(glyph_curve, 5)
      x -= int(size + size * kerning_percentage)

  def draw_bezier(self, points, steps):
    if len(points) < 3:
      print "Quadratic Bezier curves have to have at least three points"
      return

    step_inc = 1.0/(steps)

    message = []
    self.set_flags(0x03)
    message += self.point_message(points[0][0], points[0][1])
    self.set_flags(0x00)

    for i in range(0, len(points) - 2, 2):
      t = 0.0
      t_1 = 1.0
      for s in range(steps):
        t += step_inc
        t_1 = 1.0 - t
        if s == steps - 1 and i >= len(points) - 2:
          self.set_flags(0x02)
        message += (self.point_message(t_1 * (t_1 * points[i]  [0] + t * points[i+1][0]) + \
                                       t   * (t_1 * points[i+1][0] + t * points[i+2][0]),  \
                                       t_1 * (t_1 * points[i]  [1] + t * points[i+1][1]) + \
                                       t   * (t_1 * points[i+1][1] + t * points[i+2][1])))

    self.ep.write(message)

  #TODO: refactor it. It should not be in our API
  def draw_dashed_circle(self, x,y,r, c1, c2):
    step = 32
    for alpha in range(step):
      if alpha%2:
        self.set_color(c1)
      else:
        self.set_color(c2)
        
      self.ep.write(self.line_message(x + r*math.cos(alpha*2*PI/step), y + r*math.sin(alpha*2*PI/step), x + r*math.cos((alpha+1)*2*PI/step), y + r*math.sin((alpha+1)*2*PI/step)))

  def start_frame(self):
    self.messageBuffer = []

  def end_frame(self):
    self.ep.write(self.messageBuffer)

  def schedule(self, message):
    for byte in message:
      self.messageBuffer.append(byte)

