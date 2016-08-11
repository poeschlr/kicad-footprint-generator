# Tantalum Capacitors
#https://en.wikipedia.org/wiki/Tantalum_capacitor#Chip_capacitors_.28case_size.29

#AVX Datasheet
# http://akizukidenshi.com/download/ds/avx/AVX_datasheet.pdf

#Kemet Datasheet (use this as master reference)
# https://www.pa.msu.edu/hep/d0/ftp/run2b/l1cal/hardware/component_information/kemet_tant_and_ceramic_caps.pdfs

# Tantalum capacitor specifications
# EIAcode (metric) -> L -> W -> H -> EIAcode (inches) -> AVX code -> Kemet code
caps = [
"""
["1608-08",1.6,0.8,0.8,0603,"—","—"],
["1608-10",1.6,0.85,1.05,0603,"L","—"],
["2012-12",2.05,1.35,1.2,0805,"R","R"],
["2012-15",2.05,1.35,1.5,0805,"P","—"],
["3216-10",3.2,1.6,1.0,1206,"K","I"],
["3216-12",3.2,1.6,1.2,1206,"S","S"],
["3216-18",3.2,1.6,1.8,1206,"A","A"],
["3528-12",3.5,2.8,1.2,1210,"T","T"],
["3528-15",3.5,2.8,1.5,1210,"H","—"],
["3528-21",3.5,2.8,2.1,1210,"B","B"],
["6032-15",6.0,3.2,1.5,2312,"W","U"],
["6032-20",6.0,3.2,2.0,2312,"F","—"],
["6032-28",6.0,3.2,2.8,2312,"C","C"],
["7343-15",7.3,4.3,1.5,2917,"X","W"],
["7343-20",7.3,4.3,2.0,2917,"Y","V"],
["7343-30",7.3,4.3,3.0,2917,"N","—"],
["7343-31",7.3,4.3,3.1,2917,"D","D"],
["7343-40",7.3,4.3,4.0,2917,"—","Y"],
["7343-43",7,3,4.3,4.3,2917,"E","X"],
["7360-38",7.3,6.0,3.8,2623,"—","E"],
["7361-38",7.3,6.1,3.8,2924,"V","—"],
["7361-438",7.3,6.1,4.3,2924,"U","—"]
"""
]

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

prefix = "Tantalum_"
part = "Wurth_MAPI-{pn}"
dims = "{l:0.1f}mmx{w:0.1f}mm"

desc = "Inductor, Wurth Elektronik, {pn}"
tags = "inductor wurth smd"

for inductor in inductors:
    name,l,w,x,g,y = inductor
    
    fp_name = prefix + part.format(pn=str(name))
    
    fp = Footprint(fp_name)
    
    description = desc.format(pn = part.format(pn=str(name))) + ", " + dims.format(l=l,w=w)
    
    fp.setTags(tags)
    fp.setAttribute("smd")
    fp.setDescription(description)
    
    # set general values
    fp.append(Text(type='reference', text='REF**', at=[0,-y/2 - 1], layer='F.SilkS'))
    fp.append(Text(type='value', text=fp_name, at=[0,y/2 + 1.5], layer='F.Fab'))
    
    #calculate pad center
    #pad-width pw
    pw = (x-g) / 2
    c = g/2 + pw/2
    
    #add the component outline
    fp.append(RectLine(start=[-l/2,-w/2],end=[l/2,w/2],layer='F.Fab',width=0.15))
    
    layers = ["F.Cu","F.Paste","F.Mask"]
    
    #add pads
    fp.append(Pad(number=1,at=[-c,0],layers=layers,shape=Pad.SHAPE_RECT,type=Pad.TYPE_SMT,size=[pw,y]))
    fp.append(Pad(number=2,at=[c,0],layers=layers,shape=Pad.SHAPE_RECT,type=Pad.TYPE_SMT,size=[pw,y]))
    
    #add inductor courtyard
    cx = c + pw/2
    cy = y / 2
    
    fp.append(RectLine(start=[-cx,-cy],end=[cx,cy],offset=0.35,width=0.05,grid=0.05,layer="F.CrtYd"))
    
    #add lines
    fp.append(Line(start=[-g/2+0.2,-w/2-0.1],end=[g/2-0.2,-w/2-0.1]))
    fp.append(Line(start=[-g/2+0.2,w/2+0.1],end=[g/2-0.2,w/2+0.1]))
    
    #Add a model
    fp.append(Model(filename="Inductors.3dshapes/" + fp_name + ".wrl"))
    
    #filename
    filename = output_dir + fp_name + ".kicad_mod"
    
    file_handler = KicadFileHandler(fp)
    file_handler.writeFile(filename)
    