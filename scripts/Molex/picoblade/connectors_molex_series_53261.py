import sys
import os

# export PYTHONPATH="${PYTHONPATH}<path to kicad-footprint-generator directory>"
from KicadModTree import *

addidional_pin1_marker = 0

def round_to(n, precision):
    correction = 0.5 if n >= 0 else -0.5
    return int( n/precision+correction ) * precision

def round_crty_point(point):
    return [round_to(point[0],0.05),round_to(point[1],0.05)]

class footprintParams():
    tags = "connector picoblade header Molex smt"

    fab_line_width = 0.05
    silk_to_body_offset = 0.1
    silk_to_pad_min_distance = 0.2

    reference_pos_x_to_last_pin = 3.1
    reference_pos_y = -3.3
    reference_second_y = 0.5

    value_pos_y = 3.3

    pin_pitch = 1.25
    pad_para = {"type":Pad.TYPE_SMT, "shape":Pad.SHAPE_RECT, "layers":['F.Cu', 'F.Mask', 'F.Paste']}
    pin_pad_size = [0.8,1.6]
    pin_pad_center_y = -2.9

    mount_pad_size = [2.1,3]
    mount_pad_center_y = 0
    mount_pad_center_x_to_pin = 2.55

    dx_main_body_to_pin = 1.5
    y_main_body_top = -2.1
    y_main_body_bottom = 4.2+y_main_body_top

    dx_mount_body_to_pin = 3.2
    y_mount_body_top = -1.1
    y_mount_body_bottom = 1.7

    fab_first_marker_w = 1.25
    fab_first_marker_h = 1

    silk_first_marker_w = 0.8
    silk_first_marker_h = 0.5
    silk_first_marker_bottom_to_pin_top = 0.5

    courtyard_distance = 0.5

def generate_footprint(num_pins, lib_name = "Connectors_Molex", ref_on_ffab=False):
    footprint_name = "Molex_PicoBlade_53261-"+ ('%02d' % num_pins) +"71_" + ('%02d' % num_pins) + "x" + ('%.2f' % footprintParams.pin_pitch) +"mm_Angled"
    description = "Molex PicoBlade, single row, side entry type, surface mount, PN:53261-" + ('%02d' % num_pins) + "71"

    out_dir=lib_name+".pretty"+os.sep
    packages_3d=lib_name+".3dshapes"+os.sep
    kicad_mod = Footprint(footprint_name)

    kicad_mod.setDescription(description)
    kicad_mod.setTags(footprintParams.tags)

    #########################################################################################################
    #                                               PADS                                                    #
    #########################################################################################################
    outher_pin_to_0 = (num_pins-1)*footprintParams.pin_pitch/2.0
    for pin_number in range(1,num_pins+1):
        pos_x = -outher_pin_to_0 + (pin_number-1)*footprintParams.pin_pitch
        kicad_mod.append(Pad(number=pin_number, at=[pos_x, footprintParams.pin_pad_center_y],
            size=footprintParams.pin_pad_size, **footprintParams.pad_para))

    left_mount_pad_center_x = -outher_pin_to_0-footprintParams.mount_pad_center_x_to_pin
    kicad_mod.append(Pad(number='""', at=[left_mount_pad_center_x, footprintParams.mount_pad_center_y],
        size=footprintParams.mount_pad_size,  **footprintParams.pad_para))
    kicad_mod.append(Pad(number='""', at=[-left_mount_pad_center_x, footprintParams.mount_pad_center_y],
        size=footprintParams.mount_pad_size,  **footprintParams.pad_para))

    #########################################################################################################
    #                                          F.Fab outline                                                #
    #########################################################################################################
    # see freecad drawing
    dx_main_body = footprintParams.dx_main_body_to_pin + outher_pin_to_0
    dx_mount_body = footprintParams.dx_mount_body_to_pin + outher_pin_to_0
    poly_main_body=[
        {'x':-dx_main_body, 'y':footprintParams.y_main_body_top},
        {'x':dx_main_body, 'y':footprintParams.y_main_body_top},
        {'x':dx_main_body, 'y':footprintParams.y_main_body_bottom},
        {'x':-dx_main_body, 'y':footprintParams.y_main_body_bottom},
        {'x':-dx_main_body, 'y':footprintParams.y_main_body_top}
    ]
    kicad_mod.append(PolygoneLine(polygone=poly_main_body, layer='F.Fab', width=footprintParams.fab_line_width))

    poly_right_mount_body = [
        {'x':dx_main_body, 'y':footprintParams.y_mount_body_top},
        {'x':dx_mount_body, 'y':footprintParams.y_mount_body_top},
        {'x':dx_mount_body, 'y':footprintParams.y_mount_body_bottom},
        {'x':dx_main_body, 'y':footprintParams.y_mount_body_bottom}
    ]
    kicad_mod.append(PolygoneLine(polygone=poly_right_mount_body, layer='F.Fab', width=footprintParams.fab_line_width))

    poly_left_mount_body = [
        {'x':-dx_main_body, 'y':footprintParams.y_mount_body_bottom},
        {'x':-dx_mount_body, 'y':footprintParams.y_mount_body_bottom},
        {'x':-dx_mount_body, 'y':footprintParams.y_mount_body_top},
        {'x':-dx_main_body, 'y':footprintParams.y_mount_body_top}
    ]
    kicad_mod.append(PolygoneLine(polygone=poly_left_mount_body, layer='F.Fab', width=footprintParams.fab_line_width))

    fab_marker_left = -outher_pin_to_0 - footprintParams.fab_first_marker_w/2.0
    fab_marker_bottom = footprintParams.y_main_body_top + footprintParams.fab_first_marker_h
    poly_fab_marker = [
        {'x':fab_marker_left, 'y':footprintParams.y_main_body_top},
        {'x':-outher_pin_to_0, 'y':fab_marker_bottom},
        {'x':fab_marker_left + footprintParams.fab_first_marker_w, 'y':footprintParams.y_main_body_top}
    ]
    kicad_mod.append(PolygoneLine(polygone=poly_fab_marker, layer='F.Fab', width=footprintParams.fab_line_width))

    #########################################################################################################
    #                                              Silk outline                                             #
    #########################################################################################################

    dx_silk_top_near_pin = outher_pin_to_0 + footprintParams.silk_to_pad_min_distance + footprintParams.pin_pad_size[0]/2.0
    y_silk_top = footprintParams.y_main_body_top - footprintParams.silk_to_body_offset
    y_pin_marker = footprintParams.pin_pad_center_y - footprintParams.pin_pad_size[1]/2.0
    dx_main_silk = dx_main_body + footprintParams.silk_to_body_offset
    y_silk_mount_pad_top = footprintParams.mount_pad_center_y - footprintParams.mount_pad_size[1]/2.0 - footprintParams.silk_to_pad_min_distance

    poly_silk_left_top = [
        {'x':-dx_silk_top_near_pin, 'y':y_pin_marker},
        {'x':-dx_silk_top_near_pin, 'y':y_silk_top},
        {'x':-dx_main_silk, 'y':y_silk_top},
        {'x':-dx_main_silk, 'y':y_silk_mount_pad_top}
    ]
    kicad_mod.append(PolygoneLine(polygone=poly_silk_left_top))

    poly_silk_right_top = [
        {'x':dx_silk_top_near_pin, 'y':y_silk_top},
        {'x':dx_main_silk, 'y':y_silk_top},
        {'x':dx_main_silk, 'y':y_silk_mount_pad_top}
    ]
    kicad_mod.append(PolygoneLine(polygone=poly_silk_right_top))

    poly_silk_bottom = []

    y_silk_mount_pad_bottom = footprintParams.mount_pad_center_y + footprintParams.mount_pad_size[1]/2.0 + footprintParams.silk_to_pad_min_distance
    y_silk_mount_bottom = footprintParams.y_mount_body_bottom + footprintParams.silk_to_body_offset
    y_silk_bottom = footprintParams.y_main_body_bottom + footprintParams.silk_to_body_offset
    dx_mount_silk = dx_mount_body + footprintParams.silk_to_body_offset

    if y_silk_mount_pad_bottom < y_silk_mount_bottom:
        poly_silk_bottom.append({'x':-dx_mount_silk, 'y':y_silk_mount_pad_bottom})
    if y_silk_mount_pad_bottom <= y_silk_mount_bottom:
        poly_silk_bottom.append({'x':-dx_mount_silk, 'y':y_silk_mount_bottom})
        poly_silk_bottom.append({'x':-dx_main_silk, 'y':y_silk_mount_bottom})
    else:
        poly_silk_bottom.append({'x':-dx_main_silk, 'y':y_silk_mount_pad_bottom})

    poly_silk_bottom.append({'x':-dx_main_silk, 'y':y_silk_bottom})
    poly_silk_bottom.append({'x':dx_main_silk, 'y':y_silk_bottom})

    if y_silk_mount_pad_bottom <= y_silk_mount_bottom:
        poly_silk_bottom.append({'x':dx_main_silk, 'y':y_silk_mount_bottom})
        poly_silk_bottom.append({'x':dx_mount_silk, 'y':y_silk_mount_bottom})
    else:
        poly_silk_bottom.append({'x':dx_main_silk, 'y':y_silk_mount_pad_bottom})
    if y_silk_mount_pad_bottom < y_silk_mount_bottom:
        poly_silk_bottom.append({'x':dx_mount_silk, 'y':y_silk_mount_pad_bottom})

    kicad_mod.append(PolygoneLine(polygone=poly_silk_bottom))

    if addidional_pin1_marker:
        silk_pin1_marker_bottom = y_pin_marker - footprintParams.silk_first_marker_bottom_to_pin_top
        silk_pin1_marker_left = -outher_pin_to_0 - footprintParams.silk_first_marker_w/2.0

        poly_silk_pin1_marker = [
            {'x':-outher_pin_to_0, 'y':silk_pin1_marker_bottom},
            {'x':silk_pin1_marker_left, 'y':silk_pin1_marker_bottom - footprintParams.silk_first_marker_h},
            {'x':silk_pin1_marker_left + footprintParams.silk_first_marker_w, 'y':silk_pin1_marker_bottom - footprintParams.silk_first_marker_h},
            {'x':-outher_pin_to_0, 'y':silk_pin1_marker_bottom}
        ]
        kicad_mod.append(PolygoneLine(polygone=poly_silk_pin1_marker))
    #########################################################################################################
    #                                              3D Model                                                 #
    #########################################################################################################
    p3dname = packages_3d + footprint_name + ".wrl"
    kicad_mod.append(Model(filename=p3dname,
                           at=[0, 0, 0], scale=[1, 1, 1], rotate=[0, 0, 0]))

    #########################################################################################################
    #                                            Courtyard                                                 #
    #########################################################################################################

    dx_crtyd = outher_pin_to_0 + footprintParams.mount_pad_center_x_to_pin + footprintParams.mount_pad_size[0]/2.0 + footprintParams.courtyard_distance
    crtyd_top = footprintParams.pin_pad_center_y - footprintParams.pin_pad_size[1]/2.0 - footprintParams.courtyard_distance
    crtyd_bottom = footprintParams.y_main_body_bottom + footprintParams.courtyard_distance

    kicad_mod.append(RectLine(start=round_crty_point((-dx_crtyd, crtyd_top)), end=round_crty_point((dx_crtyd, crtyd_bottom)), layer='F.CrtYd'))
    #########################################################################################################
    #                                          Text Fields                                                  #
    #########################################################################################################
    ref_pos_1=[footprintParams.reference_pos_x_to_last_pin + outher_pin_to_0, footprintParams.reference_pos_y]
    ref_pos_2=[0, footprintParams.reference_second_y]
    kicad_mod.append(Text(type='reference', text='REF**', layer=('F.Fab' if ref_on_ffab else'F.SilkS'),
        at=(ref_pos_2 if ref_on_ffab else ref_pos_1)))
    if ref_on_ffab:
        kicad_mod.append(Text(type='user', text='%R', at=ref_pos_1, layer='F.SilkS'))
    kicad_mod.append(Text(type='value', text=footprint_name, layer='F.Fab', at=[0, footprintParams.value_pos_y]))

    #########################################################################################################
    #                                              output                                                   #
    #########################################################################################################
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    file_handler = KicadFileHandler(kicad_mod)
    file_handler.writeFile(out_dir+footprint_name + ".kicad_mod")

if __name__ == "__main__":
    all_possible_pin_numbers=[2,3,4,5,6,7,8,9,10,11,12,13,14,15,17]

    for pin_number in all_possible_pin_numbers:
        generate_footprint(pin_number, lib_name = "tera_Connectors_Molex", ref_on_ffab=True)
