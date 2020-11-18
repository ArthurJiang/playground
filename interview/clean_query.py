# Problem Description
######################
# Clean query log file, which has a 10 GB (maximum) file size.
#
# Query log formatting:
#   1. One key/value pair per line.
#   2. Key is a timestamp (uint 64).
#   3. Value is a string type, which is less than 128 Bytes.
#   4. Split chart (optional), use one space here.
#
# Clean rules:
#   1. Different key, key keep alphabetical ascending order.
#   2. Same key, different value: value keep alphabetical ascending order.
#   3. Same key, same value: keep one pair.
#
# Extra constraints:
#   1. No distributed support, only run on a single node.
#   2. Memroy is limited: 2 GB.

# Pre-Analysis
#######################
# Line memory range: [8 + 1, 8 + 1 + 128] bytes
# Line/Key number range: [10G / (8 + 1 + 128), 10G / (8 + 1)] ~=> [78.4M, 1.19G]
# Key memory range: ~= [78.4M * 8 Byte, 1.19G * 8 Byte] => [627 MB, 9.52 GB]
# Line index minimum type: uint32 (0 ~ 4.30G)
# Key + index memory range: ~= [940 MB, 14.28 GB]

# Assumption for Problem Simplifying
#####################################
# 1. Ignore the worst case (only has key, no value).
# 2. Key and index can be host in the memory.
# 3. Use python mimic the main logic, ignore python int object need more memory and its bad performance.

# Others
#########
# 1. If key and index could not be host in the memory, can adopt other external sorting algorithms.
# 2. Multi-nodes can also be adopted.
# 3. Could not handle some extreme case, such as very short query length and most of the timestamp are same, which may adopt hyperloglog.

# Implementation
#################
import linecache
import math
import os
import random
import string
import time

TOTAL_LINES = 10000
MIN_QUERY_LENGTH = 4
MAX_QUERY_LENGTH = 4
CHARSET = ['a', 'b', 'c'] # string.ascii_letters
TIMESTAMP_DELTA = 500 # 0 is a challenge case here
QUERY_LOG = './raw_query.log'
SPLIT_STEP = 100

SPLIT_FOLDER = './splitted_query_logs'
SORT_FOLDER = './sortted_query_logs'
FINALLY_SORT_FILE = './sortted_query.log'

# Helpper
def execution_time(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        print(f'{func.__name__} run time is {round((time.time() - start) / 60, 2)} min')
        return res
        
    return wrapper

# 1. Mock data.
@execution_time
def generate_mock_query_log(target_file: str = QUERY_LOG,
                            total_lines: int = TOTAL_LINES,
                            min_query_length: int = MIN_QUERY_LENGTH,
                            max_query_length: int = MAX_QUERY_LENGTH,
                            charset: [] = CHARSET) -> str:
    with open(target_file, 'w') as fw:
        for i in range(total_lines):
            current_query_length = random.randint(min_query_length, max_query_length)
            random_query = ''.join(random.choice(charset) for i in range(current_query_length))
            random_timestamp = int(time.time()) + random.randint(-TIMESTAMP_DELTA, TIMESTAMP_DELTA)
            fw.write(f'{random_timestamp} {random_query}\n')

    return target_file

# 2. Load key and index, sort the list, and split it.
@execution_time
def build_splitted_key_index_lists(source_file: str = QUERY_LOG,
                                   split_step: int = SPLIT_STEP) -> [[(int, int)]]:
    # Step 1, Load key and line index.
    key_index_list = []
    with open(source_file, 'r') as fr:
        # TODO: Use read(size) for finetuning
        for index, line in enumerate(fr.readlines()):
            key_index_list.append((line.split(' ')[0], index+1))

    # Step 2, Sort by key.
    sorted_key_index_list = sorted(key_index_list, key=lambda key_index: key_index[0])

    # Step 3, Split key_index_list by split_step.
    # TODO: auto split, need handel most key are same
    assert(split_step <= len(sorted_key_index_list))
    splitted_key_index_lists = []

    for i in range(math.ceil(len(sorted_key_index_list)/split_step)):
        splitted_key_index_lists.append(sorted_key_index_list[i * split_step: (i + 1) * split_step])

    return splitted_key_index_lists


# 3. Split the original big file.
@execution_time
def split_file(source_file: str = QUERY_LOG,
               target_path: str = SPLIT_FOLDER,
               splitted_key_index_lists: [[(int, int)]] = None) -> [str]:
    if not os.path.exists(target_path):
        os.makedirs(target_path)

    splitted_files = []
    for file_index, key_index_list in enumerate(splitted_key_index_lists):
        splitted_file = f'{target_path}/{file_index}.log'
        with open(splitted_file, 'w') as fw:
            for key, index in key_index_list:
                fw.write(linecache.getline(source_file, index))

        splitted_files.append(splitted_file)

    return splitted_files



# 3. Sort each sub-file.
@execution_time
def sort_sub_files(sub_file_list: [str],
                   target_path: str = SORT_FOLDER):
    if not os.path.exists(target_path):
        os.makedirs(target_path)

    sortted_sub_file_list = []
    for file_index, sub_file in enumerate(sub_file_list):
        with open(sub_file, 'r') as fr:
            kv_list = []
            for line in fr.readlines():
                kv_list.append((line.split(' ')[0], ''.join(line.split(' ')[1:]).strip()))
            
            sortted_kv_list = sorted(kv_list)
            target_file = f'{target_path}/{file_index}.log'

            with open(target_file, 'w') as fw:
                for key, value in sortted_kv_list:
                    fw.write(f'{key} {value}\n')

            sortted_sub_file_list.append(target_file)

    return sortted_sub_file_list

# 4. Merge the sub-files.
@execution_time
def merge_sub_files(target_file: str = FINALLY_SORT_FILE, sortted_sub_file_list: [str] = None):
    # TODO: Use hyperloglog remove duplicated case with an acceptable error rate.
    last_line = None
    with open(target_file, 'w') as fw:
        for sub_file in sortted_sub_file_list:
            with open(sub_file, 'r') as fr:
                for cur_line in fr.readlines():
                    if last_line != cur_line:
                        fw.write(cur_line)
                        last_line = cur_line

    return target_file

if __name__ == '__main__':
    cleaned_file = merge_sub_files(sortted_sub_file_list=
                        sort_sub_files(sub_file_list=
                            split_file(splitted_key_index_lists=
                                build_splitted_key_index_lists(source_file=
                                    generate_mock_query_log()))))

    print('==================================')
    print(f'Total lines: {TOTAL_LINES}')
    print(f'Split step: {SPLIT_STEP}')
    print(f'Query length range: [{MIN_QUERY_LENGTH}, {MIN_QUERY_LENGTH}]')
    print(f'Charset: {CHARSET}')
    print(f'Timestamp delta: {TIMESTAMP_DELTA}')
    print(f'Final file: {cleaned_file}')