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

(C) 2015-2016 by Thomas Pointhuber, <thomas.pointhuber@gmx.at>
'''

import time

def getFormatedFloat(val):
    return ('%f' % val).rstrip('0').rstrip('.')

def grid(val, spacing = 0.05):
    return int(val/spacing) * spacing
    
class KicadMod(object):
    def __init__(self, name):
        self.setModuleName(name)
        self.text_array = []
        self.line_array = []
        self.circle_array = []
        self.pad_array = []
        self.description = None
        self.tags = None
        self.attribute = None
        self.center_pos = {'x':0, 'y':0}
        self.model_pos = {'x':0, 'y':0,'z':0}
        self.model_scale = {'x':1,'y':1,'z':1}
        self.model_rot = {'x':0,'y':0,'z':0}
        self.model = None


    def setModuleName(self, name):
        self.module_name = name


    def setDescription(self, description):
        self.description = description


    def setTags(self, tags):
        self.tags = tags


    def setAttribute(self, value):
        self.attribute = value


    def setCenterPos(self, position):
        self.center_pos = position


    def addRawText(self, data):
        self.text_array.append(data)    


    def addText(self, which_text, text, position, layer='F.SilkS'):
        self.addRawText({'which_text':which_text
                        ,'text':text
                        ,'layer':layer
                        ,'position':position})

    def addReference(self, text, position, layer='F.SilkS'):
        self.addText('reference', text, position, layer)


    def addValue(self, text, position, layer='F.Fab'):
        self.addText('value', text, position, layer)

    def addRawLine(self, data):
        self.line_array.append(data)


    def addLine(self, start_pos, end_pos, layer='F.SilkS', width=0.15):
        self.addRawLine({'start':{'position':start_pos}
                        ,'end':{'position':end_pos}
                        ,'layer':layer
                        ,'width':width})


    def addPolygoneLine(self, polygone_line, layer='F.SilkS', width=0.15):
        for line_start, line_end in zip(polygone_line, polygone_line[1:]):
            self.addLine(line_start, line_end, layer, width)


    def addRectLine(self, start_pos, end_pos, layer='F.SilkS', width=0.15):
        self.addPolygoneLine([{'x':start_pos['x'], 'y':start_pos['y']}
                             ,{'x':start_pos['x'], 'y':end_pos['y']}
                             ,{'x':end_pos['x'], 'y':end_pos['y']}
                             ,{'x':end_pos['x'], 'y':start_pos['y']}
                             ,{'x':start_pos['x'], 'y':start_pos['y']}]
                            ,layer
                            ,width)


    def addRawCircle(self, data):
        self.circle_array.append(data)


    def addCircle(self, position, dimensions, layer='F.SilkS', width=0.15):
        self.addRawCircle({'position':position
                          ,'dimensions':dimensions
                          ,'layer':layer
                          ,'width':width})


    def addRawPad(self, data):
        self.pad_array.append(data)


    def addPad(self, number, type, form, position, size, drill, layers=['*.Cu', '*.Mask', 'F.SilkS']):
        self.addRawPad({'number':number, 'type':type, 'form':form, 'position':position, 'size':size, 'drill':drill, 'layers':layers})

    #create an un-numbered SMD mounting pad
    def addMountingPad(self, position, size):
        self.addRawPad({
            'number': '""',
            'type': 'smd',
            'form': 'rect',
            'position': position,
            'size': size,
            'drill': 0,
            'layers': ["F.Cu","F.Paste","F.Mask"]
        })
      
    #create an un-numbered NPTH mechanical mounting pad
    def addMountingHole(self, position, size):
        self.addRawPad({
            'number': '""',
            'type': "np_thru_hole",
            'form': "circle",
            'position': position,
            'size': {'x': size, 'y': size}  ,
            'drill': size,
            'layers': ["*.Cu"]
        })

    def _savePosition(self, position, keyword='at'):
        if position.get('orientation', 0) != 0:
            return '({keyword} {x} {y} {orientation})'.format(keyword=keyword
                                                             ,x=getFormatedFloat(position['x']-self.center_pos['x'])
                                                             ,y=getFormatedFloat(position['y']-self.center_pos['y'])
                                                             ,orientation=getFormatedFloat((position['orientation']+360)%360))
        else:
            return '({keyword} {x} {y})'.format(keyword=keyword
                                               ,x=getFormatedFloat(position['x']-self.center_pos['x'])
                                               ,y=getFormatedFloat(position['y']-self.center_pos['y']))


    def _saveSize(self, size, keyword='at'):
        return '({keyword} {x} {y})'.format(keyword=keyword
                                           ,x=getFormatedFloat(size['x'])
                                           ,y=getFormatedFloat(size['y']))


    def _saveText(self, data):
        output = '  (fp_text {which_text} {text} '.format(which_text=data['which_text']
                                                         ,text=data['text'])
        output += self._savePosition(data['position'], 'at')
        output += ' (layer {layer})\n'.format(layer=data['layer'])
        output += '    (effects (font (size 1 1) (thickness 0.15)))\n'
        output += '  )\n'
        
        return output


    def _saveLine(self, data):
        output = '  (fp_line '
        output += self._savePosition(data['start']['position'], 'start')
        output += ' '
        output += self._savePosition(data['end']['position'], 'end')
        output += ' (layer {layer}) (width {width}))\n'.format(layer=data['layer']
                                                                ,width=data['width'])
        return output


    def _saveCircle(self, data):
        output = '  (fp_circle '
        output += self._savePosition(data['position'], 'center')
        output += ' '
        
        dimensions = []
        dimensions = {'x':data['position']['x']+data['dimensions']['x']
                     ,'y':data['position']['y']+data['dimensions']['y']}
        
        output += self._savePosition(dimensions, 'end')
        output += ' (layer {layer}) (width {width}))\n'.format(layer=data['layer']
                                                                ,width=data['width'])
        return output


    def _savePad(self, data):
        output = '  (pad {number} {type} {form} '.format(number=data['number']
                                                        ,type=data['type']
                                                        ,form=data['form'])
        output += self._savePosition(data['position'], 'at')
        output += ' '
        output += self._saveSize(data['size'], 'size')
        output += ' (drill {drill}) '.format(drill=data['drill'])
        output += '(layers ' + ' '.join(data['layers']) + '))\n'
        return output
        
    def _saveModel(self):
        
        #model path
        output = "(model {model}\n".format(model=self.model)
        #model position
        output += "  (at (xyz {x} {y} {z}))\n".format(x=self.model_pos['x'],y=self.model_pos['y'],z=self.model_pos['z'])
        output += "  (scale (xyz {x} {y} {z}))\n".format(x=self.model_scale['x'],y=self.model_scale['y'],z=self.model_scale['z'])
        output += "  (rotate (xyz {x} {y} {z})))\n".format(x=self.model_rot['x'],y=self.model_rot['y'],z=self.model_rot['z'])
            
        return output
        
    def __str__(self):
        '''
        generate kicad_mod content
        '''
        output = '(module {name} (layer F.Cu) (tedit {timestamp:X})\n'.format(name=self.module_name, timestamp=int(time.time()))

        if self.description:
            output += '  (descr "{description}")\n'.format(description=self.description)

        if self.tags:
            output += '  (tags "{tags}")\n'.format(tags=self.tags)

        if self.attribute:
            output += '  (attr {attr})\n'.format(attr=self.attribute)

        for text in self.text_array:
            output += self._saveText(text)

        for circle in self.circle_array:
            output += self._saveCircle(circle)

        for line in self.line_array:
            output += self._saveLine(line)

        for pad in self.pad_array:
            output += self._savePad(pad)
            
        if (self.model):
            
            output += self._saveModel()

        output = output + '\n)'

        return output

#create 
def createNumberedPadsTHT(kicad_mod, pincount, pad_spacing, pad_diameter, pad_size, x_off=0, y_off=0, starting=1, increment=1):
    for i,pad_number in enumerate(range(starting, starting + (pincount * increment), increment)):
        pad_pos_x = (i)*pad_spacing + x_off
        if pad_number == 1:
            kicad_mod.addPad(pad_number, 'thru_hole', 'rect', {'x':pad_pos_x, 'y':y_off}, pad_size, pad_diameter, ['*.Cu', '*.Mask', 'F.SilkS'])
        elif pad_size['x'] == pad_size['y']:
            kicad_mod.addPad(pad_number, 'thru_hole', 'circle', {'x':pad_pos_x, 'y':y_off}, pad_size, pad_diameter, ['*.Cu', '*.Mask', 'F.SilkS'])
        else:
            kicad_mod.addPad(pad_number, 'thru_hole', 'oval', {'x':pad_pos_x, 'y':y_off}, pad_size, pad_diameter, ['*.Cu', '*.Mask', 'F.SilkS'])


def createNumberedPadsSMD(kicad_mod, pincount, pad_spacing, pad_size, pad_pos_y):
    start_pos_x = -(pincount-1)*pad_spacing/2.
    for pad_number in range(1, pincount+1):
        pad_pos_x = start_pos_x+(pad_number-1)*pad_spacing
        kicad_mod.addPad(pad_number, 'smd', 'rect', {'x':pad_pos_x, 'y':pad_pos_y}, pad_size, 0, ['F.Cu', 'F.Paste', 'F.Mask'])
