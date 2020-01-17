import sys
import os
import argparse
import yaml
import math

# load parent path of KicadModTree
sys.path.append(os.path.join(sys.path[0], "..", "..", ".."))
from KicadModTree import *  # NOQA
from KicadModTree.util.geometric_util import geometricLine, geometricCircle

 # load parent path of tools
sys.path.append(os.path.join(sys.path[0], "..", "..", "tools"))
from footprint_text_fields import addTextFields

FOOTPRINT_TYPES = {
    'plain':{
        'name': '',
        'description': '',
        'tag': '',
        'relieve_count': 0
    },
    'relieve':{
        'name': '_Relieve',
        'description': ' with feed through strain relieve',
        'tag': ' strain-relieve',
        'relieve_count': 1
    },
    'relieve2x':{
        'name': '_Relieve2x',
        'description': ' with double feed through strain relieve',
        'tag': ' double-strain-relieve',
        'relieve_count': 2
    }
}

def bend_radius(wire_def):
    return wire_def['outer_diameter'] * 3

def fp_name_gen(wire_def, fp_type):
    if 'area' in wire_def:
        size_code = '{:.2f}sqmm'.format(wire_def['area'])

    return 'SolderWire-{}_D{:.2f}mm_OD{:.2f}mm{}'\
        .format(size_code, wire_def['diameter'], wire_def['outer_diameter'], fp_type)

def description_gen(wire_def, fp_type):
    if 'area' in wire_def:
        size_code = '{:.2f} square mm'.format(wire_def['area'])

    return (
        'Soldered wire connection{}, for {} wire, '
        '{} insulation, '
        'conductor diameter {:.2f}mm, outer diameter {:.2f}mm, '
        'sice source {}, '
        'bend radius 3 times outer diameter, '
        'generated with kicad-footprint-generator'
        .format(
                fp_type, size_code,
                wire_def['insulation'],
                wire_def['diameter'], wire_def['outer_diameter'],
                wire_def['source']
            )
    )

def tag_gen(wire_def, fp_type):
    if 'area' in wire_def:
        size_code = '{:.2f}sqmm'.format(wire_def['area'])

    return 'connector wire {}{}'.format(size_code, fp_type)

def make_fp(wire_def, fp_type, configuration):
    crtyd_off= configuration['courtyard_offset']['connector']
    silk_pad_off = configuration['silk_pad_clearance'] + configuration['silk_line_width']/2

    fp_name = fp_name_gen(wire_def, fp_type['name'])

    kicad_mod = Footprint(fp_name)
    kicad_mod.setDescription(description_gen(wire_def, fp_type['description']))

    kicad_mod.setTags(tag_gen(wire_def, fp_type['tag']))

    kicad_mod.setAttribute('virtual')

    pad_drill = wire_def['diameter'] + 0.2
    pad_size = pad_drill + 1

    npth_drill = wire_def['outer_diameter'] + 0.5
    npth_offset = bend_radius(wire_def)*2

    kicad_mod.append(Pad(
            number=1, type=Pad.TYPE_THT, shape=Pad.SHAPE_ROUNDRECT,
            at=(0, 0), drill=pad_drill, size=pad_size,
            radius_ratio=0.25, maximum_radius=0.25,
            layers=Pad.LAYERS_THT
        ))

    for i in range(fp_type['relieve_count']):
        kicad_mod.append(Pad(
                number='', type=Pad.TYPE_NPTH, shape=Pad.SHAPE_CIRCLE,
                at=(0, (i+1)*npth_offset), drill=npth_drill, size=npth_drill,
                layers=Pad.LAYERS_NPTH
            ))

    ######################### Fab Graphic ###############################
    for i in range(fp_type['relieve_count']+1):
        kicad_mod.append(Circle(
                center=(0, i*npth_offset), radius=wire_def['outer_diameter']/2,
                layer='F.Fab', width=configuration['fab_line_width']
            ))

    # wire on top side
    if fp_type['relieve_count']>0:
        for i in range((fp_type['relieve_count']+1)//2):
            sy = 2*i * npth_offset
            ey = (2*i+1) * npth_offset
            kicad_mod.append(Line(
                    start=(-wire_def['outer_diameter']/2, sy),
                    end=(-wire_def['outer_diameter']/2, ey),
                    layer='F.Fab', width=configuration['fab_line_width']
                ))
            kicad_mod.append(Line(
                    start=(wire_def['outer_diameter']/2, sy),
                    end=(wire_def['outer_diameter']/2, ey),
                    layer='F.Fab', width=configuration['fab_line_width']
                ))

    if fp_type['relieve_count']>1:
        for i in range(fp_type['relieve_count']):
            kicad_mod.append(Circle(
                    center=(0, (i+1)*npth_offset), radius=wire_def['outer_diameter']/2,
                    layer='B.Fab', width=configuration['fab_line_width']
                ))
        for i in range((fp_type['relieve_count'])//2):
            sy = (2*i+1) * npth_offset
            ey = (2*i+2) * npth_offset
            kicad_mod.append(Line(
                    start=(-wire_def['outer_diameter']/2, sy),
                    end=(-wire_def['outer_diameter']/2, ey),
                    layer='B.Fab', width=configuration['fab_line_width']
                ))
            kicad_mod.append(Line(
                    start=(wire_def['outer_diameter']/2, sy),
                    end=(wire_def['outer_diameter']/2, ey),
                    layer='B.Fab', width=configuration['fab_line_width']
                ))

    ######################### Silk Graphic ##############################

    silk_x = wire_def['outer_diameter']/2 + configuration['silk_fab_offset']

    silk_helper_line = geometricLine(start=(silk_x, 0), end=(silk_x, npth_offset))\
        .cut(geometricCircle(center=(0,0), radius=(npth_drill/2 + silk_pad_off)))[1]

    silk_y_rel_npth = silk_helper_line.start_pos['x']

    if fp_type['relieve_count']>0:
        if silk_x > pad_size/2 + silk_pad_off:
            top = 0
        else:
            top = pad_size/2 + silk_pad_off

        bottom = npth_offset - silk_y_rel_npth
        kicad_mod.append(Line(
                start=(silk_x, top), end=(silk_x, bottom),
                layer='F.SilkS', width=configuration['silk_line_width']
            ))
        kicad_mod.append(Line(
                start=(-silk_x, top), end=(-silk_x, bottom),
                layer='F.SilkS', width=configuration['silk_line_width']
            ))

    if fp_type['relieve_count']>1:
        for i in range(fp_type['relieve_count']-1):
            layer = 'F.SilkS' if i%2 == 1 else 'B.SilkS'

            top = (i+1)*npth_offset + silk_y_rel_npth
            bottom = (i+2)*npth_offset - silk_y_rel_npth

            kicad_mod.append(Line(
                    start=(silk_x, top), end=(silk_x, bottom),
                    layer=layer, width=configuration['silk_line_width']
                ))
            kicad_mod.append(Line(
                    start=(-silk_x, top), end=(-silk_x, bottom),
                    layer=layer, width=configuration['silk_line_width']
                ))

    ########################## Courtyard ################################

    crtyd_x = max(pad_size, npth_drill)/2 + crtyd_off
    crtyd_top = -max(pad_size, wire_def['outer_diameter'])/2 - crtyd_off
    crtyd_top_main = crtyd_top
    if fp_type['relieve_count'] == 0:
        crtyd_bottom = -crtyd_top
        crtyd_bottom_main = crtyd_bottom
    else:
        crtyd_bottom = npth_offset + npth_drill/2 + crtyd_off
        crtyd_bottom_main = npth_offset*fp_type['relieve_count'] + npth_drill/2 + crtyd_off

    layer = 'F.CrtYd'
    kicad_mod.append(RectLine(
            start=Vector2D(-crtyd_x, crtyd_top).round_to(configuration['courtyard_grid']),
            end=Vector2D(crtyd_x, crtyd_bottom).round_to(configuration['courtyard_grid']),
            layer=layer, width=configuration['courtyard_line_width']
        ))

    if fp_type['relieve_count']>0:
        i = fp_type['relieve_count']
        layer = 'B.CrtYd' if i%2 == 1 else 'F.CrtYd'

        crtyd_top = (i)*npth_offset - (npth_drill/2 + crtyd_off)
        crtyd_bottom = (i)*npth_offset + npth_drill/2 + crtyd_off

        kicad_mod.append(RectLine(
                start=Vector2D(-crtyd_x, crtyd_top).round_to(configuration['courtyard_grid']),
                end=Vector2D(crtyd_x, crtyd_bottom).round_to(configuration['courtyard_grid']),
                layer=layer, width=configuration['courtyard_line_width']
            ))

    if fp_type['relieve_count']>1:
        for i in range(fp_type['relieve_count']-1):
            layer = 'F.CrtYd' if i%2 == 1 else 'B.CrtYd'

            crtyd_top = (i+1)*npth_offset - (npth_drill/2 + crtyd_off)
            crtyd_bottom = (i+2)*npth_offset + npth_drill/2 + crtyd_off

            kicad_mod.append(RectLine(
                    start=Vector2D(-crtyd_x, crtyd_top).round_to(configuration['courtyard_grid']),
                    end=Vector2D(crtyd_x, crtyd_bottom).round_to(configuration['courtyard_grid']),
                    layer=layer, width=configuration['courtyard_line_width']
                ))


    ######################### Text Fields ###############################
    addTextFields(
        kicad_mod=kicad_mod, configuration=configuration,
        body_edges={
            'left':-wire_def['outer_diameter']/2,
            'right':wire_def['outer_diameter']/2,
            'top':-wire_def['outer_diameter']/2,
            'bottom':wire_def['outer_diameter']/2+fp_type['relieve_count']*npth_offset
            },
        courtyard={'top':crtyd_top_main, 'bottom':crtyd_bottom_main},
        fp_name=fp_name, text_y_inside_position='center',
        allow_rotation=True
        )

    ##################### Output and 3d model ############################

    model3d_path_prefix = configuration.get('3d_model_prefix','${KISYS3DMOD}/')

    lib_name = 'Connector_Wire'
    model_name = '{model3d_path_prefix:s}{lib_name:s}.3dshapes/{fp_name:s}.wrl'.format(
        model3d_path_prefix=model3d_path_prefix, lib_name=lib_name, fp_name=fp_name)
    kicad_mod.append(Model(filename=model_name))

    output_dir = '{lib_name:s}.pretty/'.format(lib_name=lib_name)
    if not os.path.isdir(output_dir):
        #returns false if path does not yet exist!! (Does not check path validity)
        os.makedirs(output_dir)

    filename = '{outdir:s}{fp_name:s}.kicad_mod'\
            .format(outdir=output_dir, fp_name=fp_name)

    file_handler = KicadFileHandler(kicad_mod)
    file_handler.writeFile(filename)

def make_for_wire(wire_def, configuration):
    for fp_type in FOOTPRINT_TYPES:
        make_fp(wire_def, FOOTPRINT_TYPES[fp_type], configuration)

def make_for_file(filepath, configuration):
    with open(filepath, 'r') as wire_definition:
        try:
            wires = yaml.safe_load(wire_definition)
            for w in wires:
                make_for_wire(wires[w], configuration)
        except yaml.YAMLError as exc:
            print(exc)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Create footprints for directly soldering wires to a PCB.'
        )
    parser.add_argument(
        'wire_def', metavar='wire_def', type=str, nargs='+',
        help='Wire definition files'
        )
    parser.add_argument(
        '--global_config', type=str, nargs='?',
        help='the config file defining how the footprint will look like. (KLC)',
        default='../../tools/global_config_files/config_KLCv3.0.yaml'
        )

    args = parser.parse_args()

    with open(args.global_config, 'r') as config_stream:
        try:
            configuration = yaml.safe_load(config_stream)
        except yaml.YAMLError as exc:
            print(exc)

    for filepath in args.wire_def:
        make_for_file(filepath, configuration)
