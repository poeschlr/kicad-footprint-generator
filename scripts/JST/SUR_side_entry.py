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

#parser = argparse.ArgumentParser()
#parser.add_argument('pincount', help='number of pins of the jst connector', type=int, nargs=1)
#parser.add_argument('-v', '--verbose', help='show extra information while generating the footprint', action='store_true') #TODO
#args = parser.parse_args()

# http://www.jst-mfg.com/product/pdf/eng/eSHL.pdf

#pincount = int(args.pincount[0])

pitch = 0.8
pad_w = 0.5
pad_h = 1.0

for pincount in [2,3,4,5,6,8,10,12,14,15,16,17,20,22]:


    A = (pincount - 1) * pitch
    B = A + 3

    jst_name = "SM{pincount:02}B-SURS-TF".format(pincount=pincount)

    # SMT type shrouded header, Side entry type (normal type)
    fp_name = "JST_SUR_" + jst_name + "_{pincount:02}x{pitch:.2f}mm_Angled".format(pincount=pincount,pitch=pitch)

    fp = Footprint(fp_name)
    fp.setDescription("JST SUR series connector, " + jst_name + ", side entry, 0.80mm pitch") 
    fp.setAttribute('smd')
    fp.setTags('connector jst SUR SMT side horizontal entry 0.80mm pitch')

    #y values of pads
    #mechanical pads
    ym = 1.7 / 2
    #circuit pads
    yc = 2.3 + 0.5
    #middle
    ymiddle = (ym + yc) / 2
    
    #offset from the middle!
    YP = (ymiddle - ym)
    
    # set general values
    fp.append(Text(type='reference', text='REF**', at=[0,-3.2], layer='F.SilkS'))
    fp.append(Text(type='value', text=fp_name, at=[0,3], layer='F.Fab'))

    #create outline
    # create Courtyard
    # output kicad model
    
    layers=["F.Cu","F.Mask","F.Paste"]
    
    #add the pads!
    fp.append(PadArray(pincount=pincount, x_spacing=pitch, type=Pad.TYPE_SMT, shape=Pad.SHAPE_RECT, size=[pad_w,pad_h], center=[0,-YP], layers=layers))
    
    #add mechanical pad
    MX = A/2 + 0.7 + 1.2 / 2
    mw = 1.2
    mh = 1.7
    
    fp.append(Pad(at=[MX,YP],type=Pad.TYPE_SMT, shape=Pad.SHAPE_RECT, size=[mw,mh],layers=layers))
    fp.append(Pad(at=[-MX,YP],type=Pad.TYPE_SMT, shape=Pad.SHAPE_RECT, size=[mw,mh],layers=layers))

    #draw the bottom line
    xb = MX - mw / 2 - 0.3
    yb = YP + mh / 2 - 0.25
    
    fp.append(Line(start=[-xb,yb],end=[xb,yb]))
    
    #draw the outside line
    #offset from pads o
    o = 0.3
    
    y1 = yb - 2.7 - 0.2
    y2 = y1 + 0.3
    
    x1 = A/2 + pad_w/2 + o
    
    right = [
    {'x': x1,'y': y1},
    {'x': x1 + 0.3,'y': y1},
    {'x': x1 + 0.3,'y': y2},
    {'x': B/2 + 0.1,'y': y2},
    {'x': B/2 + 0.1,'y': YP - mh/2 - o},
    ]
    
    fp.append(PolygoneLine(polygone=right))
    fp.append(PolygoneLine(polygone=right,x_mirror=0))
    
    #add pin-1 mark
    mx = -A/2
    my = -1.9
    m = 0.25
    
    arrow = [
    {'x': mx,'y': my},
    {'x': mx-m,'y': my-2*m},
    {'x': mx+m,'y': my-2*m},
    {'x': mx,'y': my},
    ]
    
    fp.append(PolygoneLine(polygone=arrow))
    
    #add a courtyard
    cx = -MX - mw/2 - 0.5
    cy1 = -YP -pad_h/2 - 0.5
    cy2 = YP + mh/2 + 0.5
    
    fp.append(RectLine(start=[-cx,cy1],end=[cx,cy2],width=0.05,layer="F.CrtYd",grid=0.05))
    
    #Add a model
    fp.append(Model(filename="Connectors_JST.3dshapes/" + fp_name + ".wrl"))
    
    #filename
    filename = output_dir + fp_name + ".kicad_mod"
    
    file_handler = KicadFileHandler(fp)
    file_handler.writeFile(filename)