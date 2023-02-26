from components.prefabcad import load_elements, get_accessories
from collections import defaultdict, Counter
from math import isclose
import logging

class Found(Exception):
    pass


def analyze_project_stats(directory: str):
    elements = {k:v.acc_stats() for (k,v) in load_elements(directory).items()}  # load elements and add element accessory stats
    global_accessories = get_accessories(elements)
    report = analyze_elements(elements, global_accessories)

    return report


def check_acc_similarity(list1: list, list2: list) -> float:
    """Check how many objects (Accessory) from list1 are in list2"""

    common = [obj for obj in list1 if obj in list2]
    diff = [obj for obj in list1 if obj not in list2]

    set_common = {(obj.amount, obj.name, obj.length, obj.index) for obj in common}
    set_diff = {(obj.amount, obj.name, obj.length, obj.index) for obj in diff}

    similarity = len(set_common) / len(set_common | set_diff)
    return similarity


def calc_acc_average(ele_list: list) -> dict:
    """Calculate average stats of list of objects (Element)"""

    element_amount = [ele.amount for ele in ele_list]
    ele_average = {
        'volume': sum(weight * value for weight, value in zip(element_amount, [ele.volume for ele in ele_list])) / sum(element_amount),
        'length': sum(weight * value for weight, value in zip(element_amount, [ele.element_length for ele in ele_list])) / sum(element_amount),
        'width': sum(weight * value for weight, value in zip(element_amount, [ele.element_width for ele in ele_list])) / sum(element_amount),
        'height': sum(weight * value for weight, value in zip(element_amount, [ele.element_height for ele in ele_list])) / sum(element_amount),
        'area': sum(weight * value for weight, value in zip(element_amount, [ele.element_area for ele in ele_list])) / sum(element_amount),
    }
    acc_average = {
        'lines_amount':sum(weight * value for weight, value in zip(element_amount, [ele.stats['lines_amount'] for ele in ele_list])) / sum(element_amount),
        'acc_lines_amount': sum(weight * value for weight, value in zip(element_amount, [ele.stats['acc_lines_amount'] for ele in ele_list])) / sum(element_amount),
        'acc_amount': sum(weight * value for weight, value in zip(element_amount, [ele.stats['acc_amount'] for ele in ele_list])) / sum(element_amount),
        'steel_acc_lines_amount': sum(weight * value for weight, value in zip(element_amount, [ele.stats['steel_acc_lines_amount'] for ele in ele_list])) / sum(element_amount),
        'steel_acc_amount': sum(weight * value for weight, value in zip(element_amount, [ele.stats['steel_acc_amount'] for ele in ele_list])) / sum(element_amount),
        'windows_lines_amount': sum(weight * value for weight, value in zip(element_amount, [ele.stats['windows_lines_amount'] for ele in ele_list])) / sum(element_amount),
        'windows_amount': sum(weight * value for weight, value in zip(element_amount, [ele.stats['windows_amount'] for ele in ele_list])) / sum(element_amount),
        'other_lines_amount': sum(weight * value for weight, value in zip(element_amount, [ele.stats['other_lines_amount'] for ele in ele_list])) / sum(element_amount),
        'other_amount': sum(weight * value for weight, value in zip(element_amount, [ele.stats['other_amount'] for ele in ele_list])) / sum(element_amount),
    }
    return ele_average, acc_average


def analyze_repeatability(cat_k: str, cat: list, element_types_report: dict) -> dict:
    """Calculate how many same object are in list of Elements."""

    finished=False
    new_cat=[]
    checked_elem=[]
    while not finished:
        finished=True
        try:
            for elem1 in cat:
                if elem1 not in checked_elem:
                    checked_elem.append(elem1)
                    for group in new_cat:
                        for elem2 in group:
                            if isclose(elem1.volume, elem2.volume, rel_tol=0.002):
                                if isclose(elem1.element_area, elem2.element_area, rel_tol=0.005):
                                    if isclose(elem1.element_length, elem2.element_length, abs_tol=5):
                                        if isclose(elem1.element_width, elem2.element_width, abs_tol=5):
                                            if isclose(elem1.element_height, elem2.element_height, abs_tol=5):
                                                if elem1.project_index == elem2.project_index:
                                                    if isclose(elem1.reinforcement_mass, elem2.reinforcement_mass,
                                                                abs_tol=5):
                                                        if isclose(elem1.mesh_mass, elem2.mesh_mass, abs_tol=5):
                                                            if isclose(elem1.steel_mass, elem2.steel_mass,
                                                                        abs_tol=5):
                                                                if isclose(elem1.stats['acc_amount'],
                                                                            elem2.stats['acc_amount'], rel_tol=0.01):
                                                                    if elem1.strands_bottom_amount == elem2.strands_bottom_amount:
                                                                        if elem1.strands_bottom_diam == elem2.strands_bottom_diam:
                                                                            if elem1.strands_top_amount == elem2.strands_top_amount:
                                                                                if elem1.strands_top_diam == elem2.strands_top_diam:
                                                                                    if len(
                                                                                        elem1.accessories) != 0 and len(
                                                                                        elem2.accessories) != 0:
                                                                                        if min(check_acc_similarity(elem1.accessories, elem2.accessories),
                                                                                    check_acc_similarity(elem2.accessories, elem1.accessories)) > 0.9:
                                                                                            cat.remove(elem1)
                                                                                            group.append(elem1)
                                                                                            finished=False
                                                                                            raise Found
                                                                                    else:
                                                                                        if elem1.stats['lines_amount'] == elem2.stats['lines_amount']:
                                                                                            cat.remove(elem1)
                                                                                            group.append(elem1)
                                                                                            finished=False
                                                                                            raise Found
                    new_cat.append([elem1])
        except Found:
            pass

    unique_elements = len(new_cat)
    if unique_elements == 1:
        repeatability_ratio = 1
    else:
        element_amount = element_types_report[cat_k]['element_amount']
        if element_amount == 0:
            logging.error(f'{cat_k}: amount = 0 {element_types_report[cat_k]}')
            repeatability_ratio = 0
            raise ValueError
        else:
            repeatability_ratio = (element_amount - unique_elements) / element_amount

    element_types_report[cat_k]['unique_element_amount'] = unique_elements
    element_types_report[cat_k]['repeatability_ratio'] = repeatability_ratio

    return element_types_report


def analyze_elements(elements: dict, global_accessories: dict) -> dict:
    """Group elements by element type. Analize stats of each group."""

    element_type_dict=defaultdict(lambda: [])
    [element_type_dict[x.element_type].append(x) for x in elements.values()]  # segregate elements by element type
    
    report={}
    for k, v in element_type_dict.items():  # element group amounts
        report[k]={
            'element_volume': sum(i.amount * i.volume for i in v),
            'element_amount': sum(i.amount for i in v),
            'mark_amount': len(v)
        }


    for cat_k, cat in element_type_dict.items():
        # repeatability
        report = analyze_repeatability(cat_k, cat, report)

        # average acc
        report[cat_k]['avr_element'], report[cat_k]['avr_accessory'] = calc_acc_average(cat)

        # unique acc
        accessories = get_accessories(cat)
        acc_stats = {'unique_' + str(key): val for key, val in Counter(i.type for i in accessories).items()}
        report[cat_k].update(acc_stats)

    return report
