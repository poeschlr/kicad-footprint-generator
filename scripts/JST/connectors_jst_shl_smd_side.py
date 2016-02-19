#!/usr/bin/env python

import sys
sys.path.append(r'''C:\kicad\fp-gen\kicad_mod''') # load kicad_mod path

import argparse
from kicad_mod import KicadMod, createNumberedPadsSMD

parser = argparse.ArgumentParser()
parser.add_argument('pincount', help='number of pins of the jst connector', type=int, nargs=1)
parser.add_argument('-v', '--verbose', help='show extra information while generating the footprint', action='store_true') #TODO
args = parser.parse_args()

# http://www.jst-mfg.com/product/pdf/eng/eSHL.pdf

pincount = int(args.pincount[0])

pad_spacing = 1
start_pos_x = -(pincount-1)*pad_spacing/2
end_pos_x = (pincount-1)*pad_spacing/2

pad_w = 0.6
pad_h = 1.4

B = 2.8 + pincount
A = (pincount - 1) * 1.0

jst_name = "SM{pincount:02}B-SHLS-TF".format(pincount=pincount)

# SMT type shrouded header, Side entry type (normal type)
footprint_name = "JST_SHL_" + jst_name + "_{pincount:02}x1.00mm_Angled_SMT".format(pincount=pincount)

kicad_mod = KicadMod(footprint_name)
kicad_mod.setDescription("JST SHL series connector, " + jst_name) 
kicad_mod.setAttribute('smd')
kicad_mod.setTags('connector jst SHL SMT side horizontal entry 1.0mm pitch')

kicad_mod.setCenterPos({'x':0, 'y':0})

# set general values
kicad_mod.addText('reference', 'REF**', {'x':0, 'y':-4}, 'F.SilkS')
kicad_mod.addText('value', footprint_name, {'x':0, 'y':5}, 'F.Fab')

#create outline
# create Courtyard
# output kicad model

#create pads
createNumberedPadsSMD(kicad_mod, pincount, pad_spacing, {'x':pad_w,'y':pad_h}, -4.6/2 + pad_h/2)

#add mounting pads (no number)
mpad_w = 1.0
mpad_h = 2.0
mpad_x = (B/2) - (mpad_w/2)
mpad_y = 4.6/2 - mpad_h/2

kicad_mod.addPad('""', 'smd', 'rect', {'x':mpad_x, 'y':mpad_y}, {'x':mpad_w, 'y':mpad_h}, 0, ['F.Cu', 'F.Paste', 'F.Mask'])
kicad_mod.addPad('""', 'smd', 'rect', {'x':-mpad_x, 'y':mpad_y}, {'x':mpad_w, 'y':mpad_h}, 0, ['F.Cu', 'F.Paste', 'F.Mask'])

#add bottom line
kicad_mod.addPolygoneLine([{'x':-B/2-0.1,'y':4.6/2+0.8-0.4},
                         {'x':-B/2-0.1,'y':4.6/2+0.8},
                         {'x':B/2+0.1,'y':4.6/2+0.8},
                         {'x':B/2+0.1,'y':4.6/2+0.8-0.4}])
                         
#add left line
kicad_mod.addPolygoneLine([{'x':-B/2-0.1,'y':-0.1},
                            {'x':-B/2-0.1,'y':-3.5/2},
                            {'x':-A/2-pad_w/2-0.4,'y':-3.5/2}])

#add right line
kicad_mod.addPolygoneLine([{'x':B/2+0.1,'y':-0.1},
                            {'x':B/2+0.1,'y':-3.5/2},
                            {'x':A/2+pad_w/2+0.4,'y':-3.5/2}])                                  

#add designator for pin #1

x1 = 0

if (pincount % 2 == 1): #odd pins
    x1 = -pincount/2.0 * 1.0 + 0.5
else: #even pins
    x1 = (-pincount/2) + 0.5
                          
y1 = -4.6/2 - 0.5

kicad_mod.addPolygoneLine([{'x':x1,'y':y1},
                           {'x':x1-0.25,'y':y1-0.5},
                           {'x':x1+0.25,'y':y1-0.5},
                           {'x':x1,'y':y1}])
                          
#add courtyard
kicad_mod.addRectLine({'x':-B/2-0.5,'y':-4.6/2-0.5},{'x':B/2+0.5,'y':4.6/2+0.7+0.5},'F.CrtYd',0.05)

f = open(footprint_name + ".kicad_mod","w")

f.write(kicad_mod.__str__())

f.close()
