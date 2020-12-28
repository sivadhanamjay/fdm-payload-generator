import os
import json
import colorama
import traceback

from utilities.logger import Logger
from utilities.gen_utils import gen_ts

class PayloadEngine:

    def __init__(self, input_file_path, mapping_object, mapping_type, logger):
        self.logger = logger
        self.mapping_type = mapping_type
        self.mapping_object = mapping_object
        self.input_file_path = input_file_path
        

    INPUT_RESOURCE_ID_DIST = {
        'Triumph': 'ingest file data container',
        'cfe': 'qwerty_triumph'
        }


    INPUT_RESOURCE_TYPE_DIST = {
        'Triumph': 'Ingest file',
        'cfe': 'qwerty_cfe'
        }

    GENERIC_DISCT = {
        'INPUT_RESOURCE_ID': INPUT_RESOURCE_ID_DIST,
        'RESOURCE_TYPE': INPUT_RESOURCE_TYPE_DIST
        }


    output = dict()

    
    @staticmethod
    def reformat_oscc_file(input_file, input_file_object, mapping_object, logger):
        """
        """
        print(input_file['tags'])
        input_file['tags'] = ['pii', 'cde']
        bdy_array = input_file['records'][0]
        input_file['records'] = bdy_array
        bdy_object = input_file['records']['bdy']
        bdy = dict()
        for obj in bdy_object:
            data = obj['data']
            obj['tags'] = []
            key = obj['key']
            del obj['key']
            del obj['data']
            bdy[key] = obj
        data['properties'] = {}
        bdy['data'] = data
        input_file['records']['bdy'] = bdy

        temp = {}
        da_cntn_resrce = input_file_object['da_cntn_resrce']
        for cont in da_cntn_resrce:
            temp[cont['da_cntn_tech_nm']] = {}
            temp[cont['da_cntn_tech_nm']]['resourceID'] = cont['da_cntn_resrce_id']
            temp[cont['da_cntn_tech_nm']]['resourceVersion'] = cont['da_cntn_vsn_id']
            temp[cont['da_cntn_tech_nm']]['resourceType'] = 'datactr'
            temp[cont['da_cntn_tech_nm']]['type'] = 'object'
            temp[cont['da_cntn_tech_nm']]['properties'] = {}

            for attr in cont['attr_resrce']:
                temp[cont['da_cntn_tech_nm']]['properties'][attr['attr_tech_nm']] = {}
                temp[cont['da_cntn_tech_nm']]['properties'][attr['attr_tech_nm']]['resourceID'] = attr['attr_resrce_id']
                temp[cont['da_cntn_tech_nm']]['properties'][attr['attr_tech_nm']]['resourceVersion'] = attr[
                    'da_cntn_vsn_id']
                temp[cont['da_cntn_tech_nm']]['properties'][attr['attr_tech_nm']]['resourceType'] = attr[
                    'attr_da_type_cd']
                temp[cont['da_cntn_tech_nm']]['properties'][attr['attr_tech_nm']]['name'] = attr['attr_bus_nm']
                temp[cont['da_cntn_tech_nm']]['properties'][attr['attr_tech_nm']]['type'] = attr['attr_da_type_cd']
                temp[cont['da_cntn_tech_nm']]['properties'][attr['attr_tech_nm']]['format'] = attr['attr_da_frmt_cd']
                temp[cont['da_cntn_tech_nm']]['properties'][attr['attr_tech_nm']]['tags'] = []
                temp[cont['da_cntn_tech_nm']]['properties'][attr['attr_tech_nm']]['description'] = attr['attr_def']

        input_file['records']['bdy']['data']['properties'] = mapping_object['data_map']
        import pdb;pdb.set_trace()
        input_file['records']['bdy']['data'] = temp['data']
        input_file['records']['bdy']['data']['properties']['platform'] = temp['platform']
        input_file['records']['bdy']['data']['properties']['application'] = temp['application']
        input_file['records']['bdy']['data']['properties']['journey'] = temp['journey']
        input_file['records']['bdy']['data']['properties']['journey']['properties']['channel'] = temp['channel']
        input_file['records']['bdy']['data']['properties']['fulfiller'] = temp['fulfiller']
        input_file['records']['bdy']['data']['properties']['customerInfo'] = temp['customerInfo']
        input_file['records']['bdy']['data']['properties']['customerInfo']['properties']['accountDetails'] = temp[
            'accountDetails']
        input_file['records']['bdy']['data']['properties']['servicingDetail'] = temp['servicingDetail']
        input_file['records']['bdy']['data']['properties']['servicingDetail']['properties']['creditDetail'] = temp[
            'creditDetail']
        input_file['records']['bdy']['data']['properties']['servicingDetail']['properties']['creditDetail']['properties'][
            'programDetails'] = temp['programDetails']
        return input_file


    def write_to_file(self, output_final_dict, file_type):
        """
        Write output file into .json file
        """

        directory = './output/'+file_type+'/'
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(f'./output/{file_type}/payload_{file_type}_{gen_ts()}.json', 
                'w',
                encoding='utf-8') as f:
            json.dump(output_final_dict, f, ensure_ascii=False, indent=4)


    def convert_to_json(self):
        """ 
        Used to convert to json from dictionary 
        """

        input_file_object = self.get_dict_from_input(self.input_file_path)
        try:
            self.output = getattr(self, 'reformat_'+self.mapping_type+'_file')(
                                self.output, 
                                input_file_object, 
                                self.mapping_object, 
                                self.logger
                                )
            self.logger.info("applying custom reformat: reformat_{}_file ".format(self.mapping_type))
        except Exception as e:
            self.logger.info("applying default reformat: 'reformat_input_file' ")

        self.write_to_file(self.output, self.mapping_type)
        

    def get_dict_from_input(self, input_file_path):
        """ 
        Return dictionary from the given input file path which has json file 
        """

        with open(input_file_path) as f:
            input_exchange_container_dict = json.load(f)
            # input_exchange_container_json = json.dumps(input_exchange_container_dict, indent=3)
            # self.logger.status(f'input_exchange_container_json: {input_exchange_container_json}')
        return input_exchange_container_dict


    def get_value_for_key(self, input_dict, attribute):
        """ 
        Will return the value for the given key from the dictionary 
        """

        return input_dict[attribute]

    def generate_payload(self):
        """

        """
        input_dict = self.get_dict_from_input(self.input_file_path)
        mapping_object = self.mapping_object
        mapping_type = self.mapping_type
        for key in mapping_object[mapping_type]:
            self.add_each_key(key, mapping_object, mapping_type, input_dict, "na", 0, "na", False)

    def add_each_key(self, key, input_mapping, mapping_type, input_dict, insert_type, index, obj_key, is_return):
        if insert_type == 'na':
            mapping_value = str(input_mapping[mapping_type][key])
        else:
            mapping_value = input_mapping[obj_key][key]
        if isinstance(mapping_value, list):
            newKey = mapping_value[0]
            condition = mapping_value[1]
            if newKey.startswith('$'):
                cond_array = condition.split(".")
                array_value = self.map_value_from_input(condition[6:], input_mapping, input_dict, "array")
                current_array = self.get_value_for_key(input_mapping, newKey[1:])
                counter = 0
                self.output[mapping_type][index][key] = []
                for value in array_value:
                    self.output[mapping_type][index][key].append({})
                    for key_obj in current_array:
                        if current_array[key_obj].startswith('CONST.'):
                            self.output[mapping_type][index][key][counter][key_obj] = current_array[key_obj][6:]
                        elif current_array[key_obj] == "null":
                            self.output[mapping_type][index][key][counter][key_obj] = ""
                        elif current_array[key_obj].startswith('&'):
                            self.output[mapping_type][index][key][counter][key_obj] = {}
                            for key1 in input_mapping[current_array[key_obj][1:]]:
                                temp_value = self.add_each_key(key1,
                                                                input_mapping,
                                                                current_array[key_obj][1:],
                                                                input_dict,
                                                                "na",
                                                                0,
                                                                "na",
                                                                True)
                                self.output[mapping_type][index][key][counter][key_obj][key1] = temp_value
                        else:
                            self.output[mapping_type][index][key][counter][key_obj] = value[current_array[key_obj]]
                    counter += 1
        else:
            if mapping_value.startswith("["):
                newKey = input_mapping[mapping_type][key][0]
                if newKey.startswith('#'):
                    counter = 0
                    key_value = newKey[1:]
                    if not newKey[1:].startswith('+'):
                        self.output[key] = []
                    else:
                        key_value = newKey[2:]
                    for x in self.get_value_for_key(input_mapping, key_value):
                        if newKey[1:].startswith('+'):
                            self.output[key] = {}
                        else:
                            self.output[key].append({})

                        for y in self.get_value_for_key(input_mapping, x[1:]):
                            self.add_each_key(y, input_mapping, key, input_dict, "object", counter, x[1:], False)
                        counter += 1
            elif mapping_value.startswith('CONST!'):
                if insert_type == 'na':
                    return self.GENERIC_DISCT[mapping_value[(mapping_value.index('CONST!') + 6):]][mapping_type]
                else:
                    self.output[mapping_type][index][key] = \
                        self.GENERIC_DISCT[mapping_value[(mapping_value.index('CONST!') + 6):]][mapping_type]
            elif mapping_value.startswith('APPL.'):
                if is_return:
                    return self.map_value_from_input(
                                    mapping_value[(mapping_value.index('APPL.') + 5):],
                                    input_mapping,
                                    input_dict,
                                    "object"
                                    )
                elif insert_type == 'na':
                    self.output[key] = self.map_value_from_input(
                                            mapping_value[(mapping_value.index('APPL.') + 5):],
                                            input_mapping,
                                            input_dict,
                                            "object"
                                            )
                else:
                    self.output[mapping_type][index][key] = self.map_value_from_input(
                                                                mapping_value[(mapping_value.index('APPL.') + 5):],
                                                                input_mapping,
                                                                input_dict,
                                                                "object"
                                                                )
            elif mapping_value.startswith('ARRAY.'):
                if is_return:
                    return self.map_value_from_input(
                                                    mapping_value[(mapping_value.index('ARRAY.') + 6):],
                                                    input_mapping,
                                                    input_dict,
                                                    "array"
                                                    )
                elif insert_type == 'na':
                    self.output[key] = self.map_value_from_input(
                                            mapping_value[(mapping_value.index('ARRAY.') + 6):],
                                            input_mapping,
                                            input_dict,
                                            "array"
                                            )
                else:
                    self.output[mapping_type][index][key] = self.map_value_from_input(
                                                                mapping_value[(mapping_value.index('ARRAY.') + 6):],
                                                                input_mapping,
                                                                input_dict,
                                                                "array"
                                                                )
            elif mapping_value == "null":
                if is_return:
                    return ""
                elif insert_type == 'na':
                    self.output[key] = ""
                else:
                    self.output[mapping_type][index][key] = ""
            elif mapping_value.startswith('CONST.'):
                if is_return:
                    return mapping_value[(mapping_value.index('CONST.') + 6):]
                elif insert_type == 'na':
                    self.output[key] = mapping_value[(mapping_value.index('CONST.') + 6):]
                else:
                    self.output[mapping_type][index][key] = mapping_value[(mapping_value.index('CONST.') + 6):]


    def map_value_from_input(self, mapping, input_mapping, input_dict, data_type):
        """
        Used to walk the json based on dot operator
        """

        mapping_array = mapping.split(".")
        temp_arr = input_dict
        for item in mapping_array[:len(mapping_array) - 1]:
            temp_arr = temp_arr[item]

        if data_type == "object":
            return temp_arr[mapping_array[len(mapping_array) - 1]]

        array_map = mapping_array[len(mapping_array) - 1].split('$')

        extra_check = ""
        extra_check_required = False
        if array_map[2].startswith("[") and array_map[2].endswith("]"):
            extra_cond = array_map[2][1:len(array_map[2]) - 1].split("|")
            temp_arr_after = input_dict
            for y in extra_cond[:len(extra_cond) - 1]:
                temp_arr_after = temp_arr_after[y]

            extra_check_required = True
            extra_check = temp_arr_after[extra_cond[len(extra_cond) - 1]]

        for arr in temp_arr:
            if extra_check_required:
                if arr[array_map[1]] == extra_check:
                    return arr[array_map[0]]
            else:
                if arr[array_map[1]] == array_map[2]:
                    return arr[array_map[0]]
        return
