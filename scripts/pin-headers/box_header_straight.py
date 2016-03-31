#!/usr/bin/env python

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

drill = 1.0
size = 1.75
pitch = 2.54

for rows in [2]:
    for pincount in range(2,21): #range(1,21):

        # Through-hole type shrouded header, Top entry type
        footprint_name = 'Box_Header_Straight_{rows:01}x{pincount:02}x2.54mm'.format(rows=rows,pincount=pincount)

        footprint = Footprint(footprint_name)
        
        footprint.setDescription("Through hole box header, {rows}x{pincount:02}, 2.54mm pitch, ".format(rows=rows,pincount=pincount))
        footprint.setTags("conn box header idc")
        
        #general header dimensions
        D = (pincount - 1) * pitch
        A = 7.62 + pincount * pitch

        W1 = 8.9 #external width of connector
        W2 = 6.4 #internal width of connector
        
        #wall thickness T
        T = (W1 - W2) / 2
        
        #x,y dimensions of outside of connector housing
        x1 = -(A-D) / 2
        x2 = x1 + A
        
        y1 = -W1/2 - 2.54/2
        y2 = y1 + W1

        # set general values
        footprint.append(Text(type='reference', text='REF**', at=[D/2,4.5], layer='F.SilkS'))
        footprint.append(Text(type='value', text=footprint_name, at=[D/2,-7], layer='F.Fab'))
        
        #add the outside of the connector
        footprint.append(RectLine(start=[x1,y1],end=[x2,y2],offset=0.2))
        #add the inside of the connector
        footprint.append(RectLine(start=[x1,y1],end=[x2,y2],offset=-T))
        
        #draw tab
        footprint.append(Line(start=[D/2-2,y2],end=[D/2-2,y2-T]))
        footprint.append(Line(start=[D/2+2,y2],end=[D/2+2,y2-T]))
        
        #add the courtyard
        footprint.append(RectLine(start=[x1,y1],end=[x2,y2],offset=0.5,grid=0.05,width=0.05,layer="F.CrtYd"))
        
        #add pins
        footprint.append(PadArray(pincount = pincount, x_spacing=pitch, type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, increment=2, size=size, drill=drill, layers=['*.Cu','*.Mask']))
        footprint.append(PadArray(pincount = pincount, x_spacing=pitch, start=[0,-pitch], type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, increment=2, initial=2, size=size, drill=drill, layers=['*.Cu','*.Mask']))
        
        #add a pin-1 indicator
        x = 0
        y = 3.8
        m = 0.3
        
        pin = [
        {'x': x,'y': y},
        {'x': x-m,'y': y+2*m},
        {'x': x+m,'y': y+2*m},
        {'x': x,'y': y},
        ]
        
        footprint.append(PolygoneLine(polygone=pin))
        
        #Add a model
        footprint.append(Model(filename="Pin_Headers.3dshapes/" + footprint_name + ".wrl"))
        
        #filename
        filename = output_dir + footprint_name + ".kicad_mod"
        
        file_handler = KicadFileHandler(footprint)
        file_handler.writeFile(filename)
