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

PREFIX = '1591XX'
SUFFIZ = 'S'

#parameters for various enclosures in the series
Params = namedtuple("Params", [
    'L', #Length (not including flange)
    'W', #Width
    
    #inner dimensions
    'iL', #inside length
    'iW', #inside width
    
    #screw post dimensions
    'pL', #horizontal distance between interiors of mounting posts
    'pW', #vertical distance between interiors of mounting postss
    
    #PCB parameters
    'pcb_L', #PCB Maximum Length
    'pcb_W', #PCB Maximum Width
    
    'pcb_L2', #length of small horizontal side
    'pcb_W2', #length of small vertical side
    
    'pcb_x', #horizontal distance between mounting hole centers
    'pcb_y', #vertical distance between mounting hole centers
    
    'pcb_c', #pcb corner radius
])

#descriptions of the various enclosures
enc = {}

enc['M'] = Params(
    L = 85,
    W = 56,
    
    #pcb dimensions
    pcb_L = 80.7,
    pcb_W = 51.51,
    
    pcb_L2 = 64.7,
    pcb_W2 = 35.51,
    
    #pcb hole centers
    pcb_x = 50.27,
    pcb_y = 30.51,
    
    pcb_c = 3.51,
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
    name = PREFIX + k + SUFFIX
    
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
    px = prop.pcb_x / 2
    py = prop.pcb_y / 2
    
    fp.append(Pad(at=[px,py],size=2.50,drill=2.50,shape=Pad.SHAPE_CIRCLE,type=Pad.TYPE_NPTH,layers=["*.Cu"]))
    fp.append(Pad(at=[-px,-py],size=2.50,drill=2.50,shape=Pad.SHAPE_CIRCLE,type=Pad.TYPE_NPTH,layers=["*.Cu"]))
    
    fp.append(Circle(center=[px,py],radius=2.0,width=0.15, layer="B.SilkS"))
    fp.append(Circle(center=[px,py],radius=2.0,width=0.15, layer="F.SilkS"))
    
    fp.append(Circle(center=[-px,-py],radius=2.0,width=0.15, layer="B.SilkS"))   
    fp.append(Circle(center=[-px,-py],radius=2.0,width=0.15, layer="F.SilkS"))   
    
    #generate the outline of the pcb
    #top side
    pcb = [
    {'x': -prop.pcb_L/2 + pcb_C - pcb_R,'y': prop.pcb_W/2 - pcb_C},
    {'x': -prop.pcb_L/2 ,'y': prop.pcb_W/2 - pcb_C},
    {'x': -prop.pcb_L/2 ,'y': -prop.pcb_W/2},
    {'x': prop.pcb_L/2 - pcb_C,'y': -prop.pcb_W/2},
    {'x': prop.pcb_L/2 - pcb_C,'y': -prop.pcb_W/2 + pcb_C - pcb_R},
    ]
    
    fp.append(PolygoneLine(polygone=pcb, layer='Edge.Cuts', width=0.1))
    fp.append(PolygoneLine(polygone=pcb, layer='Edge.Cuts', width=0.1, x_mirror=0, y_mirror=0))
    
    #add the arcs
    fp.append(Arc(center=[prop.pcb_L/2 - pcb_C + pcb_R, -prop.pcb_W/2 + pcb_C - pcb_R],end=[prop.pcb_L/2 - pcb_C + pcb_R, -prop.pcb_W/2 + pcb_C], angle=90, layer='Edge.Cuts', width=0.1))
    fp.append(Arc(center=[-prop.pcb_L/2 + pcb_C - pcb_R, prop.pcb_W/2 - pcb_C + pcb_R],end=[-prop.pcb_L/2 + pcb_C - pcb_R, prop.pcb_W/2 - pcb_C], angle=90, layer='Edge.Cuts', width=0.1))
    
    #enclosure 'thickness'
    T = (prop.W - prop.iW) / 2
    
    #generate the inner dimensions of the enclosure
    fp.append(RectLine(start=[-prop.iL/2,-prop.iW/2],end=[prop.iL/2,prop.iW/2],width=0.1,layer='Eco2.User'))
    fp.append(RectLine(start=[-prop.iL/2,-prop.iW/2],end=[prop.iL/2,prop.iW/2],width=0.1,layer='Eco2.User',offset=T))
    
    #generate positions of the plastic lid mounting posts
    px = prop.pL / 2 + 2.5
    py = prop.pW / 2 + 2.5
    
    fp.append(Circle(center=[px,-py],radius=1.75,layer='Eco2.User',width=0.1))
    fp.append(Circle(center=[px,-py],radius=2.5,layer='Eco2.User',width=0.1))
    
    fp.append(Circle(center=[-px,py],radius=1.75,layer='Eco2.User',width=0.1))
    fp.append(Circle(center=[-px,py],radius=2.5,layer='Eco2.User',width=0.1))
    
    #add a model
    fp.append(Model(filename="Enclosures.3dshapes/" + full + ".wrl"))
    
    #output filename
    filename = output_dir + full + ".kicad_mod"
    
    fh = KicadFileHandler(fp)
    fh.writeFile(filename)
