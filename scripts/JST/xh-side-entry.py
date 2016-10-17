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
_3dshapes = "Connectors_JST.3dshapes"+os.sep
ref_on_ffab = False
fab_line_width = 0.1
silk_line_width = 0.15
value_fontsize = [1,1]
value_fontwidth=0.15
silk_reference_fontsize=[1,1]
silk_reference_fontwidth=0.15
fab_reference_fontsize=[0.6,0.6]
fab_reference_fontwidth=0.1

CrtYd_offset = 0.5
CrtYd_linewidth = 0.05

pin1_marker_offset = 0.3
pin1_marker_linelen = 1.25
fab_pin1_marker_type = 1

#if specified as an argument, extract the target directory for output footprints
if len(sys.argv) > 1:
    out_dir = sys.argv[1]
    if out_dir.endswith(".pretty"):
        out_dir += os.sep
    if not out_dir.endswith(".pretty"+os.sep):
        out_dir += ".pretty"+os.sep

    if os.path.isabs(out_dir) and os.path.isdir(out_dir):
        output_dir = out_dir
    else:
        output_dir = os.path.join(os.getcwd(),out_dir)

if len(sys.argv) > 2:
    if sys.argv[2] == "TERA":
        ref_on_ffab = True
        fab_line_width = 0.05
        silk_line_width = 0.15
        _3dshapes = "tera_Connectors_JST.3dshapes"+os.sep
        value_fontsize = [0.6,0.6]
        value_fontwidth = 0.1
        fab_pin1_marker_type = 2
    else:
        _3dshapes = sys.argv[2]
        if _3dshapes.endswith(".3dshapes"):
            _3dshapes += os.sep
        if not _3dshapes.endswith(".3dshapes"+os.sep):
            _3dshapes += ".3dshapes"+os.sep

if output_dir and not output_dir.endswith(os.sep):
    output_dir += os.sep

if not os.path.isdir(output_dir): #returns false if path does not yet exist!! (Does not check path validity)
    os.makedirs(output_dir)

#import KicadModTree files
# export PYTHONPATH="${PYTHONPATH}<path to kicad-footprint-generator directory>"
sys.path.append("..\\..")
from KicadModTree import *
from KicadModTree.nodes.specialized.PadArray import PadArray

"""
footprint specific details to go here

Datasheet: http://www.jst-mfg.com/product/pdf/eng/eXH.pdf

"""
pitch = 2.50
boss = True

variants = ["A"]#,"A-1"]

#FP name strings
part_base = "S{n:02}B-XH-" #JST part number format string

prefix = "JST_XH_"
suffix = "_{n:02}x{p:.2f}mm_Angled"

fab_first_marker_w = 1.25
fab_first_marker_h = 1

#FP description and tags

if __name__ == '__main__':

    for variant in variants:
        #variant offset V
        V = 0
        if variant is "A-1":
            pincount = range(2,16)
            V = 7.6
        else:
            pincount = range(2,17)
            V = 9.2
        for pins in pincount:


            #calculate fp dimensions
            A = (pins - 1) * pitch
            B = A + 4.9

            #Thickness of connector
            T = 11.5

            #corners
            x1 = -2.45
            x2 = x1 + B

            x_mid = (x1 + x2) / 2

            y2 = V
            y1= y2 - T


            #y at which the plastic tabs end
            y3 = y2 - 7

            #generate the name
            part = part_base + variant
            fp_name = prefix + part.format(n=pins) + suffix.format(n=pins, p=pitch)

            print(fp_name)
            footprint = Footprint(fp_name)

            description = "JST XH series connector, " + part.format(n=pins) + ", side entry type, through hole"

            #set the FP description
            footprint.setDescription(description)

            tags = "connector jst xh tht side horizontal angled 2.50mm"

            #set the FP tags
            footprint.setTags(tags)

            # set general values
            #footprint.append(Text(type='reference', text='REF**', at=[x_mid,-3.5], layer='F.SilkS'))

            ref_pos_1=[x_mid,-3.5]
            ref_pos_2=[x_mid,4]
            footprint.append(Text(type='reference', text='REF**', layer=('F.Fab' if ref_on_ffab else'F.SilkS'),
                at=(ref_pos_2 if ref_on_ffab else ref_pos_1)))
            if ref_on_ffab:
                footprint.append(Text(type='user', text='%R', at=ref_pos_1, layer='F.SilkS'))

            footprint.append(Text(type='value', text=fp_name, at=[x_mid,y2 + 1.1], layer='F.Fab'))

            #draw simple outline on F.Fab layer
            footprint.append(RectLine(start=[x1,y1],end=[x2,y2],layer='F.Fab', width=fab_line_width))

            drill = 0.9

            #generate the pads
            pa = PadArray(pincount=pins, x_spacing=pitch, type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, size=1.75, drill=drill, layers=['*.Cu','*.Mask','F.SilkS'])

            footprint.append(pa)

            #draw the courtyard
            cy = RectLine(start=[x1,y1],end=[x2,y2],layer='F.CrtYd',width=0.05,offset = 0.5)
            footprint.append(cy)

            #offset the outline around the connector
            off = 0.15

            xo1 = x1 - off
            yo1 = y1 - off

            xo2 = x2 + off
            yo2 = y2 + off

            #thickness of the notches
            notch = 1.5

            #wall thickness of the outline
            wall = 1.2

            #draw the outline of the connector
            outline = [
            {'x': x_mid,'y': yo2},
            {'x': xo1,'y': yo2},
            {'x': xo1,'y': yo1},
            {'x': xo1+wall,'y': yo1},
            {'x': xo1+wall,'y': y3 - off},
            {'x': A/2,'y': y3 - off},
            #{'x': -1.1,'y': y3 + off}
            ]

            footprint.append(PolygoneLine(polygone = outline))
            footprint.append(PolygoneLine(polygone = outline,x_mirror=x_mid))

            #draw the pinsss
            for i in range(pins):

                x = i * pitch
                w = 0.25
                footprint.append(RectLine(start=[x-w,y3+0.5],end=[x+w,y2-0.5]))

            #add pin-1 designator
            px = 0
            py = -1.5
            m = 0.3

            pin1 = [
            {'x': px,'y': py},
            {'x': px-m,'y': py-2*m},
            {'x': px+m,'y': py-2*m},
            {'x': px,'y': py},
            ]

            footprint.append(PolygoneLine(polygone=pin1))
            if fab_pin1_marker_type == 1:
                footprint.append(PolygoneLine(polygone=pin1,layer='F.Fab'))

            if fab_pin1_marker_type == 2:
                fab_marker_left = -fab_first_marker_w/2.0
                fab_marker_bottom = y1 + fab_first_marker_h
                poly_fab_marker = [
                    {'x':fab_marker_left, 'y':y1},
                    {'x':0, 'y':fab_marker_bottom},
                    {'x':fab_marker_left + fab_first_marker_w, 'y':y1}
                ]
                footprint.append(PolygoneLine(polygone=poly_fab_marker, layer='F.Fab', width=fab_line_width))
            #Add a model
            footprint.append(Model(filename=_3dshapes + fp_name + ".wrl"))

            #filename
            filename = output_dir + fp_name + ".kicad_mod"


            file_handler = KicadFileHandler(footprint)
            file_handler.writeFile(filename)
