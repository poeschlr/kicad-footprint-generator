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
from KicadModTree.nodes.specialized.PadArray import PadArray

from collections import namedtuple

# LGA parameters
LGA = namedtuple("LGA", [
    'N1', #pitch
    'E1', #length
    'D1', #width,
    'T1', #pin length
    'T2', #pin width
    'M', #distance between end of pad and case
    'nx', #number of pads in x-dir
    'ny', #number of pads in y-dir
    'ep', #endpoint?
])

lga = {
    'lga-14-2x2' : LGA(
    #http://www.st.com/web/en/resource/technical/document/datasheet/DM00042751.pdf
    N1 = 0.35,
    E1 = 2,
    D1 = 2,
    T1 = 0.275,
    T2 = 0.2,
    M = 0.1,
    nx = 3,
    ny = 4,
    ep = False
    ),

    'lga-16-3x3' : LGA(
    #http://www.st.com/web/en/resource/technical/document/datasheet/CD00213470.pdf
    N1 = 0.5,
    E1 = 3,
    D1 = 3,
    T1 = 0.35,
    T2 = 0.25,
    M = 0.1,
    nx = 3,
    ny = 5,
    ep = False
    ),
    
    'lga-24-3x5' : LGA(
    #http://cache.freescale.com/files/sensors/doc/data_sheet/FXLC95000CL.pdf
    N1 = 0.5,
    E1 = 5,
    D1 = 3,
    T1 = 0.65,
    T2 = 0.25,
    M = 0.1,
    nx = 5,
    ny = 7,
    ep = False
    ),
    
    'lga-16-4x4' : LGA(
    #http://www.st.com/web/en/resource/technical/document/datasheet/DM00036465.pdf
    N1 = 0.65,
    D1 = 4,
    E1 = 4,
    T1 = 0.4,
    T2 = 0.3,
    M = 0.1,
    nx = 4,
    ny = 4,
    ep = False
    ),
    
    #http://www.st.com/web/en/resource/technical/document/datasheet/CD00237186.pdf
    'lga-16-5x5' : LGA(
    N1 = 0.8,
    D1 = 5,
    E1 = 5,
    T1 = 0.8,
    T2 = 0.5,
    M = 0.1,
    nx = 3,
    ny = 5,
    ep = False
    ),
    
    #http://www.st.com/web/en/resource/technical/document/datasheet/CD00254134.pdf
    'lga-28-4x5' : LGA(
    N1 = 0.5,
    D1 = 5,
    E1 = 4,
    T1 = 0.325,
    T2 = 0.25,
    M = 0.075,
    nx = 8,
    ny = 6,
    ep = False
    ),
    
    #http://www.st.com/web/en/resource/technical/document/datasheet/CD00199096.pdf
    'lga-28-7x7' : LGA(
    N1 = 0.8,
    D1 = 7,
    E1 = 7,
    T1 = 0.45,
    T2 = 0.35,
    M = 0.1,
    nx = 7,
    ny = 7,
    ep = False
    )
}

name = "LGA-{n}{ep}_{x}x{y}mm_Pitch{pitch}mm"

for key in lga.keys():

    part = lga[key]
    
    #how many pins?
    n = 2 * part.nx + 2 * part.ny
    
    partname = name.format(n=n, ep = "-1EP" if part.ep else "", x=part.D1, y=part.E1, pitch=part.N1)
    
    fp = Footprint(partname)
    
    print(partname)
    
    #description
    
    fp.setAttribute("smd")
    fp.setDescription("LGA-{n}, {x}x{y}, p={pitch}".format(n=n,x=part.D1, y=part.E1, pitch=part.N1))
    fp.setTags("LGA {p}".format(p=part.N1))
    
    #set general values
    
    fp.append(Text(type='reference', text='REF**', at=[0,-part.E1/2-1.5], layer='F.SilkS'))
    fp.append(Text(type='value', text=partname, at=[0,part.E1/2+1.5], layer='F.Fab'))
    
    #calculations
    #length of pads
    #extend pads all the way up to the base
    pl = part.T1 + part.M + 0.2
    
    #position of pads
    #center line of sides
    x = part.D1 / 2 - part.T1 / 2 + 0.2
    
    #center line of top/bottom
    y = part.E1 / 2 - part.T1 / 2 + 0.2
    
    #pad layers
    layers = ['F.Cu','F.Mask','F.Paste']
    
    #add the outline of the part to the F.Fab layer
    if part.D1 < 2:
        b = 0.5
    else:
        b = 1
    outline = [
    {'x': -part.D1/2 + b,'y': -part.E1/2},
    {'x': part.D1/2,'y': -part.E1/2},
    {'x': part.D1/2,'y': part.E1/2},
    {'x': -part.D1/2,'y': part.E1/2},
    {'x': -part.D1/2,'y': -part.E1/2 + b},
    {'x': -part.D1/2 + b,'y': -part.E1/2},
    ]
    
    fp.append(PolygoneLine(polygone=outline, layer='F.Fab'))
    #fp.append(RectLine(start=[-part.D1/2,-part.E1/2],end=[part.D1/2,part.E1/2],layer='F.Fab'))
    
    #draw the left-hand-pads
    fp.append(PadArray(pincount=part.ny, y_spacing=part.N1, center=[-x,0], size=[pl,part.T2], layers=layers, type=Pad.TYPE_SMT, shape=Pad.SHAPE_RECT))
    
    #draw the right-hand size
    fp.append(PadArray(pincount=part.ny, initial=1+part.nx+part.ny, y_spacing=-part.N1, center=[x,0], size=[pl,part.T2], layers=layers, type=Pad.TYPE_SMT, shape=Pad.SHAPE_RECT))
    
    #generate the bottom side
    fp.append(PadArray(pincount=part.nx, initial=1+part.ny, x_spacing=part.N1, center=[0,y], size=[part.T2,pl], layers=layers, type=Pad.TYPE_SMT, shape=Pad.SHAPE_RECT))
    
    #draw the top side
    fp.append(PadArray(pincount=part.nx, initial=1+part.nx+part.ny+part.ny, x_spacing=-part.N1, center=[0,-y], size=[part.T2,pl], layers=layers, type=Pad.TYPE_SMT, shape=Pad.SHAPE_RECT))
    
    L1 = (part.nx - 1) * part.N1 + part.T2
    L2 = (part.ny - 1) * part.N1 + part.T2
    
    #component outline
    off = 0.15
    out = [
    {'x': L1/2 + 0.3,'y': -part.E1/2 - off},
    {'x': part.D1/2 + off ,'y': -part.E1/2 - off},
    {'x': part.D1/2 + off,'y': -L2/2 - 0.3},
    ]

    fp.append(PolygoneLine(polygone=out))
    fp.append(PolygoneLine(polygone=out, y_mirror=0))
    fp.append(PolygoneLine(polygone=out, x_mirror=0))
    
    #pin-1 indication
    p1 = [
        {'x': -L1/2 - 0.3,'y': -part.E1/2-off},
        {'x': -part.D1/2 - off,'y': -part.E1/2-off},
        #{'x': -part.D1/2 - off,'y': -L2/2 - 0.3},
        #{'x': -x-pl/2,'y': -L2/2 - 0.3},
    ]
    
    fp.append(PolygoneLine(polygone=p1))
    #fp.append(Line( start = [-L1/2-0.25,-part.E1/2-off],
    #                end  = [-part.D1/2-0.2,-part.E1/2-off]))
    
    #max dims
    xmax = x + pl / 2
    ymax = y + pl / 2
    
    #draw component outline
    fp.append(RectLine(start=[-xmax,-ymax],end=[xmax,ymax],width=0.05,grid=0.05,offset=0.25,layer='F.CrtYd'))
    
    #Add a model
    fp.append(Model(filename="Housings_DFN_QFN.3dshapes/" + partname + ".wrl"))
    
    #filename
    filename = output_dir + partname + ".kicad_mod"
    
    file_handler = KicadFileHandler(fp)
    file_handler.writeFile(filename)
        
