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
"""
pitch = 1.25

row_pitch = 1.25

drill = 0.55

pad_dia = 0.95

rows = 2

pincount = [3, 5, 6, 8, 10, 13, 17, 25]

name = "Harwin_Gecko-{pn}_2x{n:02}x{p:.2f}mm_Straight"

desc = "Harwin Gecko Connector, {pins} pins, dual row female, vertical entry, PN:{pn}"

part = "G125-FVX{nn:02}05L0X"

tags = "connector harwin gecko"
#FP description and tags

if __name__ == '__main__':

    
    for pins in pincount:
            
        #calculate fp dimensions
        A = (pins - 1) * pitch
        
        n = pins * 2 #total pin count
        
        B = (n-2) * 0.625 + 3.8
        
        WIDTH = 4.9
        #outline
        x2 = A/2 + B/2
        x1 = x2 -  B
        
        ymid = (rows - 1) * pitch / 2
        y1 = ymid - WIDTH/2
        y2 = ymid + WIDTH/2
        
        pn = part.format(nn=2 * pins)
    
        #generate the name
        fp_name = name.format(n=pins, p=pitch, pn=pn)

        footprint = Footprint(fp_name)
        
        
        #set the FP description
        footprint.setDescription(desc.format(pins = pins * rows, pn=pn))
        
        #set the FP tags
        footprint.setTags(tags)

        # set general values
        footprint.append(Text(type='reference', text='REF**', at=[A/2,4.3], layer='F.SilkS'))
        footprint.append(Text(type='value', text=fp_name, at=[A/2,-3.5], layer='F.Fab'))
            
        #generate the pads (row 1)
        for i in range(rows):
            footprint.append(PadArray(pincount=pins, start=[0,i*pitch], initial=(i+1), increment=rows, x_spacing=pitch, type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, size=pad_dia, drill=drill, layers=['*.Cu','*.Mask']))

        #rough outline
        #corner radius
        r = 0.75
        footprint.append(Arc(center=[x1+r,y1+r],start=[x1,y1+r],angle=90))
        footprint.append(Arc(center=[x2-r,y1+r],start=[x2-r,y1],angle=90))
        footprint.append(Arc(center=[x2-r,y2-r],start=[x2,y2-r],angle=90))
        footprint.append(Arc(center=[x1+r,y2-r],start=[x1+r,y2],angle=90))
        
        footprint.append(Line(start=[x1+r,y1],end=[x2-r,y1]))
        footprint.append(Line(start=[x1+r,y2],end=[x2-r,y2]))
        
        footprint.append(Line(start=[x1,y1+r],end=[x1,y2-r]))
        footprint.append(Line(start=[x2,y1+r],end=[x2,y2-r]))
        
        #inner outline
        #wall thickness T
        xa = x1 + 1
        xb = x2 - 1
        xm1 = A/2 - pitch/2
        xm2 = A/2 + pitch/2
        T = 0.9
        ya = y1 + 0.5
        yb = y2 - T 
        yc = y2 - 0.5
        #corner radius R
        R = 0.25
        
        #draw the top line
        footprint.append(PolygoneLine(polygone=[
            {'x': xa+R,'y': ya},
            {'x': xa+pitch,'y': ya},
            {'x': xa+pitch,'y': y1 + T},
            {'x': xb-pitch,'y': y1 + T},
            {'x': xb-pitch,'y': ya},
            {'x': xb-R,'y': ya},
            ]))
            
        #left line
        footprint.append(Line(start=[xa,ya+R],end=[xa,yb-R]))
        #right line
        footprint.append(Line(start=[xb,ya+R],end=[xb,yb-R]))
        #bottom line
        footprint.append(PolygoneLine(polygone=[
            {'x': xa + R,'y': yb},
            {'x': xm1,'y': yb},
            {'x': xm1,'y': yc},
            {'x': xm2,'y': yc},
            {'x': xm2,'y': yb},
            {'x': xb - R,'y': yb},
            ]))
        #corners
        footprint.append(Arc(center=[xa+R,ya+R],start=[xa,ya+R],angle=90))
        footprint.append(Arc(center=[xb-R,ya+R],start=[xb-R,ya],angle=90))
        footprint.append(Arc(center=[xb-R,yb-R],start=[xb,yb-R],angle=90))
        footprint.append(Arc(center=[xa+R,yb-R],start=[xa+R,yb],angle=90))
        
        #courtyard
        footprint.append(RectLine(start=[x1,y1],end=[x2,y2],offset=0.5,grid=0.05,width=0.05,layer='F.CrtYd'))

        
        #add p1 marker
        px = 0
        py = -2.1
        m = 0.3
        
        marker = [
            {'x': px,'y': py},
            {'x': px-m,'y': py-2*m},
            {'x': px+m,'y': py-2*m},
            {'x': px,'y': py},
        ]
        
        footprint.append(PolygoneLine(polygone=marker))
        #Add a model
        footprint.append(Model(filename="Connectors_Harwin.3dshapes/" + fp_name + ".wrl"))
        
        #filename
        filename = output_dir + fp_name + ".kicad_mod"
        
        file_handler = KicadFileHandler(footprint)
        file_handler.writeFile(filename)
