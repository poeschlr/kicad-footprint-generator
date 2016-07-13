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

JAE LY series vertical entry dual row
Datasheet: http://www.jae.com/z-en/pdf_download_exec.cfm?param=SJ103130.pdf
"""

datasheet = "http://www.jae.com/z-en/pdf_download_exec.cfm?param=SJ103130.pdf"

#pins per row (4 -> 44 pins total)
pincount = range(2,23)

#JAE part numbers
code = "LY20-{n:02}P-2T"

#part description format strings
part_name = "JAE_{pn}_2x{n:02}x{p:.2f}mm_Straight"
part_description = "JAE LY series connector, dual row top entry, through hole, Datasheet:{ds}".format(ds=datasheet)
part_tags = "connector jae ly"

#connector pitch
pitch = 2.00
#spacing between rows
row = 2.0

#drill size
drill = 0.8
#pad size
size = 1.35

#FP description and tags

if __name__ == '__main__':
    
    for pins in pincount:
        
        pn = code.format(n=pins*2)
        
        #generate the name
        fp_name = part_name.format(
            pn = pn,
            n=pins,
            p=pitch)
            
        footprint = Footprint(fp_name)
        
        print(fp_name)
        
        #set the FP description
        footprint.setDescription(part_description)
        
        tags = part_tags + " " + pn
        
        #set the FP tags
        footprint.setTags(tags)
        
        #E = connector length
        E = pins * pitch + 1.6
        
        #A = Distance between end pins
        A = (pins - 1) * pitch
        
        #W = thickness of plastic base
        W = 5.3
        
        #corner positions for plastic housing outline
        x1 = -(E-A)/2
        x2 = x1 + E
        
        y2 = (W - pitch) / 2
        y1 = y2 - W

        # set general values
        footprint.append(Text(type='reference', text='REF**', at=[A/2,-5], layer='F.SilkS'))
        footprint.append(Text(type='value', text=fp_name, at=[A/2,3.5], layer='F.Fab'))
            
        #generate the pads (two rows)
        for r in range(2):
            footprint.append(PadArray(pincount=pins, initial=r*pins+1, start=[0,-r*row], x_spacing=pitch, type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, size=size, drill=drill, layers=['*.Cu','*.Mask']))
        
        #add outline to F.Fab
        footprint.append(RectLine(start=[x1,y1],end=[x2,y2],layer='F.Fab',width=0.05))
        
        #add the courtyard
        footprint.append(RectLine(start=[x1,y1],end=[x2,y2],layer='F.CrtYd',width=0.05,offset=0.5,grid=0.05))
        
        #add the silk-screen
        footprint.append(RectLine(start=[x1,y1],end=[x2,y2],offset=0.1))
        
        #add the inner silk-screen
        if pins < 6:
            footprint.append(RectLine(start=[x1,y1],end=[x2,y2],offset=-0.5))
        else:
            B = A - 8
            
            poly = [
                {'x': A/2-B/2,'y': y2},
                {'x': A/2-B/2,'y': y2 - 0.5},
                {'x': x1 + 0.5,'y': y2 - 0.5},
                {'x': x1 + 0.5,'y': y1 +  0.5},
                {'x': A/2 - B/2,'y': y1 +  0.5},
                {'x': A/2 - B/2,'y': y1},
            ]
            
            footprint.append(PolygoneLine(polygone=poly))
            footprint.append(PolygoneLine(polygone=poly, x_mirror=A/2))
        
        #pin-1 marker
        x = 0
        y = 2
        m = 0.3
        
        pin = [
        {'x': x,'y': y},
        {'x': x-m,'y': y+2*m},
        {'x': x+m,'y': y+2*m},
        {'x': x,'y': y},
        ]
        
        footprint.append(PolygoneLine(polygone=pin))

        #Add a model
        footprint.append(Model(filename="Connectors_JAE.3dshapes/" + fp_name + ".wrl"))
        
        #filename
        filename = output_dir + fp_name + ".kicad_mod"

        file_handler = KicadFileHandler(footprint)
        file_handler.writeFile(filename)
