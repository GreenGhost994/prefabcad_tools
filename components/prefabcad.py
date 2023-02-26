from dataclasses import dataclass, field
from typing import Any
from os import path, listdir, walk
from collections import defaultdict
import re

class Accessory:
    """PrefaBCad accessory"""
    
    def __init__(self, acc_data: list):
        self.amount = clear_val(acc_data[0], 'float')
        self.name = acc_data[1]
        self.length = clear_val(acc_data[2], 'float')
        self.index, self.type = clear_index(acc_data[3], acc_data[1])

    def __repr__(self):
            return f'{self.amount}x {self.name} ({self.index})'

    def __eq__(self, other):
        if isinstance(other, Accessory):
            return (self.amount, self.name, self.length, self.index) == (other.amount, other.name, other.length, other.index)
        return False
    
    def __hash__(self):
        return hash((self.amount, self.name, self.length, self.index))


@dataclass
class Element:
    """PrefaBCad element"""
    
    file_date: float = 0
    drawing_name: str = ''
    drawing_number: str = ''
    creation_date: str = ''
    revision: str = ''
    revision_date: str = ''
    amount: float = 0
    volume: float = 0
    concrete_class: str = ''
    demoulding_force: str = ''
    reinforcement_mass: float = 0
    strands_bottom_amount: float = 0
    strands_bottom_diam: float = 0
    strands_bottom_force: str = ''
    strands_top_amount: str = ''
    strands_top_diam: str = ''
    strands_top_force: str = ''
    fire_resistance: str = ''
    exposure_class: str = ''
    element_length: int = 0
    element_width: int = 0
    element_height: int = 0
    status: str = ''
    factory: str = ''
    mesh_mass: str = ''
    steel_mass: str = ''
    reinforcement_mass_dia: str = ''
    mark_exist: str = ''
    reinforcement_amount: str = ''
    steel_amount: str = ''
    mesh_amount: str = ''
    element_mass: float = 0
    element_mass_montage: float = 0
    element_area: str = ''
    revisions: str = ''
    element_name: str = ''
    element_type: str = ''
    project_index: str = ''
    accessories: list[Accessory] = field(default_factory=list)

    def __repr__(self):
        return self.element_name
            
    def from_txt(self, file_path: str):
        def load_parameters(self, parameters: list, accessories: list):
            self.file_date = parameters[0]
            self.drawing_name = parameters[1]
            self.drawing_number = parameters[2]
            self.creation_date = parameters[3]
            self.revision = clear_val(parameters[4], 'rev')
            self.revision_date = parameters[5]
            self.amount = clear_val(parameters[6], 'float')
            self.volume = clear_val(parameters[7], 'float')
            self.concrete_class = parameters[8]
            self.demoulding_force = parameters[9]
            self.reinforcement_mass = clear_val(parameters[10], 'float')
            self.strands_bottom_amount = clear_val(parameters[11], 'float')
            self.strands_bottom_diam = clear_val(parameters[12], 'float')
            self.strands_bottom_force = parameters[13]
            self.strands_top_amount = clear_val(parameters[14], 'float')
            self.strands_top_diam = clear_val(parameters[15], 'float')
            self.strands_top_force = parameters[16]
            self.fire_resistance = parameters[17]
            self.exposure_class = parameters[18]
            self.element_length = clear_val(parameters[19], 'float')
            self.element_width = clear_val(parameters[20], 'float')
            self.element_height = clear_val(parameters[21], 'float')
            self.status = parameters[22]
            self.factory = convert_to_list_of_lists(parameters[23].split('|'))
            self.mesh_mass = clear_val(parameters[24], 'float')
            self.steel_mass = clear_val(parameters[25], 'float')
            self.reinforcement_mass_dia = parameters[26:42]
            self.mark_exist = parameters[42]
            self.reinforcement_amount = parameters[44]
            self.steel_amount = parameters[45]

            self.mesh_amount = parameters[56]
            self.element_mass = clear_val(parameters[57], vtype='float')
            self.element_mass_montage = clear_val(parameters[58], vtype='float')

            self.element_area = clear_val(parameters[60], vtype='float')
            self.revisions = parameters[61]
            self.element_name = parameters[62]
            self.element_type = parameters[63]

            self.project_index = parameters[66]

            self.accessories = [Accessory(x) for x in accessories]

        # read data from txt
        parameters, accessories = read_txt(file_path)
        
        # check if data is newer
        if not (parameters[63]).endswith('zbrojenie'):
            try:
                if self.revision != '':
                    if ord(self.revision) < ord(clear_val(parameters[4], vtype='rev')):  # if revision is higher
                        load_parameters(self, parameters, accessories)
                        return
                    elif (self.file_date < parameters[0]) and (ord(self.revision) == ord(clear_val(parameters[4], vtype='rev'))):  # if revision is the same but file is newer
                        load_parameters(self, parameters, accessories)
                        return
                else:
                    if self.file_date < parameters[0]:  # if file is newer
                        load_parameters(self, parameters, accessories)
                        return
            except Exception as e:
                print(e, file_path)
                return
    
    def acc_stats(self):
        """Calculate stats of accessories"""

        self.stats = {'lines_amount': len(self.accessories),
        'acc_lines_amount': len([x for x in self.accessories if x.type == 'accessory']),
        'acc_amount': sum([x.amount for x in self.accessories if x.type == 'accessory']),
        'steel_acc_lines_amount': len([x for x in self.accessories if x.type == 'steel_accessory']),
        'steel_acc_amount': sum([x.amount for x in self.accessories if x.type == 'steel_accessory']),
        'windows_lines_amount': len([x for x in self.accessories if x.type == 'window']),
        'windows_amount': sum([x.amount for x in self.accessories if x.type == 'window']),
        'other_lines_amount': len([x for x in self.accessories if x.type == 'other']),
        'other_amount': sum([x.amount for x in self.accessories if x.type == 'other']),
        }
        return self

def read_txt(file_path: str) -> list[list]:
    """Read data from PrefaBCad standard .txt file and split them to parameters and accessories."""
    
    count = 0
    accessories = []
    with open(file_path) as fp:
        for line in fp:
            count += 1
            if count == 1:
                parameters = (line.strip()).split('§')
            else:
                accessories.append((line.strip()).split('§'))

        parameters[0] = path.getmtime(file_path)

        return parameters, accessories

def txt_element_name(file_path: str) -> str:
    """Read element name from PrefaBCad standard .txt file"""

    with open(file_path) as fp:
        for line in fp:
            parameters = (line.strip()).split('§')
            return parameters[62]

def convert_to_list_of_lists(input_list: list) -> list[list[str]]:
    """Convertion list to list of list len 2"""

    result = []
    for i in range(0, len(input_list), 2):
        result.append(input_list[i:i+2])
    return result

def clear_val(value: str, vtype: str) -> Any:
    """Clear and unify the loaded values"""

    if type(value) == str:
        value = value.strip()
    non_value = ''
    if vtype == 'float':
        non_value = 0
    elif vtype == 'rev':
        non_value = '-'

    if value == '-' or value == '' or value == ' ':
        value = non_value

    if vtype == 'float' and type(value) != float:
        if not type(value) == int:
            if value.isdigit():
                value = float(value)
            elif (value.replace(".", "")).isdigit():
                value = float(value)

    return value

def clear_index(index: str, name: str) -> str:
    """Format index to 12 symbols if pattern is found"""

    if len(index) == 12:
        return index, 'accessory'
    elif index.startswith(('SB', 'SH')):
        match = re.match(r'^[A-Za-z]{2}\d{10}', index)
        if match:
            return match.group(), 'accessory'
    elif index.startswith('B'):
        match = re.match(r'^[A-Za-z]{1}\d{11}', index)
        if match:
            return match.group(), 'accessory'
    if name.startswith('Marka wg rys. '):
        index = name.strip('Marka wg rys. ')
        return index, 'steel_accessory'
    if '_AK_' in index:
        return index, 'steel_accessory'
    elif '_AW_' in index:
        return index, 'window'
    return index, 'other'

def load_elements(directory: str) -> dict:
    """Loop through all .txt files in directory and return data of all elements"""

    elements = defaultdict(lambda: Element())

    # loop folder and subfolders
    for subdir, dirs, files in walk(directory):
        for file in files:
            if file.endswith('.txt'):
                fpath = path.join(subdir, file)
                element_name = txt_element_name(fpath)
                elements[element_name].from_txt(fpath)

    return elements

def get_accessories(elements: dict[Element] | list[Element]) -> dict:
    """Extract list of accessories from dict or list of elements"""

    accessories = defaultdict(lambda: 0)
    if isinstance(elements, dict):
        elements = elements.values()

    for i in elements:
        for j in i.accessories:
            acc_name = (j.name, j.length, j.index)
            accessories[acc_name] += j.amount
    
    return [Accessory([v, k[0], k[1], k[2]]) for k, v in accessories.items()]

def update_steel_acc_amount(file_path: str, name: str, amount: int) -> bool:
    """Modify amount in .txt file."""

    with open(file_path, "r+") as f:
        data = f.read() # read everything in the file
        f.seek(0) # rewind
        data = data.split('§')
        if data[62] == name:
            data[45] = str(int(amount))
            data = '§'.join(data)
            f.write(data) # write everything to the file
            return True
        return False