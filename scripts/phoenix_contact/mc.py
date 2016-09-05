#!/usr/bin/env python

import sys
import os
from helpers import *
from global_params import *

sys.path.append(os.path.join(sys.path[0],"..","..")) # load KicadModTree path
from KicadModTree import *

from mc_params import seriesParams, dimensions, generate_description, all_params

def generate_one_footprint(motel, params, with_fabLayer=False):

    # Through-hole type shrouded header, Top entry type
    footprint_name = params.file_name

    calc_dim = dimensions(params)

    body_top_left=[calc_dim.left_to_pin,params.back_to_pin]
    body_bottom_right=v_add(body_top_left,[calc_dim.length,calc_dim.width])
    silk_top_left=v_offset(body_top_left, globalParams.silk_body_offset)
    silk_bottom_right=v_offset(body_bottom_right, globalParams.silk_body_offset)
    center_x = (params.num_pins-1)/2.0*params.pin_pitch
    kicad_mod = Footprint(footprint_name)


    kicad_mod.setDescription(generate_description(params))
    kicad_mod.setTags(manufacturer_tag + model)

    #add the pads
    kicad_mod.append(Pad(number=1, type=Pad.TYPE_THT, shape=Pad.SHAPE_RECT,
                        at=[0, 0], size=[seriesParams.pin_Sx, seriesParams.pin_Sy], \
                        drill=seriesParams.drill, layers=globalParams.pin_layers))
    for p in range(1,params.num_pins):
        Y = 0
        X = p * params.pin_pitch

        num = p+1
        kicad_mod.append(Pad(number=num, type=Pad.TYPE_THT, shape=Pad.SHAPE_OVAL,
                            at=[X, Y], size=[seriesParams.pin_Sx, seriesParams.pin_Sy], \
                            drill=seriesParams.drill, layers=globalParams.pin_layers))
    if params.mount_hole:
        kicad_mod.append(Pad(number='""', type=Pad.TYPE_NPTH, shape=Pad.SHAPE_CIRCLE,
                            at=calc_dim.mount_hole_left, size=[seriesParams.mount_drill, seriesParams.mount_drill], \
                            drill=seriesParams.mount_drill, layers=globalParams.mount_hole_layers))
        kicad_mod.append(Pad(number='""', type=Pad.TYPE_NPTH, shape=Pad.SHAPE_CIRCLE,
                            at=calc_dim.mount_hole_right, size=[seriesParams.mount_drill, seriesParams.mount_drill], \
                            drill=seriesParams.mount_drill, layers=globalParams.mount_hole_layers))
    #add an outline around the pins

    # create silscreen


    if params.angled:
        #kicad_mod.append(RectLine(start=silk_top_left, end=silk_bottom_right, layer='F.SilkS'))

        kicad_mod.append(Line(start=silk_top_left, end=[silk_top_left[0], silk_bottom_right[1]], layer='F.SilkS'))
        kicad_mod.append(Line(start=[silk_top_left[0], silk_bottom_right[1]], end=silk_bottom_right, layer='F.SilkS'))
        kicad_mod.append(Line(start=silk_bottom_right, end=[silk_bottom_right[0], silk_top_left[1]], layer='F.SilkS'))

        kicad_mod.append(Line(start=silk_top_left, end=[-seriesParams.silkGab, silk_top_left[1]], layer='F.SilkS'))
        kicad_mod.append(Line(start=[silk_bottom_right[0], silk_top_left[1]], end=[(params.num_pins-1)*params.pin_pitch+seriesParams.silkGab, silk_top_left[1]],\
                        layer='F.SilkS'))

        for p in range(params.num_pins-1):
            kicad_mod.append(Line(start=[p*params.pin_pitch+seriesParams.silkGab, silk_top_left[1]], \
                            end=[(p+1)*params.pin_pitch-seriesParams.silkGab, silk_top_left[1]], layer='F.SilkS'))

        if with_fabLayer:
            kicad_mod.append(RectLine(start=body_top_left, end=body_bottom_right, layer='F.Fab', width=globalParams.fab_line_width))

        left = silk_top_left[0] + (seriesParams.flange_lenght if params.flanged else 0)
        right = silk_bottom_right[0] - (seriesParams.flange_lenght if params.flanged else 0)
        scoreline_y = seriesParams.scoreline_from_back+params.back_to_pin
        kicad_mod.append(Line(start=[left, scoreline_y], end=[right, scoreline_y], layer='F.SilkS'))
        if with_fabLayer:
            kicad_mod.append(Line(start=[left +(0 if params.flanged else globalParams.silk_body_offset), scoreline_y],
                end=[right-(0 if params.flanged else globalParams.silk_body_offset), scoreline_y], layer='F.Fab', width=globalParams.fab_line_width))
        if params.flanged:
            kicad_mod.append(Line(start=[left, silk_top_left[1]], end=[left, silk_bottom_right[1]], layer='F.SilkS'))
            kicad_mod.append(Line(start=[right, silk_top_left[1]], end=[right, silk_bottom_right[1]], layer='F.SilkS'))
            if with_fabLayer:
                kicad_mod.append(Line(start=[left, body_top_left[1]], end=[left, body_bottom_right[1]], layer='F.Fab', width=globalParams.fab_line_width))
                kicad_mod.append(Line(start=[right, body_top_left[1]], end=[right, body_bottom_right[1]], layer='F.Fab', width=globalParams.fab_line_width))
    else:
        if not params.flanged:
            kicad_mod.append(RectLine(start=silk_top_left, end=silk_bottom_right, layer='F.SilkS'))
            if with_fabLayer:
                kicad_mod.append(RectLine(start=body_top_left, end=body_bottom_right, layer='F.Fab', width=globalParams.fab_line_width))
        else:
            flange_cutout = calc_dim.width-calc_dim.flange_width
            outline_poly=[
                    {'x':silk_top_left[0], 'y':silk_bottom_right[1]},
                    {'x':silk_bottom_right[0], 'y':silk_bottom_right[1]},
                    {'x':silk_bottom_right[0], 'y':silk_top_left[1]+flange_cutout},
                    {'x':silk_bottom_right[0]-seriesParams.flange_lenght, 'y':silk_top_left[1]+flange_cutout},
                    {'x':silk_bottom_right[0]-seriesParams.flange_lenght, 'y':silk_top_left[1]},
                    {'x':silk_top_left[0]+seriesParams.flange_lenght, 'y':silk_top_left[1]},
                    {'x':silk_top_left[0]+seriesParams.flange_lenght, 'y':silk_top_left[1]+flange_cutout},
                    {'x':silk_top_left[0], 'y':silk_top_left[1]+flange_cutout},
                    {'x':silk_top_left[0], 'y':silk_bottom_right[1]}
                ]
            kicad_mod.append(PolygoneLine(polygone=outline_poly))
            if with_fabLayer:
                outline_poly=offset_polyline(outline_poly,-globalParams.silk_body_offset,(center_x,0))
                kicad_mod.append(PolygoneLine(polygone=outline_poly, layer="F.Fab", width=0.05))
        if params.flanged:
            kicad_mod.append(Circle(center=calc_dim.mount_hole_left, radius=1.9, layer='F.SilkS'))
            kicad_mod.append(Circle(center=calc_dim.mount_hole_right, radius=1.9, layer='F.SilkS'))
            if not params.mount_hole:
                kicad_mod.append(Circle(center=calc_dim.mount_hole_left, radius=1, layer='F.SilkS'))
                kicad_mod.append(Circle(center=calc_dim.mount_hole_right, radius=1, layer='F.SilkS'))
            if with_fabLayer:
                kicad_mod.append(Circle(center=calc_dim.mount_hole_left, radius=1.9, layer='F.Fab', width=globalParams.fab_line_width))
                kicad_mod.append(Circle(center=calc_dim.mount_hole_right, radius=1.9, layer='F.Fab', width=globalParams.fab_line_width))
                kicad_mod.append(Circle(center=calc_dim.mount_hole_left, radius=1, layer='F.Fab', width=globalParams.fab_line_width))
                kicad_mod.append(Circle(center=calc_dim.mount_hole_right, radius=1, layer='F.Fab', width=globalParams.fab_line_width))

        for i in range(params.num_pins):
            plug_outline_translation = Translation(i*params.pin_pitch, 0)
            plug_outline_poly=[
                {'x':-seriesParams.plug_arc_len/2.0, 'y':calc_dim.plug_front},
                {'x':-seriesParams.plug_cut_len/2.0, 'y':calc_dim.plug_front},
                {'x':-seriesParams.plug_cut_len/2.0, 'y':calc_dim.plug_front-seriesParams.plug_cut_width},
                {'x':-seriesParams.plug_seperator_distance/2.0, 'y':calc_dim.plug_front-seriesParams.plug_cut_width},
                {'x':-seriesParams.plug_seperator_distance/2.0, 'y':calc_dim.plug_back+seriesParams.plug_trapezoid_width},
                {'x':-seriesParams.plug_trapezoid_short/2.0, 'y':calc_dim.plug_back+seriesParams.plug_trapezoid_width},
                {'x':-seriesParams.plug_trapezoid_long/2.0, 'y':calc_dim.plug_back},
                {'x':seriesParams.plug_trapezoid_long/2.0, 'y':calc_dim.plug_back},
                {'x':seriesParams.plug_trapezoid_short/2.0, 'y':calc_dim.plug_back+seriesParams.plug_trapezoid_width},
                {'x':seriesParams.plug_seperator_distance/2.0, 'y':calc_dim.plug_back+seriesParams.plug_trapezoid_width},
                {'x':seriesParams.plug_seperator_distance/2.0, 'y':calc_dim.plug_front-seriesParams.plug_cut_width},
                {'x':seriesParams.plug_cut_len/2.0, 'y':calc_dim.plug_front-seriesParams.plug_cut_width},
                {'x':seriesParams.plug_cut_len/2.0, 'y':calc_dim.plug_front},
                {'x':seriesParams.plug_arc_len/2.0, 'y':calc_dim.plug_front}
            ]
            plug_outline_translation.append(PolygoneLine(polygone=plug_outline_poly))
            plug_outline_translation.append(Arc(start=[-seriesParams.plug_arc_len/2.0,calc_dim.plug_front], center=[0,calc_dim.plug_front+1.7], angle=47.6))
            if with_fabLayer:
                plug_outline_translation.append(PolygoneLine(polygone=plug_outline_poly,  layer="F.Fab", width=0.05))
                plug_outline_translation.append(Arc(start=[-seriesParams.plug_arc_len/2.0,calc_dim.plug_front], center=[0,calc_dim.plug_front+1.7], angle=47.6,  layer="F.Fab", width=0.05))
            kicad_mod.append(plug_outline_translation)
    if params.angled:
        crtyd_top_left=v_offset([silk_top_left[0],-seriesParams.pin_Sy/2], globalParams.courtyard_distance)
    else:
        crtyd_top_left=v_offset(body_top_left, globalParams.courtyard_distance)
    crtyd_bottom_right=v_offset(body_bottom_right, globalParams.courtyard_distance)
    kicad_mod.append(RectLine(start=round_crty_point(crtyd_top_left), end=round_crty_point(crtyd_bottom_right), layer='F.CrtYd'))
    if params.mount_hole:
        kicad_mod.append(Circle(center=calc_dim.mount_hole_left, radius=seriesParams.mount_screw_head_r, layer='B.SilkS'))
        kicad_mod.append(Circle(center=calc_dim.mount_hole_right, radius=seriesParams.mount_screw_head_r, layer='B.SilkS'))
        if with_fabLayer:
            kicad_mod.append(Circle(center=calc_dim.mount_hole_left, radius=seriesParams.mount_screw_head_r, layer='B.Fab', width=globalParams.fab_line_width))
            kicad_mod.append(Circle(center=calc_dim.mount_hole_right, radius=seriesParams.mount_screw_head_r, layer='B.Fab', width=globalParams.fab_line_width))
        # kicad_mod.append(Circle(center=mount_hole_left, radius=mount_screw_head_r+0.25, layer='B.CrtYd'))
        # kicad_mod.append(Circle(center=mount_hole_right, radius=mount_screw_head_r+0.25, layer='B.CrtYd'))

    kicad_mod.append(Text(type='reference', text='REF**', at=[center_x + (0 if params.num_pins > 2 else 1), crtyd_top_left[1]-0.7], layer='F.SilkS'))
    kicad_mod.append(Text(type='value', text=footprint_name, at=[center_x, crtyd_bottom_right[1]+1], layer='F.Fab'))
    if with_fabLayer:
        if params.angled:
            kicad_mod.append(Text(type='user', text="%R", at=[center_x, body_bottom_right[1]-1.5], layer='F.Fab'))
        else:
            kicad_mod.append(Text(type='user', text="%R", at=[0, -0.1], layer='F.Fab', rotation=90.0))
    kicad_mod.append(create_marker(crtyd_top_left[1]))

    p3dname = packages_3d + footprint_name + ".wrl"
    kicad_mod.append(Model(filename=p3dname,
                           at=[0, 0, 0], scale=[1, 1, 1], rotate=[0, 0, 0]))

    file_handler = KicadFileHandler(kicad_mod)
    file_handler.writeFile(out_dir+footprint_name + ".kicad_mod")


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print('No variant name is given! building all')
        to_generate=all_params
    else:
        variant=sys.argv[1]
        if variant == "all":
            to_generate=all_params
        elif variant in all_params.keys():
            to_generate = {variant:all_params[variant]}
        else:
            print('ERROR: Variant "'+ str(variant) + '" is not part of this package!')
            sys.exit(1)
        if len(sys.argv) < 3:
            with_fabLayer = False
        else:
            with_fabLayer = sys.argv[2] == "WITH_FFAB"

    #m ='MCV_01x02_GF_5.08mm_MH'
    #to_generate = {m:all_params[m]}


    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for model, params in to_generate.iteritems():
        generate_one_footprint(model, params, with_fabLayer)
