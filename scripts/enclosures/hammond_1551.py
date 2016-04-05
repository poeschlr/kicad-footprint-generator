#!/usr/bin/env python

'''
kicad-footprint-generator is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

kicad-footprint-generator is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with kicad-footprint-generator. If not, see < http://www.gnu.org/licenses/ >.
'''

import sys
import os

output_dir = os.getcwd()

#if specified as an argument, extract the target directory for output footprints
if len(sys.argv) > 1:
    out_dir = sys.argv[1]
    
    if os.path.isabs(out_dir) and os.path.isdir(out_dir):
        output_dir = out_dir
    else:
        out_dir = os.path.join(os.getcwd(),out_dir)
        if os.path.isdir(out_dir):
            output_dir = out_dir

if output_dir and not output_dir.endswith(os.sep):
    output_dir += os.sep
        
#import KicadModTree files
sys.path.append("..\\..")
from KicadModTree import *

from collections import namedtuple

#common parameters
#x,y size of PCB corner cutout
pcb_C = 6.25

#pcb corner cutout radius
pcb_R = 3.0

#pcb drill diameter
pcb_D = 2.50

#corner radius CR
CR = 0.5

PREFIX = '1551'
SUFFIX = 'FL'

#parameters for various enclosures in the series
Params = namedtuple("Params", [
    'L', #Length (not including flange)
    'W', #Width
    
    #inner dimensions
    'iL', #inside length
    'iW', #inside width
    
    #screw post dimensions
    'pL', #horizontal distance between exteriors of mounting posts
    'pW', #vertical distance between exteriors of mounting postss
    
    #PCB parameters
    'pcb_L', #PCB Maximum Length
    'pcb_W', #PCB Maximum Width
    
    'pcb_v', #offset of hole from vertical edge
    'pcb_h', #offset of hole from horizontal edge
])

#descriptions of the various enclosures
enc = {}

enc['N'] = Params(
    L = 35.0,
    W = 35.0,
    
    iL = 30.17,
    iW = 30.17,
    
    pL = 28.73,
    pW = 28.8,
    
    pcb_L = 29.0,
    pcb_W = 29.0,
    
    pcb_v = 2.75,
    pcb_h = 5.75,
)

enc['M'] = Params(
    L = 35.0,
    W = 35.0,
    
    iL = 29.73,
    iW = 29.73,
    
    pL = 28.73,
    pW = 28.28,
    
    pcb_L = 29.0,
    pcb_W = 29.0,
    
    pcb_v = 2.75,
    pcb_h = 5.75,
)

enc['Q'] = Params(
    L = 40.0,
    W = 40.0,
    
    iL = 35.12,
    iW = 35.0,
    
    pL = 33.8,
    pW = 33.8,
    
    pcb_L = 34.5,
    pcb_W = 34.5,
    
    pcb_v = 3.0,
    pcb_h = 7.25,
)

enc['P'] = Params(
    L = 40.0,
    W = 40.0,
    
    iL = 34.72,
    iW = 34.72,
    
    pL = 33.8,
    pW = 33.8,
    
    pcb_L = 34.0,
    pcb_W = 34.0,
    
    pcb_v = 2.75,
    pcb_h = 7.0,
)
    
enc['F'] = Params(
    L = 50.0,
    W = 35.0,
    
    iL = 45.17,
    iW = 30.17,
    
    pL = 43.88,
    pW = 28.88,
    
    pcb_L = 44.5,
    pcb_W = 29.5,
    
    pcb_v = 3.0,
    pcb_h = 9.75,
)

enc['G'] = Params(
    L = 50.0,
    W = 35.0,
    
    iL = 44.73,
    iW = 29.73,
    
    pL = 43.88,
    pW = 28.88,
    
    pcb_L = 44.0,
    pcb_W = 29.0,
    
    pcb_v = 2.75,
    pcb_h = 12.00,
)
    
enc['S'] = Params(
    L = 50.0,
    W = 50.0,
    
    iL = 45.12,
    iW = 45.12,
    
    pL = 43.8,
    pW = 43.73,
    
    pcb_L = 44.0,
    pcb_W = 44.0,
    
    pcb_v = 2.75,
    pcb_h = 9.50,
)

enc['R'] = Params(
    L = 50.0,
    W = 50.0,
    
    iL = 44.72,
    iW = 44.72,
    
    pL = 43.8,
    pW = 43.73,
    
    pcb_L = 44.0,
    pcb_W = 44.0,
    
    pcb_v = 2.75,
    pcb_h = 9.50,
)

enc['J'] = Params(
    L = 60.0,
    W = 35.0,
    
    iL = 55.17,
    iW = 30.17,
    
    pL = 53.88,
    pW = 28.88,
    
    pcb_L = 54.5,
    pcb_W = 29.5,
    
    pcb_v = 3.0,
    pcb_h = 12.25,
)

enc['H'] = Params(
    L = 60.0,
    W = 35.0,
    
    iL = 54.73,
    iW = 29.73,
    
    pL = 53.88,
    pW = 28.88,
    
    pcb_L = 54.0,
    pcb_W = 29.0,
    
    pcb_v = 2.75,
    pcb_h = 12.70,
)

enc['L'] = Params(
    L = 80.0,
    W = 40.0,
    
    iL = 75.17,
    iW = 35.17,
    
    pL = 73.8,
    pW = 33.8,
    
    pcb_L = 74.0,
    pcb_W = 34.0,
    
    pcb_v = 2.75,
    pcb_h = 17.0,
)

enc['K'] = Params(
    L = 80.0,
    W = 40.0,
    
    iL = 74.73,
    iW = 34.73,
    
    pL = 73.8,
    pW = 33.8,
    
    pcb_L = 74.0,
    pcb_W = 34.0,
    
    pcb_v = 2.75,
    pcb_h = 17.0,
)

"""
footprint specific details to go here

Hammond 1551-series enclosures
http://www.hammondmfg.com/dwg9FL.htm

"""

for k in enc.keys():
    
    #properties
    prop = enc[k]
    
    #part name
    name = PREFIX + k   
    
    #complete part name
    full = "Hammond_{n}_{l}x{w}".format(n=name,l=int(prop.L),w=int(prop.W))
    
    pdf = "http://www.hammondmfg.com/pdf/{pn}.pdf".format(pn=name)
    
    fp = Footprint(full)
    
    fp.setAttribute("virtual")
    
    description = "Hammond miniature plastic enclosure, 1551-FL series, flanged lid, " + pdf
    
    tags = "enclosure hammond plastic 1551" 
    
    fp.setDescription(description)
    fp.setTags(tags)
    
    #texts
    fp.append(Text(type='reference', text="REF**", at=[0,-2], layer="F.SilkS", hide=True))
    fp.append(Text(type='value', text=full, at=[0,2], layer="F.Fab", hide=True))
    
    #draw cross in the center of the box
    fp.append(Line(start=[-1,0],end=[1,0],layer="Eco1.User",width=0.1))
    fp.append(Line(start=[0,-1],end=[0,1],layer="Eco1.User",width=0.1))
    
    #add the mounting holes
    px = prop.pcb_L/2 - prop.pcb_h
    py = prop.pcb_W/2 - prop.pcb_v
    
    fp.append(Pad(at=[px,py],size=2.50,drill=2.50,shape=Pad.SHAPE_CIRCLE,type=Pad.TYPE_NPTH,layers=["*.Cu"]))
    fp.append(Pad(at=[-px,-py],size=2.50,drill=2.50,shape=Pad.SHAPE_CIRCLE,type=Pad.TYPE_NPTH,layers=["*.Cu"]))
    
    fp.append(Circle(center=[px,py],radius=1.5,width=0.15))
    fp.append(Circle(center=[-px,-py],radius=1.5,width=0.15))   
    
    #generate the outline of the pcb
    #top side
    pcb = [
    {'x': -prop.pcb_L/2 + pcb_C - pcb_R,'y': prop.pcb_W/2 - pcb_C},
    {'x': -prop.pcb_L/2 ,'y': prop.pcb_W/2 - pcb_C},
    {'x': -prop.pcb_L/2 ,'y': -prop.pcb_W/2},
    {'x': prop.pcb_L/2 - pcb_C,'y': -prop.pcb_W/2},
    {'x': prop.pcb_L/2 - pcb_C,'y': -prop.pcb_W/2 + pcb_C - pcb_R},
    ]
    
    fp.append(PolygoneLine(polygone=pcb, layer='Eco1.User', width=0.1))
    fp.append(PolygoneLine(polygone=pcb, layer='Eco1.User', width=0.1, x_mirror=0, y_mirror=0))
    
    #add the arcs
    fp.append(Arc(center=[prop.pcb_L/2 - pcb_C + pcb_R, -prop.pcb_W/2 + pcb_C - pcb_R],end=[prop.pcb_L/2 - pcb_C + pcb_R, -prop.pcb_W/2 + pcb_C], angle=90, layer='Eco1.User', width=0.1))
    fp.append(Arc(center=[-prop.pcb_L/2 + pcb_C - pcb_R, prop.pcb_W/2 - pcb_C + pcb_R],end=[-prop.pcb_L/2 + pcb_C - pcb_R, prop.pcb_W/2 - pcb_C], angle=90, layer='Eco1.User', width=0.1))
    
    #enclose 'thickness'
    T = (prop.W - prop.iW) / 2
    
    #generate the inner dimensions of the enclosure
    fp.append(RectLine(start=[-prop.iL/2,-prop.iW/2],end=[prop.iL/2,prop.iW/2],width=0.1,layer='Eco2.User'))
    fp.append(RectLine(start=[-prop.iL/2,-prop.iW/2],end=[prop.iL/2,prop.iW/2],width=0.1,layer='Eco2.User',offset=T))
    
    #generate positions of the mounting posts
    px = prop.pL / 2 - (10.3 / 4)
    py = prop.pW / 2 - (10.3 / 4)
    
    fp.append(Circle(center=[px,-py],radius=1.75,layer='Eco2.User',width=0.1))
    fp.append(Circle(center=[px,-py],radius=2.5,layer='Eco2.User',width=0.1))
    
    fp.append(Circle(center=[-px,py],radius=1.75,layer='Eco2.User',width=0.1))
    fp.append(Circle(center=[-px,py],radius=2.5,layer='Eco2.User',width=0.1))
    
    #add a model
    #fp.append(Model(filename="Enclosures.3dshapes/" + full + ".wrl"))
    
    #output filename
    filename = output_dir + full + ".kicad_mod"
    
    fh = KicadFileHandler(fp)
    fh.writeFile(filename)
