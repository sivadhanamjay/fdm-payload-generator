import ast
import shelve
import traceback
import colorama
import argparse
import json
from utilities.logger import Logger
from utilities.gen_utils import gen_ts

from engine.payloadEngine import PayloadEngine


if __name__ == "__main__":
    colorama.init()

    # Argument parsing
    parser = argparse.ArgumentParser(description='Generate JSON payload from exchange format.')
    parser.add_argument('input',
                        help="The json file(s) to use for generation. Can point to a specific file, or folder " +
                             "containing the files.",
                        type=str)

    parser.add_argument('type',
                        type=str,
                        choices=['bnc', 'Triumph', 'cfe', 'oscc'],
                        help='The type of files being created')

    parser.add_argument('-o', '--output_path',
                        type=str,
                        default=None,
                        help="This overrides the default output directory set by the data_stage. Generated payload JSON" +
                             "files will be written to this directory.")

    args = parser.parse_args()
    input_file_path = args.input
    output_type = args.type
    output_path = args.output_path

    # print(input_file_path)

    logger = Logger(log_file_path='./logs/' + gen_ts() + '.log')

    # Define output path if not provided as argument
    if not output_path:
        output_path = './output/'
    try:
        logger.status("\n" +
                      'Payload JSON Generator' + '\n' +
                      '------------------' + '\n' +
                      'Type:\t\t' + output_type + '\n' +
                      'Output Path:\t' + output_path + '\n' +
                      'Log File:\t' + logger.log_file_path + '\n')

        if output_type == 'Triumph':
            mapping_path = 'mappings/MappingTriumph.json'
        elif output_type == 'cfe':
            mapping_path = 'mappings/MappingCfe.json'
        elif output_type == 'oscc':
            mapping_path = 'mappings/MappingOscc.json'
        else:
            raise Exception('Output type (' + output_type + ') not recognized.')

        mapping_object= json.load(open(mapping_path,'r'))
        
        logger.status(f'passing input path: {input_file_path}, mapping file dict: {mapping_object}, logger obj to the generic '
                      f'method')

        
        payloadEngine = PayloadEngine(input_file_path=input_file_path, mapping_object=mapping_object,
                                                    mapping_type=output_type, logger=logger)
        payloadEngine.generate_payload()
        payloadEngine.convert_to_json()

    except Exception as e:
        _ = e
        logger.error(traceback.format_exc())
