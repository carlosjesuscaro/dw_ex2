import json
import logging

logger = logging.getLogger(__name__)


class Datawalk:
    def __init__(self, obj_id: int, obj_name: str, obj_virtual: bool, attr_name: str):
        self.id = obj_id
        self.name_obj = obj_name
        self.virtual = obj_virtual
        self.name_attr = attr_name


class DataError(Exception):
    pass


def read_json(path: str) -> dict:
    """Reads the JSON file from the path provided
    Args:
        path: path to the JSOn file

    Raises:
        DataError: if there is any issue when reading the JSON file

    Returns:
        data: dictionary with the content from the JSON file
    """
    try:
        with open(path, 'r') as file:
            data_json = json.load(file)
        return data_json
    except DataError:
        logger.error('There was an issue')


def data_traversing(data: dict) -> list[list[Datawalk], list[str]]:
    """Loads the data dictionary to a list of Datwalk objects with the relevant fields
    Args:
        data: deserialized data from the JSON file

    Returns:
        dw_objs: list of objects with the required fields to remap the data into a new format
        attr_list: list of attribute names
    """
    dw_objs = []
    attr_list = []
    for key, value in data['classes'].items():
        if int(key) == value['id']:
            attr_list.append(value['name'])
            [dw_objs.append(Datawalk(x['id'], x['name'], x['virtual'], value['name'])) for x in value['attributes']]
        else:
            logger.warning("Misalignment between key: %s and value ID: %d", key, value['id'])
    return [dw_objs, attr_list]


def remap(parsed_data: list) -> dict:
    objs, attrs = parsed_data[0], parsed_data[1]
    dict_maps = {"classes_with_virtual_attributes": [], "classes_without_virtual_attributes": []}
    for obj in objs:
        new_dict = {}
        new, index = 0, 0
        class_type = 'classes_with_virtual_attributes' if obj.virtual else 'classes_without_virtual_attributes'
        for i in range(len(dict_maps[class_type])):
            if obj.name_attr == dict_maps[class_type][i]['name']:
                new, index = 1, i
                break
        if new == 0:
            new_dict['name'] = obj.name_attr
            new_dict['attributes'] = [{"name": obj.name_obj, "id": obj.id}]
            dict_maps[class_type].append(new_dict)
        else:
            new_dict['attributes'] = {"name": obj.name_obj, "id": obj.id}
            dict_maps[class_type][index]['attributes'].append(new_dict['attributes'])
    return dict_maps


def write_json(data: dict) -> None:
    with open('data/result.json', 'w') as f:
        json.dump(data, f)
