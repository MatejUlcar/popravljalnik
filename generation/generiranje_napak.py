### generiranje napak
import random
import json
import os
import os.path
from tqdm import tqdm

# load sloleks
# load corpus
#sloleks_file = "/home/matej/Embeddia/Sloleks2.0.MTE/sloleks_clarin_2.0-sl.tbl"

def load_sloleks(filename="/home/matej/Embeddia/Sloleks2.0.MTE/sloleks_clarin_2.0-sl.tbl"):
    """Reads sloleks in tbl format, outputs dictionary of dictionaries, where top level keys are neutral/indefinite forms of words,
       and second level keys are Multext-East Slovene MSDs, value is the word form of the key word for the given gender/case/etc. code."""
    sloleks = {}
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip().split('\t')
            if '*' in line[-1]:
                continue
            if not line[1] in sloleks:
                sloleks[line[1]] = {}
            sloleks[line[1]][line[2]] = line[0]
    return sloleks
# iterate corpus
# for each sentence
# if word/its lemma in sloleks and has wanted msd
# then replace it with word with changed msd (eg. sing->plural)
# fi
# add original sentence, new sentence and err code in dataset
all_categories = {'O/KAT/sklon-rt', 'O/KAT/sklon-dm', 'O/KAT/sklon-mo', 'O/KAT/število-em', 'O/KAT/število-dm', 'O/KAT/število-ed', 'O/KAT/spol',
                  'O/KAT/vid', 'O/KAT/čas', 'O/KAT/oseba', 'O/KAT/nedoločnik-kratki', 'O/KAT/nedoločnik-namenilnik', 'O/KAT/nedoločnik-osebna',
                  'O/KAT/naklon', 'O/KAT/način', 'O/KAT/oblika_zaimka', 'O/KAT/določnost', 'O/KAT/stopnjevanje'} # except problematic

verb_categories = {'O/KAT/število-em', 'O/KAT/število-dm', 'O/KAT/število-ed', 'O/KAT/spol', 'O/KAT/vid', 'O/KAT/čas', 'O/KAT/oseba',
                   'O/KAT/nedoločnik-kratki', 'O/KAT/nedoločnik-namenilnik', 'O/KAT/nedoločnik-osebna', 'O/KAT/naklon', 'O/KAT/način'}

noun_categories = {'O/KAT/sklon-rt', 'O/KAT/sklon-dm', 'O/KAT/sklon-mo', 'O/KAT/število-em', 'O/KAT/število-dm', 'O/KAT/število-ed', 'O/KAT/spol'}

adject_categories = {'O/KAT/sklon-rt', 'O/KAT/sklon-dm', 'O/KAT/sklon-mo', 'O/KAT/število-em', 'O/KAT/število-dm', 'O/KAT/število-ed', 'O/KAT/spol',
                     'O/KAT/oblika_zaimka', 'O/KAT/določnost', 'O/KAT/stopnjevanje'}

problematic_categories = {'O/KAT/sklon-drugo', 'O/KAT/povratnost'} # plus others

currently_supported_categories = {'O/KAT/sklon-rt', 'O/KAT/sklon-dm', 'O/KAT/sklon-mo', 'O/KAT/število-em', 'O/KAT/število-dm', 'O/KAT/število-ed', 'O/KAT/spol', 'O/KAT/vid', 'O/KAT/oseba'} # WIP
# TODO: čas, nedoločniki-vsi, naklon, način, oblika_zaimka, določnost, stopnjevanje
# TODO: NOTE! most of above (if not all) can not be easily done automatically, but only carefully manually, so... probably skip them


def change_gram_case(msd, case1, case2):
    #if msd[0] == 'D': # predlog
        #k = 1
    if msd[0] == 'S': # samostalnik
        k = 4
    elif msd[0] in 'PZK': # pridevnik, zaimek, stevnik
        k = 5
    else:
        k = -1
    if k > 0 and k < len(msd):
        if msd[k] == case1:
            newmsd = msd[:k]+case2+msd[k+1:]
        elif msd[k] == case2:
            newmsd = msd[:k]+case1+msd[k+1:]
        else:
            newmsd = msd
    else:
        newmsd = msd
    # handle animate in nouns, masculine, accusative. remove feature when changing case
    if k == 4 and msd[2] == 'm':
        if msd[k] == 't':
            newmsd = newmsd[:-1]
        elif newmsd[k] == 't':
            newmsd += 'n'
    return newmsd

def change_number(msd, num1, num2):
    if msd[0] == 'S':
        k = 3
    elif msd[0] == 'G':
        k = 5
    elif msd[0] in 'PZK':
        k = 4
    else:
        k = -1
    if k > 0 and k < len(msd):
        if msd[k] == num1:
            newmsd = msd[:k]+num2+msd[k+1:]
        elif msd[k] == num2:
            newmsd = msd[:k]+num1+msd[k+1:]
        else:
            newmsd = msd
    else:
        newmsd = msd    
        
    return newmsd

def change_gender(msd):
    genders = ['m', 'z', 's']
    if msd[0] == 'S':
        k = 2
    elif msd[0] == 'G':
        k = 6
    elif msd[0] in 'PZK':
        k = 3
    else:
        k = -1
    if k > 0 and k < len(msd):
        g1 = msd[k]
        try:
            g2_idx = (genders.index(g1)+random.randint(0,1)) % 3
            g2 = genders[g2_idx]
        except ValueError:
            g2 = g1
        newmsd = msd[:k]+g2+msd[k+1:]
    else:
        newmsd = msd
            
    return newmsd

def change_vid(msd):
    if msd[0] == 'G':
        k = 2
        if msd[k] == 'd':
            newmsd = msd[:k]+'n'+msd[k+1:]
        elif msd[k] == 'n':
            newmsd = msd[:k]+'d'+msd[k+1:]
    else:
        newmsd = msd
    return msd

def change_person(msd):
    persons = ['p', 'd', 't']
    if msd[0] == 'G':
        k = 4
    elif msd[0] == 'Z':
        k = 2
    else:
        k = -1
    if k > 0 and k < len(msd):
        g1 = msd[k]
        try:
            g2_idx = (persons.index(g1)+random.randint(0,1)) % 3
            g2 = persons[g2_idx]
        except ValueError:
            g2 = g1
        newmsd = msd[:k]+g2+msd[k+1:]
    else:
        newmsd = msd
    return newmsd

def random_cat_mistake(lemma, msd, categories, sloleks):
    # find what categories are applicable for given msd
    # select one category at random
    # replace msd with new msd for the chosen category if any, else keep same msd
    # generate new word from given lemma and newmsd
    # return generated new word and chosen category if any else ''/none
    pass

def generate_cat_mistake(lemma, msd, category, sloleks, word):
    if category.startswith('O/KAT/sklon'):
        case1 = category[-2]
        case2 = category[-1]
        newmsd = change_gram_case(msd, case1, case2)
    elif category.startswith('O/KAT/število'):
        num1 = category[-2]
        num2 = category[-1]
        newmsd = change_number(msd, num1, num2)
    elif category.startswith('O/KAT/spol'):
        newmsd = change_gender(msd)
    elif category.startswith('O/KAT/vid'):
        newmsd = change_vid(msd)
    elif category.startswith('O/KAT/oseba'):
        newmsd = change_person(msd)
    else:
        return word

    if newmsd not in sloleks[lemma]:
        #print(lemma, msd, newmsd, category)
        # handle (in)animate property in nouns, masculine, accusative
        if newmsd[0] == 'S' and len(newmsd) == 6 and newmsd[-1] == 'n':
            newmsd = newmsd[:-1]+'d'
        newmsd = newmsd.split('--')[0]
    if newmsd in sloleks[lemma]:
        newword = sloleks[lemma][newmsd]
    else:
        newword = word
    if word.istitle():
        newword = newword.title()
    elif word.isupper():
        newword = newword.upper()
    return newword
    #print(lemma, msd, newmsd, category, case1, case2)
    #return sloleks[lemma][msd]


def iterate_conllu(corpus_filepath, sloleks):
    dataset = []
    curr_category = ''
    avail_verb_cats = list(verb_categories & currently_supported_categories)
    avail_noun_cats = list(noun_categories & currently_supported_categories)
    avail_adje_cats = list(adject_categories & currently_supported_categories)
    verb_weights = [6 if vc=='O/KAT/vid' else 2 if vc=='O/KAT/oseba' else 1 for vc in avail_verb_cats]
    with open(corpus_filepath, 'r') as f:
        new_sent = ''
        category = set()
        for line in f:
            if line.startswith('# text ='):
                if len(new_sent.split()) > 3 and len(category) > 0:
                    dataset.append({'orig': new_sent.rstrip(), 'corr': orig_sentence, 'category': list(category)}) # here, we create new originals by generating mistakes, and new corrected as copying actual "original" sentences.
                orig_sentence = line.strip().replace('# text = ','')
                new_sent = ''
                category = set()
            elif line.startswith('#') or len(line) < 3:
                continue
            else:
                line = line.strip().split('\t')
                word = line[1]
                lemma = line[2]
                msd = line[4]
                # TODO: add some sampling, do not always apply cat mistake, keep some words intact, some random...
                r0 = random.random()
                r1 = random.random()
                if lemma in sloleks and ((msd[0]=='G' and r0<0.4) or r0 < 0.15):
                    if msd[0] == 'G':
                        if curr_category not in verb_categories or r1 < 0.7:
                            curr_category = random.choices(avail_verb_cats, weights=verb_weights, k=1)[0]
                    elif msd[0] == 'S':
                        if curr_category not in noun_categories or r1 < 0.3: # keep same category if applicable, to better represent PS, KS, ZS combos, but only with some (high) probability
                            curr_category = random.choice(avail_noun_cats) #(noun_categories)
                    elif msd[0] in 'PRZK':
                        # TODO: consider adding same as above, keeping existing category
                        if curr_category not in adject_categories or r1 < 0.4:
                            curr_category = random.choice(avail_adje_cats) #(adject_categories)
                    #else:
                    #    curr_category = random.choice(list(currently_supported_categories)) #(all_categories)

                    newword = generate_cat_mistake(lemma, msd, curr_category, sloleks, word)

                    if newword != word:
                        category.add(curr_category)
                else:
                    newword = word

                new_sent += newword+' '*('SpaceAfter=No' not in line[-1])

        if len(new_sent.split()) > 3 and len(category) > 0: # last buffer, after loop ends
            dataset.append({'orig': new_sent.rstrip(), 'corr': orig_sentence, 'category': list(category)}) # here, we create new originals by generating mistakes, and new corrected as copying actual "original" sentences.
            orig_sentence = line.strip().replace('# text = ','')
            new_sent = ''
    return dataset

def main():
    sloleks = load_sloleks()
    with open('generated_data_v2.jsonl', 'w') as writer:
        for dirpath, dirnames, filenames in os.walk('/home/matej/GigaDisk/crkovalnik/maks/maks.conllu/'):
            for f in tqdm(filenames, total=1327):
                if f.endswith('.conllu'):
                    corpus = os.path.join(dirpath, f)
                    writer.write('#newdoc\n')
                    for _ in range(3): # repeat 3 time, creating 3 different versions of each document
                        dataset = iterate_conllu(corpus, sloleks)
                        for line in dataset:
                            writer.write(json.dumps(line, ensure_ascii=False)+'\n')
                    
    #corpus = '/home/matej/GigaDisk/crkovalnik/maks/maks.conllu/maks1.conllu'
    #dataset = iterate_conllu(corpus, sloleks)
    #with open('generated_data_test.jsonl', 'w') as writer:
        #for line in dataset:
            #writer.write(json.dumps(line, ensure_ascii=False)+'\n')

if __name__ == "__main__":
    main()

"""CATEGORY (sl)	Value (sl)	Code (sl)	CATEGORY (en)	Value (en)	Code (en)	Attributes
besedna_vrsta	samostalnik	S	CATEGORY	Noun	N	5
besedna_vrsta	glagol	G	CATEGORY	Verb	V	7
besedna_vrsta	pridevnik	P	CATEGORY	Adjective	A	6
besedna_vrsta	prislov	R	CATEGORY	Adverb	R	2
besedna_vrsta	zaimek	Z	CATEGORY	Pronoun	P	8
besedna_vrsta	števnik	K	CATEGORY	Numeral	M	6
besedna_vrsta	predlog	D	CATEGORY	Adposition	S	1
besedna_vrsta	veznik	V	CATEGORY	Conjunction	C	1
besedna_vrsta	členek	L	CATEGORY	Particle	Q	0
besedna_vrsta	medmet	M	CATEGORY	Interjection	I	0
besedna_vrsta	okrajšava	O	CATEGORY	Abbreviation	Y	0
besedna_vrsta	neuvrščeno	N	CATEGORY	Residual	X	1
besedna_vrsta	ločilo	U	CATEGORY	Punctuation	Z	0"""
