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

pincount = [3, 4, 6, 8, 10, 13, 17, 25]

name = "Harwin_Gecko-{pn}_2x{n:02}x{p:.2f}mm_Straight"

desc = "Harwin Gecko Connector, {pins} pins, dual row male, vertical entry, {latch}, PN:{pn}"

part = "G125-MVX{nn}05L{l}X"

tags = "connector harwin gecko"
#FP description and tags

if __name__ == '__main__':

    for latch in [True, False]:
        for pins in pincount:
                
            #calculate fp dimensions
            A = (pins - 1) * pitch
            
            n = pins * 2 #total pin count
            
            B = (n-2) * 0.625 + 3.8
            
            WIDTH = 4.9
            #outline
            x2 = A/2 + B/2
            x1 = x2 -  B
            
            ymid = -1 * (rows - 1) * pitch / 2
            y1 = ymid - WIDTH/2
            y2 = ymid + WIDTH/2
            
            pn = part.format(nn=2 * pins, l = "1" if latch else "0")
        
            #generate the name
            fp_name = name.format(n=pins, p=pitch, pn=pn)

            footprint = Footprint(fp_name)
            
            #set the FP description
            footprint.setDescription(desc.format(pins = pins * rows, pn=pn, latch="with latches" if latch else "no latches"))
            
            #set the FP tags
            footprint.setTags(tags)

            # set general values
            footprint.append(Text(type='reference', text='REF**', at=[A/2,3.5], layer='F.SilkS'))
            footprint.append(Text(type='value', text=fp_name, at=[A/2,-4.3], layer='F.Fab'))
                
            #generate the pads
            for i in range(rows):
                footprint.append(PadArray(pincount=pins, start=[0,-i*pitch], initial=(i+1), increment=rows, x_spacing=pitch, type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, size=pad_dia, drill=drill, layers=['*.Cu','*.Mask']))

            if latch:
                #mounting holes
                m = (n - 2) * 0.625 + 2.5
                footprint.append(Pad(at=[A/2 - m/2,ymid],size=[1.1,2],drill=[1,1.9],type=Pad.TYPE_NPTH, shape=Pad.SHAPE_OVAL, layers=["*.Cu"]))
                footprint.append(Pad(at=[A/2 + m/2,ymid],size=[1.1,2],drill=[1,1.9],type=Pad.TYPE_NPTH, shape=Pad.SHAPE_OVAL, layers=["*.Cu"]))
                
            #rough outline
            #corner radius
            r = 0.75
            footprint.append(Arc(center=[x1+r,y1+r],start=[x1,y1+r],angle=90))
            footprint.append(Arc(center=[x2-r,y1+r],start=[x2-r,y1],angle=90))
            footprint.append(Arc(center=[x2-r,y2-r],start=[x2,y2-r],angle=90))
            footprint.append(Arc(center=[x1+r,y2-r],start=[x1+r,y2],angle=90))
            
            #horizontal lines
            footprint.append(Line(start=[x1+r,y1],end=[x2-r,y1]))
            footprint.append(Line(start=[x1+r,y2],end=[x2-r,y2]))

            #inner outline
            #wall thickness T
            xa = x1 + 1
            xb = x2 - 1
            xm1 = A/2 - pitch/2
            xm2 = A/2 + pitch/2
            T = 0.7
            ya = y1 + T 
            yb = y2 - 0.4 
            yc = y1 + 0.4
            #corner radius R
            R = 0.25
            
            #draw the bottom line
            footprint.append(PolygoneLine(polygone=[
                {'x': xa+R,'y': yb},
                {'x': xa+pitch,'y': yb},
                {'x': xa+pitch,'y': y2 -  T},
                {'x': xb-pitch,'y': y2 -  T},
                {'x': xb-pitch,'y': yb},
                {'x': xb-R,'y': yb},
                ]))
                
            #left line
            #footprint.append(Line(start=[xa,ya+R],end=[xa,yb-R]))
            #right line
            #footprint.append(Line(start=[xb,ya+R],end=[xb,yb-R]))
            #top line
            footprint.append(PolygoneLine(polygone=[
                {'x': xa + R,'y': ya},
                {'x': xm1,'y': ya},
                {'x': xm1,'y': yc},
                {'x': xm2,'y': yc},
                {'x': xm2,'y': ya},
                {'x': xb - R,'y': ya},
                ]))
            #corners
            footprint.append(Arc(center=[xa+R,ya+R],start=[xa,ya+R],angle=90))
            footprint.append(Arc(center=[xb-R,ya+R],start=[xb-R,ya],angle=90))
            footprint.append(Arc(center=[xb-R,yb-R],start=[xb,yb-R],angle=90))
            footprint.append(Arc(center=[xa+R,yb-R],start=[xa+R,yb],angle=90))
            
            t = 1.5
            poly = [
                {'x': x1,'y': y1+r},
                {'x': x1,'y': ymid-t},
                {'x': xa,'y': ymid-t},
                {'x': xa,'y': ya+R},
                ]
            footprint.append(PolygoneLine(polygone=poly))
            footprint.append(PolygoneLine(polygone=poly, x_mirror=A/2))
            footprint.append(PolygoneLine(polygone=poly, y_mirror=ymid))
            footprint.append(PolygoneLine(polygone=poly, x_mirror=A/2))
            
            footprint.append(Line(start=[xa,yb-R],end=[xa,ymid+t]))
            footprint.append(Line(start=[xb,yb-R],end=[xb,ymid+t]))
            
            l = (n - 2) * 0.625 + 5.2
            if latch:
                ll = [
                    {'x': (x1 + xa) / 2, 'y': ymid-1.25},
                    {'x': (A/2 - l/2), 'y': ymid-1.25},
                    {'x': (A/2 - l/2), 'y': ymid+1.25},
                    {'x': (x1 + xa) / 2, 'y': ymid+1.25},
                    ]
                footprint.append(PolygoneLine(polygone=ll))
                footprint.append(PolygoneLine(polygone=ll, x_mirror=A/2))
            
            #courtyard
            if latch: #latches increase the courtyard
                x1 = A/2 - l/2
                x2 = A/2 + l/2
            footprint.append(RectLine(start=[x1,y1],end=[x2,y2],offset=0.5,grid=0.05,width=0.05,layer='F.CrtYd'))

            
            #add p1 marker
            px = 0
            py = 2.1
            m = 0.3
            
            marker = [
                {'x': px,'y': py},
                {'x': px-m,'y': py+2*m},
                {'x': px+m,'y': py+2*m},
                {'x': px,'y': py},
            ]
            
            footprint.append(PolygoneLine(polygone=marker))
            #Add a model
            footprint.append(Model(filename="Connectors_Harwin.3dshapes/" + fp_name + ".wrl"))
            
            #filename
            filename = output_dir + fp_name + ".kicad_mod"
            
            file_handler = KicadFileHandler(footprint)
            file_handler.writeFile(filename)
