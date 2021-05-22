import pandas as pd
import re
import sys

def get_cleaned_tagged_ner_df(temp_df):
    ne_df = temp_df[2].str.split('\d+', n=1, expand=True)
    # print(tagged_ner_df.iloc[:, 2])
    temp_df_cleaned = pd.DataFrame()
    temp_df_cleaned['sentence'] = temp_df.iloc[:, 1]
    temp_df_cleaned['entity'] = ne_df.iloc[:, 0]
    return temp_df_cleaned

def read_oger_ner_output(inputfilename):
    oger_ner_output_df = pd.read_csv(inputfilename, sep="\t", header=0)
    oger_ner_output_clean_df = pd.DataFrame()
    oger_ner_output_clean_df['sentence'] = oger_ner_output_df['Sentence']
    oger_ner_output_clean_df['entity'] = oger_ner_output_df['Entity']

    return oger_ner_output_clean_df


def tokenize_sentence_for_BIO(sentence):
    sentence = sentence.strip()
    sentence_arr = re.split(r'\s+', sentence)
    tokenize_sentence_arr = list()
    for word in sentence_arr:
        if not re.search(r'\W', word):
            tokenize_sentence_arr.append(word)
            continue
        word_arr = list(word)
        word_str = ""

        for ch in word_arr:
            if re.match(r'\W', ch):
                if len(word_str) > 0:
                    tokenize_sentence_arr.append(word_str)
                    word_str = ""
                tokenize_sentence_arr.append(ch)

            else:
                word_str = word_str+ch

        if len(word_str) > 0:
            tokenize_sentence_arr.append(word_str)
            word_str = ""
    return tokenize_sentence_arr

def prepare_tokenized_sentence_BIO_arr(tokenized_sentence):
    tokenized_sentence_BIO_arr = list()
    for tk in tokenized_sentence:
        tokenized_sentence_BIO_arr.append([tk, 'O'])

    return tokenized_sentence_BIO_arr


def get_BIO_tagged_tokenized_sentence(tokenized_sentence, tokenized_sentence_BIO_tagged, tokenized_ne, entity_tag):
    i = 0
    while i < len(tokenized_sentence):
        if (tokenized_sentence[i] == tokenized_ne[0]) and (i <= len(tokenized_sentence) - len(tokenized_ne)):
            ne_flag = 1
            sent_token_counter = i
            for ne_token in tokenized_ne:
                if not ne_token == tokenized_sentence[sent_token_counter]:
                    ne_flag = 0
                    break
                sent_token_counter += 1
            if ne_flag == 1:
                for j in range(0, len(tokenized_ne)):
                    if j == 0:
                        #tokenized_sentence_BIO_tagged[i + j][1] = 'B-' + entity_tag
                        tokenized_sentence_BIO_tagged[i + j][1] = 'B'
                    else:
                        #tokenized_sentence_BIO_tagged[i + j][1] = 'I-' + entity_tag
                        tokenized_sentence_BIO_tagged[i + j][1] = 'I'
                i += len(tokenized_ne)
            else:
                i += 1
        else:
            #tokenized_sentence_BIO_tagged[i][1] = 'O'
            i += 1
    return tokenized_sentence_BIO_tagged

def print_tokenized_sentence_BIO_tagged(master_dict, outfilename):
    outfile = open(outfilename, "w")
    for sentence in master_dict:
        for token in master_dict[sentence]['tok_sentence_BIO_arr']:
            outfile.write(token[0]+"\t"+token[1]+"\n")
        outfile.write("\n")
    outfile.close()


def process_tagged_ner_df(temp_df):
    master_dict = {}
    for index, row in temp_df.iterrows():
        sentence = row['sentence'].strip()
        entity = row['entity'].strip()
        tokenized_ne = tokenize_sentence_for_BIO(entity)
        if sentence in master_dict:
            master_dict[sentence]['entity'].append(tokenized_ne)
        else:
            master_dict[sentence] = {}
            tokenized_sentence = tokenize_sentence_for_BIO(sentence)
            master_dict[sentence]['tok_sentence'] = tokenized_sentence
            master_dict[sentence]['tok_sentence_BIO_arr'] = prepare_tokenized_sentence_BIO_arr(tokenized_sentence)
            master_dict[sentence]['entity'] = list()
            master_dict[sentence]['entity'].append(tokenized_ne)

    return master_dict


def process_master_dict(master_dict, entity_tag):
    for sentence in master_dict:
        for tok_entity in master_dict[sentence]['entity']:
            master_dict[sentence]['tok_sentence_BIO_arr'] = get_BIO_tagged_tokenized_sentence(
                master_dict[sentence]['tok_sentence'],
                master_dict[sentence]['tok_sentence_BIO_arr'],
                tok_entity,
                entity_tag)

    return master_dict


tagged_ner_df = read_oger_ner_output(sys.argv[1])
outfile_file = sys.argv[2]
entity_tag = sys.argv[3]
master_dict = process_tagged_ner_df(tagged_ner_df)
master_dict = process_master_dict(master_dict, entity_tag)
print_tokenized_sentence_BIO_tagged(master_dict, outfile_file)



