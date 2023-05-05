# !python -m spacy download en_core_web_lg

from tqdm.auto import tqdm

import pandas as pd
import numpy as np
import re
import spacy

from sentence_transformers import SentenceTransformer, util
from happytransformer import  HappyTextToText
from happytransformer import TTSettings
from deepmultilingualpunctuation import PunctuationModel
import language_tool_python
import difflib
import wordfreq
import nltk
from nltk.translate import gleu_score
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer

import warnings
warnings.filterwarnings("ignore")

def Grade_Map(final_score):
    grade_map = {'A+': [97, 100],
                     'A': [93, 96],
                     'A−': [90, 92],
                     'B+': [87, 89],
                     'B': [83, 86],
                     'B−': [80, 82],
                     'C+': [77, 79],
                     'C': [73, 76],
                     'C−': [70, 72],
                     'D+': [67, 69],
                     'D': [63, 66],
                     'D−': [60, 62],
                     'F': [0, 59]}
    for key in grade_map.keys():
        if grade_map[key][0] <= round(final_score) <= grade_map[key][1]:
            break
    
    return key

def startup():
    if 'model_sim' not in globals():
        print('Loading SentenceTransformer...')
        global model_sim
        model_sim = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')
    
    if 'gramm_model' not in globals():
        print('Loading GrammarTransformer...')
        global gramm_model
        gramm_model = HappyTextToText("T5", "vennify/t5-base-grammar-correction")
    
    if 'punct_model' not in globals():
        global punct_model
        punct_model = PunctuationModel()
    
    nltk.download('vader_lexicon')
    nltk.download('punkt')
    nltk.download('omw-1.4')
    
    if not set(['stops', 'gramm_tool', 'nlp', 'sid', 'grade_map']).issubset(globals()):
        print('Setting up dependencies...')
        global stops
        stops = set(stopwords.words('english'))
    
        global gramm_tool
        gramm_tool = language_tool_python.LanguageTool('en-US')
        
        global nlp
        nlp = spacy.load('en_core_web_sm')
        
        global sid
        sid = SentimentIntensityAnalyzer()
        
        global grade_map
        grade_map = {'A+': [97, 100],
                     'A': [93, 96],
                     'A−': [90, 92],
                     'B+': [87, 89],
                     'B': [83, 86],
                     'B−': [80, 82],
                     'C+': [77, 79],
                     'C': [73, 76],
                     'C−': [70, 72],
                     'D+': [67, 69],
                     'D': [63, 66],
                     'D−': [60, 62],
                     'F': [0, 59]}
        

def grader(output, flag = False):
    if flag:
        return grader_comm(output)
    else:
        return grader_pers(output)
    
def grader_comm(output):
    tone_score = 3
    format_score = 4
    content_score = 6
    grammar_score = 7
    
    total_score = grammar_score + content_score + format_score + tone_score
    
    grammar_score -= 0.5*output['n_rules_violated']
    grammar_score = round(grammar_score*output['correction_score'], 2)
    grammar_score = round(grammar_score*4)/4
    
    if grammar_score < 0:
        grammar_score = 0

    # average length penality
    lb = 10
    ub = 30
    if output['avg_sentence_length'] < lb:
        content_score -= (lb - round(output['avg_sentence_length']))*0.5
    elif output['avg_sentence_length'] > ub:
        content_score -= (round(output['avg_sentence_length']) - ub)*0.5

    # deviation penalty
    if output['dev_sentence_length'] < 4:
        content_score -= (5 - round(output['dev_sentence_length']))*0.5
    
    content_score *= output['prompt_similarity']
    content_score = round(content_score*4)/4
    
    if content_score < 0:
        content_score = 0
    
    # format penalty
    format_score -= output['format_issues']
    
    # tone penalty
    tone_score *= output['sentiment_score']
    tone_score = round(tone_score*4)/4
    
    final_score = round(200*(grammar_score + content_score + format_score + tone_score)/total_score)/2
    
    # grade calculation
    for key in grade_map.keys():
        if grade_map[key][0] <= round(final_score) <= grade_map[key][1]:
            break
    
    return_json = {'grammar_score': grammar_score,
                   'content_score': content_score,
                   'format_score': format_score,
                   'tone_score': tone_score,
                   'final_score': final_score,
                   'grade': key}
    
    return return_json

def grader_pers(output):
    fluency_score = 10
    grammar_score = 6
    content_score = 4
    total_score = fluency_score + grammar_score + content_score
    
    grammar_score -= 0.5*output['n_rules_violated']
    grammar_score = round(grammar_score*output['correction_score'], 2)
    grammar_score = round(grammar_score*4)/4
    
    if grammar_score < 0:
        grammar_score = 0

    # average length penality
    lb = 10
    ub = 30
    if output['avg_sentence_length'] < lb:
        fluency_score -= (lb - round(output['avg_sentence_length']))*0.5
    elif output['avg_sentence_length'] > ub:
        fluency_score -= (round(output['avg_sentence_length']) - ub)*0.5

    # deviation penalty
    if output['dev_sentence_length'] < 4:
        fluency_score -= (5 - round(output['dev_sentence_length']))*0.5
    
    fluency_score = round(fluency_score*4)/4
    
    if fluency_score < 0:
        fluency_score = 0
    
    content_score *= output['prompt_similarity']
    content_score = round(content_score*4)/4
    
    if content_score < 0:
        content_score = 0
    
    final_score = round(200*(fluency_score + grammar_score + content_score)/total_score)/2
    
    # grade calculation
    for key in grade_map.keys():
        if grade_map[key][0] <= round(final_score) <= grade_map[key][1]:
            break
    
    return_json = {'fluency_score': fluency_score,
                   'grammar_score': grammar_score,
                   'content_score': content_score,
                   'final_score': final_score,
                   'grade': key}
    
    return return_json

def sentence_metrics(text):
    print('Calculating sentence metrics...')
    sent_lens = np.array([len(i.strip().split()) for i in re.split('\.|\?|\!', text) if len(i.strip()) > 0])
    text_average = round(np.mean(sent_lens), 4)
    text_dev = round(np.std(sent_lens), 4)
    
    return sent_lens, text_average, text_dev

def prompt_similarity(text, prompt):
    print('Calculating prompt similarity...')
    query = model_sim.encode(prompt)
    passage = model_sim.encode(text)
    sim_score = round(util.dot_score(query, passage).tolist()[0][0], 4)
    
    return sim_score

def grammar_corrector(text):
#     beam_settings =  TTSettings(num_beams = 8, min_length = 1, max_length = len(text) + 250)
    print('Checking language rules...')
    matches = gramm_tool.check(text)
    print('Generating corrected version...')
    corr_text_pre = gramm_tool.correct(text)
    
    print('Calculating correction score...')
    corr_text = []
    for sen in corr_text_pre.strip().split('. '):
        if len(sen) >= 1:
#             beam_settings =  TTSettings(num_beams = 5, min_length = 5, max_length = len(sen) + 10)
            beam_settings =  TTSettings(num_beams = 8, min_length = 5, max_length = len(sen.split()) + 8)
            corrected = gramm_model.generate_text(sen, args = beam_settings)
            corr_text.append(corrected.text)
    corr_text = ' '.join(corr_text)
    corr_text = punct_model.restore_punctuation(corr_text)

    corr_score = round(gleu_score.sentence_gleu([corr_text.split()], corr_text_pre.split()), 4)
        
    return corr_text, corr_score, matches

# def uncommon_identifier(text):
#     freqs = []

#     for word in [i for i in set(text.split()) if i not in stops]:
#         freqs.append(wordfreq.zipf_frequency(word, 'en', wordlist = 'large'))

#     return sum([i < 3 for i in freqs])

def format_check(response):
    n_issues = 0
    salutations = ['hi', 'hello', 'dear', 'greetings',
                   'good morning', 'good afternoon', 'good evening']
    signoffs = ['best', 'all the best', 'best wishes',
               'best regards', 'regards', 'warm regards',
               'kind regards', 'sincerely', 'cheers']

    text = [i.strip() for i in response.split('\n') if i.strip() != '']
    
    lb = 4
    ub = 10
    if not lb <= len(text) <= ub:
#         print('len')
        n_issues += 1
        if len(text) == 1:
            text = [i.strip() for i in response.split('.') if i.strip() != '']
            
    if np.max([text[0].lower().find(salute) for salute in salutations]) == -1:
#         print('sal miss')
        n_issues += 1

    if np.max([text[-2].lower().find(signoff) for signoff in signoffs]) == -1:
#         print('sign miss')
        n_issues += 1
        if np.max([text[-1].lower().find(signoff) for signoff in signoffs]) == -1:
            n_issues += 1

    return n_issues

def evaluator(text, prompt, format_flag = False):
    format_issues = 0
    if format_flag:
        format_issues += format_check(text)
    
    text = '. '. join([i.strip() for i in text.split('.')])
    
    sent_lens, text_average, text_dev = sentence_metrics(text)
    sim_score = prompt_similarity(text, prompt)
    corr_text, corr_score, matches = grammar_corrector(text)
    sent_score = sid.polarity_scores(text)['compound']
    
    output = {
#         'response': text,
        'response_length': len(text),
        'avg_sentence_length': text_average,
        'dev_sentence_length': text_dev,
        'format_issues': format_issues,
        'prompt_similarity': round(np.interp(sim_score, (0, 0.4), (0, 1)), 4),
        'correction_score': corr_score,
        'sentiment_score': round(np.interp(sent_score, (-0.75, 0.75), (0, 1)), 4),
        'n_rules_violated': len(set([match.ruleId for match in matches])),
        'rules_violated': matches,
#         'corrected': corr_text,
    }
    
    result = grader(output, format_flag)

    return_dict = {'score': result['final_score'], 
               'grade': result['grade'], 
               'logs': output, 
               'score_breakdown': result}
    return return_dict