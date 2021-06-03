import sys
import re

def get_entity_sentence_dict(Ojer_output_filename):
    Ojer_output_file = open(Ojer_output_filename, 'r')
    lineno = 0
    entity_sentence_dict = {}
    for line in Ojer_output_file:
        if lineno == 0:
            lineno = 1
            continue
        line = line.rstrip()
        linearr = re.split(r'\t', line)
        ent = linearr[2].strip()
        if ent in entity_sentence_dict:
            entity_sentence_dict[ent].append(line)
        else:
            entity_sentence_dict[ent]=list()
            entity_sentence_dict[ent].append(line)

        lineno+=1

    return entity_sentence_dict

def print_split_files(split_dict, outfilename):
    outfile = open(outfilename, "w")
    outfile.write("Index"+"\t"+"Sentence"+"\t"+"Entity"+"\t"+"Entity_Startindex"+"\t"+"Entity_Stopindex"+"\t"+"Entity_Info"+"\n")
    for entity in split_dict:
        for sentence in split_dict[entity]:
            outfile.write(sentence+"\n")
    outfile.close()

def process_entity_sentence_dict(entity_sentence_dict, entity_count_cutoff):
    breaks = [0.8, 0.9]
    train_dict = {}
    test_dict = {}
    devel_dict = {}
    for entity in entity_sentence_dict:
        entity_count = len(entity_sentence_dict[entity])
        if not entity_count >= entity_count_cutoff:
            continue
        else:
            data_arr = entity_sentence_dict[entity]
            train_break = int(breaks[0] * entity_count)
            test_break = int(breaks[1] * entity_count)
            devel_break = int(1 * entity_count)

            train_dict[entity] = data_arr[0:train_break]
            test_dict[entity] = data_arr[train_break:test_break]
            devel_dict[entity] = data_arr[test_break:devel_break]

    print_split_files(train_dict, sys.argv[2])
    print_split_files(test_dict, sys.argv[3])
    print_split_files(devel_dict, sys.argv[4])

Ojer_output_filename = sys.argv[1]
entity_sentence_dict = get_entity_sentence_dict(Ojer_output_filename)
process_entity_sentence_dict(entity_sentence_dict, 10)
