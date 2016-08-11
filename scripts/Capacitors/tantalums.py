"""
Tantalum Capacitors

References:
http://www.dialelectrolux.ru/files/file/Kemet/f3102.pdf
https://en.wikipedia.org/wiki/Tantalum_capacitor#Chip_capacitors_.28case_size.29
#

"""

#Reflow-soldering dimensions
#[Z, G, X]
rR = [3.9, 0.8, 1.8]
rA = rS = [4.7, 0.8, 1.5]
rB = rT = [5.0, 1.1, 2.5]
rC = rU = [7.6, 2.5, 2.5]
rD = rV = rX = [8.9, 3.8, 2.7]
rE = [8.9, 3.8, 4.4]

#Wave-soldering dimensions
#[Z, G, X]
wR = [4.3, 0.8, 1.26]
wA = wS = [5.1, 0.8, 1.1]
wB = wT = [5.4, 1.1, 1.8]
wC = wU = [8.0, 2.5, 1.8]
wD = wV = wX = [9.7, 3.8, 2.7]
wE = [9.7, 3.8, 4.4]

# Designator, EIA, L, W, H, [Zr, Gr, Xr], [Zw, Gw, Xr]
caps = [
['A', '3216-18', 3.2, 1.6, 1.6, rA, wA],
['B', '3528-21', 3.5, 2.8, 1.9, rB, wB],
['C', '6032-28', 6.0, 3.2, 2.5, rC, wC],
['D', '7343-31', 7.3, 4.3, 2.8, rD, wD],
['E', '7260-38', 7.3, 6.0, 3.6, rE, wE],
['X', '7343-43', 7.3, 4.2, 4.0, rX, wX],
['R', '2012-12', 2.0, 1.3, 1.2, rR, wR],
['S', '3216-12', 3.2, 1.6, 1.2, rS, wS],
['T', '3528-12', 3.5, 2.8, 1.2, rT, wT],
['U', '6032-15', 6.0, 3.2, 1.5, rU, wU],
['V', '7343-20', 7.3, 4.3, 2.0, rV, wV],
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

prefix = "Tantalum_Case-{case}_EIA-{eia}"
suffix = "_{pattern}"

name = prefix + suffix

desc = "Tantalum calacitor, Case {case}, EIA {eia}, {l}x{w}x{h}mm, {pattern} soldering footprint"
tags = "capacitor tantalum smd"

HAND_SOLDER_SIZE = 2

for cap in caps:
    
    #extract information
    case, eia, l, w, h, reflow, wave = cap
    
    #calculate the hand-soldering values
    #based on the reflow soldering
    
    z,g,x = reflow
    z = l + 2 * HAND_SOLDER_SIZE
    
    #various patterns to generate
    patterns = {
    'Reflow' : reflow,
    'Wave' : wave,
    'Hand' : [z,g,x]
    }
    
    for pattern_name in patterns.keys():
        fp_name = name.format(
            case = case,
            eia  = eia,
            pattern = pattern_name)
            
        fp_description = desc.format(
            case = case,
            eia  = eia,
            l    = l,
            w    = w,
            h    = h,
            pattern = pattern_name)
            
        print(fp_name)
            
        pattern = patterns[pattern_name]
        
        #extract the pattern information
        Z, G, X = pattern
        
        #Make the footprint
        fp = Footprint(fp_name)
        fp.setAttribute('smd')
        fp.setDescription(fp_description)
        fp.setTags(tags)
        
        #set the general values
        fp.append(Text(type='reference', text='REF**', at=[0,-w/2 - 1], layer='F.SilkS'))
        fp.append(Text(type='value', text=fp_name, at=[0,w/2 + 1.5], layer='F.Fab'))
    
        #draw the courtyard
        cy = max(w/2, X/2)
        fp.append(RectLine(start=[-Z/2, -cy], end=[Z/2, cy], width=0.05, layer='F.CrtYd', grid=0.05, offset=0.4))
        
        #draw the cap outline
        fp.append(RectLine(start=[-l/2,-w/2],end=[l/2,w/2],layer='F.Fab'))
        
        #F.Fab polarization
        fx1 = -0.40 * l
        fx2 = -0.35 * l
        fp.append(Line(start=[fx1,-w/2],end=[fx1,w/2],layer='F.Fab'))
        fp.append(Line(start=[fx2,-w/2],end=[fx2,w/2],layer='F.Fab'))
        
        #draw the pads
        px = (G + Z) / 4
        layers = ["F.Cu","F.Paste","F.Mask"]
        fp.append(Pad(number=1, size=[(Z-G)/2,X], at=[-px, 0],layers=layers,shape=Pad.SHAPE_RECT,type=Pad.TYPE_SMT))
        fp.append(Pad(number=2, size=[(Z-G)/2,X], at=[px, 0],layers=layers,shape=Pad.SHAPE_RECT,type=Pad.TYPE_SMT))
        
        #silkscreen it up like a boss
        fp.append(Line(start=[0.25*l,-cy-0.2],end=[-Z/2,-cy-0.2]))
        fp.append(Line(start=[0.25*l,+cy+0.2],end=[-Z/2,+cy+0.2]))
        #fp.append(Line(start=[-Z/2 - 0.2, -0.75 * cy], end=[-Z/2 - 0.2, 0.75 * cy]))
        
        #Add a model
        model_name = prefix.format(case = case, eia = eia)
        fp.append(Model(filename="Capacitors_Tantalum_SMD.3dshapes/" + model_name + ".wrl"))
        
        #filename
        filename = output_dir + fp_name + ".kicad_mod"
        
        file_handler = KicadFileHandler(fp)
        file_handler.writeFile(filename)
        
    
    """
    #calculate pad center
    #pad-width pw
    pw = (x-g) / 2
    c = g/2 + pw/2
    
    #add the component outline
    fp.append(RectLine(start=[-l/2,-w/2],end=[l/2,w/2],layer='F.Fab',width=0.15))
    
    
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
    
    """
    