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
"""
footprint specific details to go here

Datasheet: http://www.jst-mfg.com/product/pdf/eng/eXH.pdf

"""
pitch = 2.00

pincount = [2,3,4,5,6,7,17,22] #number of pins in each row
rows = 1

row_pitch = 2.0

drill = 0.80
drill_strain_relief = 0.90

pad_dia = 1.35


#FP name strings
part = "S{n:02}B-J21DK-GG" #JST part number format string

name = "Harwin_L-Tek_Male_1x{n:02}x{p:.2f}mm_Straight{supports}"

desc = "Harwin L-Tek Connector, single row male, vertical entry{supports}"

tags = "connector harwin ltek M80"
#FP description and tags

if __name__ == '__main__':

    for pins in pincount:
        
        for supports in [True,False]:
            #calculate fp dimensions
            A = (pins - 1) * pitch
            B = pins * pitch + 4.10
        
            #generate the name
            fp_name = name.format(n=pins, p=pitch, supports="_StrainRelief" if supports else "")

            footprint = Footprint(fp_name)
            
            #set the FP description
            footprint.setDescription(desc.format(supports=", strain relief clip" if supports else ''))
            
            #set the FP tags
            footprint.setTags(tags)

            # set general values
            footprint.append(Text(type='reference', text='REF**', at=[A/2,-3.5], layer='F.SilkS'))
            footprint.append(Text(type='value', text=fp_name, at=[A/2,3.5], layer='F.Fab'))
                
            #generate the pads (row 1)
            footprint.append(PadArray(pincount=pins, x_spacing=pitch, type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, size=pad_dia, drill=drill, layers=['*.Cu','*.Mask']))
            
            if supports:
                sx1 = -2.25
                sx2 = A + 2.25
                sy1 = -4.75/2
                sy2 = +4.75/2
                footprint.append(Pad(at=[sx1,sy1],type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, size=1.2, drill=drill_strain_relief, layers=['*.Cu','*.Mask']))
                footprint.append(Pad(at=[sx1,sy2],type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, size=1.2, drill=drill_strain_relief, layers=['*.Cu','*.Mask']))
                footprint.append(Pad(at=[sx2,sy1],type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, size=1.2, drill=drill_strain_relief, layers=['*.Cu','*.Mask']))
                footprint.append(Pad(at=[sx2,sy2],type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, size=1.2, drill=drill_strain_relief, layers=['*.Cu','*.Mask']))
                
            #outline
            x1 = A/2 - B/2
            x2 = x1 + B
            
            y1 = -2
            y2 = +2
            
            #rough outline
            footprint.append(RectLine(start=[x1,y1],end=[x2,y2],offset=0.1))
            #courtyard
            footprint.append(RectLine(start=[x1,y1],end=[x2,y2],offset=0.5,grid=0.05,width=0.05,layer='F.CrtYd'))
            """
            #draw the component outline
            x1 = A/2 - B/2
            x2 = x1 + B
            y1 = -2.5 - 0.62
            y2 = y1 + 17.8
            
            #offset off
            off = 0.1
            
            x1 -= off
            y1 -= off
            x2 += off
            y2 += off
            
            #outline
            side = [
            {'x': -1,'y': y1},
            {'x': x1,'y': y1},
            {'x': x1,'y': y2},
            {'x': A/2,'y': y2},
            ]
            
            footprint.append(PolygoneLine(polygone=side))
            footprint.append(PolygoneLine(polygone=side,x_mirror=A/2))
            
            #courtyard
            cy = RectLine(start=[x1,y1],end=[x2,y2],offset=0.5,layer='F.CrtYd',width=0.05,grid=0.05)
            footprint.append(cy)
            
            #add mounting holes
            
            if pins == 3:
                m = Pad(at=[pitch,7],layers=["*.Cu","*.Mask"],shape=Pad.SHAPE_CIRCLE,type=Pad.TYPE_THT,size=3.4,drill=2)
                footprint.append(m)
            else:        
                m1 = Pad(at=[0,7],layers=["*.Cu",'*.Mask'],shape=Pad.SHAPE_CIRCLE,type=Pad.TYPE_THT,size=3.4, drill=2)
                m2 = Pad(at=[A,7],layers=["*.Cu",'*.Mask'],shape=Pad.SHAPE_CIRCLE,type=Pad.TYPE_THT,size=3.4, drill=2)
                
                footprint.append(m1)
                footprint.append(m2)
            
            #add p1 marker
            px = -3
            m = 0.3
            
            marker = [
            {'x': px,'y': 0},
            {'x': px-2*m,'y': m},
            {'x': px-2*m,'y': -m},
            {'x': px,'y': 0},
            ]
            
            footprint.append(PolygoneLine(polygone=marker))
            """
            #Add a model
            footprint.append(Model(filename="Connectors_Harwin.3dshapes/" + fp_name + ".wrl"))
            
            #filename
            filename = output_dir + fp_name + ".kicad_mod"
            
            file_handler = KicadFileHandler(footprint)
            file_handler.writeFile(filename)
