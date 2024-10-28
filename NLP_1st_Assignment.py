
import nltk
from collections import Counter

# from lxml.parser import result
from nltk.corpus import brown, stopwords,europarl_raw,abc
from nltk import tokenize, sent_tokenize, unique_list, word_tokenize
# nltk.download("brown")
# nltk.download("europarl_raw")
# nltk.download("stopwords")
# nltk.download('punkt_tab')
# nltk.download("abc")
from nltk.util import ngrams
from Levenshtein import distance
import string
import numpy as np
import random
#pip install jiwer
from evaluate import load
from math import log2

import nltk
import math

#Every corpus can be accessed by a "reader object" from "nltk.corpus".
from nltk.corpus import brown, stopwords
from collections import Counter
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.util import ngrams


def download_nltk_data_resources(var_resources_id):
    nltk.download(var_resources_id)

# download_nltk_data_resources("brown")
# print(brown.categories())
# obj_corpus_reader_category_text = brown.words(categories="news")
obj_corpus_reader_category_text = abc.words()
list_corpus_text = list(map(lambda var_token: var_token.lower(), obj_corpus_reader_category_text))
# We need the stopwords as we are dealing with sentences and not just words themselves
# list_corpus_text = [var_token for var_token in list_corpus_text if not var_token in stopwords.words("english")]

print("Reader: Length of Corpus is:", len(obj_corpus_reader_category_text), "First tokens are:", obj_corpus_reader_category_text[:20])
print("List:   Length of Corpus is:", len(list_corpus_text), "First tokens are:", list_corpus_text[:20])

obj_collections_counter = Counter(list_corpus_text)
print("Length of Counter is:", len(obj_collections_counter))
obj_collections_counter = Counter({var_key: var_value for var_key, var_value in obj_collections_counter.items() if var_value > 9})
print("Length of Counter is:", len(obj_collections_counter))
print("Most common are:", obj_collections_counter.most_common(10))
print("Least common are:", obj_collections_counter.most_common()[-10:])

dict_keys_vocabulary = obj_collections_counter.keys()
print("Length of Vocabulary:", len(dict_keys_vocabulary), "Type:", type(dict_keys_vocabulary))

list_corpus_text = [var_token if var_token in dict_keys_vocabulary else "<UNK>" for var_token in list_corpus_text]
print("Length of Corpus with unknown words replaced:", len(list_corpus_text))

# From 3.8.2 nltk version, "punkt" is replaced by "punkt_tab".
# download_nltk_data_resources("punkt")
# download_nltk_data_resources("punkt_tab")
counter_unigram = Counter()
counter_bigram = Counter()
counter_trigram = Counter()

var_corpus_text = " ".join(list_corpus_text)
list_sentences = sent_tokenize(var_corpus_text)
print(type(list_sentences))

for var_sent in list_sentences:
    counter_unigram.update([var_unigram for var_unigram in ngrams(var_sent.split(), 1, pad_left = True, pad_right=True, left_pad_symbol = "<start>", right_pad_symbol="<end>")])
    counter_bigram.update([var_bigram for var_bigram in ngrams(var_sent.split(), 2, pad_left = True, pad_right=True, left_pad_symbol = "<start>", right_pad_symbol="<end>")])
    counter_trigram.update([var_trigram for var_trigram in ngrams(var_sent.split(), 3, pad_left = True, pad_right=True, left_pad_symbol = "<start>", right_pad_symbol="<end>")])

print(counter_unigram.most_common(10))
print(counter_bigram.most_common(10))
print(counter_trigram.most_common(10))
print(counter_bigram.most_common()[-10:])
print(type(counter_unigram))

dict_counter_unigrams = {var_key[0]: var_value for var_key, var_value in counter_unigram.items()}
dict_counter_unigrams.update({"<start>": len(list_sentences)})
dict_counter_bigrams = {(var_key[0], var_key[1]): var_value for var_key, var_value in counter_bigram.items()}
dict_counter_bigrams.update({("<start>","<start>"): len(list_sentences)})
dict_counter_trigrams = {(var_key[0], var_key[1], var_key[2]): var_value for var_key, var_value in counter_trigram.items()}
# print(dict_counter_unigrams)
# print(dict_counter_bigrams)
# print(dict_counter_trigrams)

print("keys are:", dict_counter_unigrams.keys())
print("count is:", dict_counter_unigrams['<start>'])


var_vocabulary_size = len(dict_keys_vocabulary)
print("vocabulary size is:", var_vocabulary_size)
dict_bigram_probabilities = { }
for var_bigram_key, var_bigram_value in dict_counter_bigrams.items():
    #print("var_bigram_key is:", var_bigram_key, "with value:", var_bigram_value)
    #print("count of:", var_bigram_key[0], "is: ", dict_counter_unigrams.get(var_bigram_key[0]), "is there in vocabulary:", var_bigram_key[0] in dict_keys_vocabulary)
    dict_bigram_probabilities.update({(var_bigram_key[1], var_bigram_key[0]): (var_bigram_value + 1) / (dict_counter_unigrams[var_bigram_key[0]] + var_vocabulary_size)})

dict_trigram_probabilities = { }
for var_trigram_key, var_trigram_value in dict_counter_trigrams.items():
    dict_trigram_probabilities.update({(var_trigram_key[2], var_trigram_key[0], var_trigram_key[1]): (var_trigram_value + 1) / (dict_counter_bigrams[(var_trigram_key[0],var_trigram_key[1])] + var_vocabulary_size)})

# print(dict_bigram_probabilities)
# print(dict_trigram_probabilities)

############################################################################################### 2nd exercise


list_subset_sentences = sent_tokenize(var_corpus_text)[:10]
var_bigram_sum_log_likelihood = 0
var_trigram_sum_log_likelihood = 0
var_total_tokens = 0
for var_sent in list_subset_sentences:
    var_sent_bigram = "<start> " + var_sent + " <end>"
    var_sent_trigram = "<start1> <start2> " + var_sent + " <end>"
    list_sentence_tokens = var_sent_bigram.split()
    var_total_tokens += len(list_sentence_tokens)
    for var_bigram_token in range(1, len(list_sentence_tokens)-1):
        # print("token is:", list_sentence_tokens[var_bigram_token])
        # print((list_sentence_tokens[var_bigram_token+1], list_sentence_tokens[var_bigram_token]))
        var_bigram_sum_log_likelihood += math.log2(dict_bigram_probabilities[(list_sentence_tokens[var_bigram_token+1], list_sentence_tokens[var_bigram_token])])
    for var_trigram_token in range(2, len(list_sentence_tokens)-2):
        var_trigram_sum_log_likelihood += math.log2(dict_trigram_probabilities[(list_sentence_tokens[var_trigram_token+2], list_sentence_tokens[var_trigram_token], list_sentence_tokens[var_trigram_token+1])])

var_bigram_cross_entropy = - var_bigram_sum_log_likelihood / var_total_tokens
var_bigram_perplexity = math.pow(2, var_bigram_cross_entropy)
var_trigram_cross_entropy = - var_trigram_sum_log_likelihood / var_total_tokens
var_trigram_perplexity = math.pow(2, var_trigram_cross_entropy)
print("Bigram: Cross Entropy is:", var_bigram_cross_entropy, "Perplexity is:", var_bigram_perplexity)
print("Trigram: Cross Entropy is:", var_trigram_cross_entropy, "Perplexity is:", var_trigram_perplexity)


############################################################################################### 3rd Exercise

# print("1:", dict_bigram_probabilities[("county", "fulton")], "Key existing: ", ("county", "fulton") in dict_bigram_probabilities)
# print("2:", dict_bigram_probabilities[("fulton", "election")])

list_subset_complete_sentences = list_subset_sentences[:2]
print("Sentence 1:", list_subset_complete_sentences[0], "Length is:", len(list_subset_complete_sentences[0].split()))
print("Sentence 2:", list_subset_complete_sentences[1], "Length is:", len(list_subset_complete_sentences[1].split()))

for var_sent in list_subset_complete_sentences:
    list_incomplete_bigram_sentence = ["<start>"]
    list_incomplete_trigram_sentence = ["<start1>", "<start2>"]
    list_incomplete_bigram_sentence.extend(var_sent.split())
    list_incomplete_trigram_sentence.extend(var_sent.split())
    var_total_tokens = len(list_incomplete_bigram_sentence)
    var_max_unremoved_index = var_total_tokens // 2 + 1
    # print("Max unremoved index is: ", var_max_unremoved_index)
    for var_index in range(var_max_unremoved_index + 1, var_total_tokens):
        list_incomplete_bigram_sentence.pop()
        list_incomplete_trigram_sentence.pop()
    print("Bigram Sentence Incomplete:", list_incomplete_bigram_sentence)
    print("Trigram Sentence Incomplete:", list_incomplete_trigram_sentence)


    for var_index in range(var_max_unremoved_index + 1, var_total_tokens):
        var_bigram_probability = 0.0
        var_trigram_probability = 0.0
        tuple_bigram_choice_01 = (" ", 0.0)
        tuple_bigram_choice_02 = (" ", 0.0)
        tuple_trigram_choice_01 = (" ", 0.0)
        tuple_trigram_choice_02 = (" ", 0.0)
        #print("index:", var_index, "token:", list_incomplete_bigram_sentence[var_index - 1])
        for var_word in dict_keys_vocabulary:
            bigram_tuple = (var_word, list_incomplete_bigram_sentence[var_index - 1])
            if bigram_tuple in dict_bigram_probabilities:
                var_bigram_probability = dict_bigram_probabilities[bigram_tuple]
            else:
                #Laplace Smoothing
                var_bigram_probability = 1 / (dict_counter_unigrams[bigram_tuple[1]] + var_vocabulary_size)

            trigram_tuple = (var_word, list_incomplete_trigram_sentence[var_index - 2], list_incomplete_trigram_sentence[var_index - 1])
            if  trigram_tuple in dict_trigram_probabilities:
                var_trigram_probability = dict_trigram_probabilities[trigram_tuple]
            else:
                if (trigram_tuple[1], trigram_tuple[2]) in dict_counter_bigrams:
                    var_trigram_probability = 1 / (dict_counter_bigrams[(trigram_tuple[1], trigram_tuple[2])] + var_vocabulary_size)
                else:
                    var_trigram_probability = 1 / var_vocabulary_size

            if  tuple_bigram_choice_01[1] < var_bigram_probability:
                # print("index", var_index, "new candidate bigram word:", var_word, "tuple: ", bigram_tuple)
                tuple_bigram_choice_02 =  tuple_bigram_choice_01
                tuple_bigram_choice_01 = (var_word, var_bigram_probability)
            elif tuple_bigram_choice_02[1] < var_bigram_probability:
                tuple_bigram_choice_02 = (var_word, var_bigram_probability)
            if tuple_trigram_choice_01[1] < var_trigram_probability:
                # print("index", var_index, "new candidate trigram word:", var_word, "tuple: ", bigram_tuple)
                tuple_trigram_choice_02 = tuple_trigram_choice_01
                tuple_trigram_choice_01 = (var_word, var_trigram_probability)
            elif tuple_trigram_choice_02[1] < var_trigram_probability:
                tuple_trigram_choice_02 = (var_word, var_bigram_probability)
        # print("choice_bigram_01 is:", tuple_bigram_choice_01[0], "choice_bigram_02 is:", tuple_bigram_choice_02[0])
        list_incomplete_bigram_sentence.append(tuple_bigram_choice_01[0])
        list_incomplete_trigram_sentence.append(tuple_trigram_choice_01[0])
    print("Bigram Complete:", list_incomplete_bigram_sentence)
    print("Trigram Complete:", list_incomplete_trigram_sentence)


# VERBOSE=True
# words_from_abc_australia = abc.words()
# # filtering out the stopwords is not needed as it gets rid of the words that make a sentence flow
# words_from_abc_australia = list(map(lambda x: x.lower(),words_from_abc_australia))
# corpus_length = len(words_from_abc_australia)
# count = Counter(words_from_abc_australia)
# vocabulary = count.keys()
#
# bigrams = list(ngrams(words_from_abc_australia,2,pad_left=True,pad_right=True))
# bigram_counter = Counter()
# bigram_counter.update([gram for gram in bigrams])
# laplace_vals_bigram = {}
# #alpha
# for i in range(len(bigrams)):
#     laplace_vals_bigram[bigrams[i]] = (bigram_counter[bigrams[i]] + 1) / (count[bigrams[i][0]] + len(vocabulary))
# if VERBOSE:
#     for x in laplace_vals_bigram.keys():
#         print("L2=",laplace_vals_bigram[x])
#
# trigrams = list(ngrams(words_from_abc_australia,3,pad_left=True,pad_right=True))
# trigram_counter = Counter()
# trigram_counter.update([gram for gram in trigrams])
# laplace_vals_trigram = {}
# for i in range(len(trigrams)):
#     laplace_vals_trigram[trigrams[i]] = (trigram_counter[trigrams[i]] + 1) / (bigram_counter[(trigrams[0],trigrams[1])] + len(vocabulary))
#
# for x in laplace_vals_trigram.keys():
#     print("L3=",laplace_vals_trigram[x])

### Context-Aware Spelling Corrector

class SentenceCorrectionResult:
    initial_sentence = ""
    typos_sentence = ""
    mistake_probability = 0.0
    corrected_sentence = ""
    wer = -1
    cer = -1
    lev_weight = -1
    lm_weight = -1
    def append_to_file(self,filepath):
        with open(filepath, mode='a', encoding='utf-8') as file:
            file.write(f"{self.initial_sentence},{self.typos_sentence},{self.corrected_sentence},{self.mistake_probability},{self.wer},{self.cer},{self.lev_weight},{self.lm_weight}\n")

class AutoCorrector:
    _texts = [] #= [("","")]
    # this makes it so that we can use anything where we can do .get((w1,w2))
    # to get the probability
    _bigram_model = dict()
    _trigram_model = dict()
    _file_output = "Per-Sentence-Results-Final.csv"

    _sentences_to_evaluate_on = 5
    _mistake_probability = 0.25


    _beam_search_max_depth = 7
    _beam_search_beam_width = 4
    _beam_search_candidates_amount = 10
    _beam_search_use_bigram = False
    _beam_search_weights_for_prob = (0.25,0.75)


    _sentences = []
    _sentences_with_typos = []

    _vocabulary = []
    def run_with_default_settings(self,bigram_model,trigram_model,vocab):
        self._bigram_model = bigram_model
        self._trigram_model = trigram_model
        self._vocabulary = vocab
        assert (len(self._vocabulary) > 0)
        assert (self._beam_search_candidates_amount > 0)

        self.get_default_texts()
        self.get_random_sentences_from_texts()
        self.add_typos_to_sentences()
        self.correct_sentences()

    # (v) Create an artificial test dataset to evaluate your context-aware spelling corrector
    def get_default_texts(self):
        self._texts.append((europarl_raw.english.raw(),"Sample European Parliament Proceedings Parallel Corpus"))
    def get_random_sentences_from_texts(self):
        assert (len(self._texts) > 0)
        text,title = random.choice(self._texts)
        sentences = sent_tokenize(text)
        random_sentences = [random.choice(sentences) for _ in range(self._sentences_to_evaluate_on)]
        self._sentences = [s.replace("\n"," ").replace(","," ").lower() for s in random_sentences]
    def add_typos_to_sentences(self):
        self._sentences_with_typos = list(map(lambda sentence: self.add_typos_to_sentence(sentence),self._sentences))

    ### (VI) Evaluate your context-aware spelling corrector in terms of
    # Word Error Rate (WER) and
    # Character Error Rate (CER).
    def correct_sentences(self):
        assert (len(self._sentences) == len(self._sentences_with_typos))
        print("========Correcting sentences=========")
        print("\n")
        with open(self._file_output, mode="a", encoding='utf-8') as file:
            file.write(
                "Initial Sentence,Sentence with Typos,Corrected Sentence,Mistake Probability,WER,CER,Levenshtein Weight,Language Model Weight\n")
        weight_options = [
            #LM,LEV
            (0.0, 1.0),
            (0.1, 0.9),
            (0.2, 0.8),
            (0.3, 0.7),
            (0.4, 0.6),
            (0.5, 0.5),
            (0.6, 0.4),
            (0.7, 0.3),
            (0.8, 0.2),
            (0.9, 0.1),
            (1.0, 0.0),
        ]
        for weights in weight_options:
            self._beam_search_weights_for_prob = weights
            avg_word_error_rate = 0
            avg_character_error_rate = 0
            for index in range(len(self._sentences)):
                correct = self._sentences[index]
                with_typos = self._sentences_with_typos[index]
                corrected = self.correct_sentence(with_typos)

                wer = AutoCorrector.WER([corrected], [correct])
                cer = AutoCorrector.CER([corrected], [correct])

                print("Initial Sentence->", correct)
                print("With added typos->", with_typos)
                print("Final correct sentence->", corrected)
                print("WER->", wer)
                print("CER->", cer)

                res = SentenceCorrectionResult()
                res.initial_sentence = correct
                res.typos_sentence = with_typos
                res.mistake_probability = self._mistake_probability
                res.corrected_sentence = corrected
                res.wer = wer
                res.cer = cer
                res.lm_weight = self._beam_search_weights_for_prob[0]
                res.lev_weight = self._beam_search_weights_for_prob[1]
                res.append_to_file(self._file_output)

                avg_word_error_rate = avg_word_error_rate + wer
                avg_character_error_rate = avg_character_error_rate + cer
            avg_word_error_rate = avg_word_error_rate / len(self._sentences)
            avg_character_error_rate = avg_character_error_rate / len(self._sentences)
            print(f"For weights(lm,lev): {self._beam_search_weights_for_prob}")
            print("For mistake probability: ", self._mistake_probability)
            print("Our model's AVG WER is: ", avg_word_error_rate)
            print("Our model's AVG CER is: ", avg_character_error_rate)
    def correct_sentence(self, with_typos):
        # have not yet added <start>, <end>
        initial_state = word_tokenize(with_typos)
        initial_state = list(map(lambda word: word.lower(), initial_state))
        # initial_state.insert(0,"<start>")
        # initial_state.append("<end>")
        best_correction = self.beam_search_decode(
            initial_state,
            self._beam_search_max_depth,
            self._beam_search_beam_width,
            self.get_candidate_corrections_with_levenshtein,
            self.score)

        return best_correction

    def add_typos_to_sentence(self,complete_text):
        final_text = ""
        def is_non_space_char(ch):
            return ch == ' ' or ch == '\t' or ch == '\r' or ch == '\n'
        for i in range(len(complete_text)):
            character = complete_text[i]
            if is_non_space_char(character):
                # so we can maintain the same sentence format
                final_text += character
                continue
            p = np.random.uniform(0, 1)
            if p <= self._mistake_probability:
                final_text = final_text + AutoCorrector.generate_random_character(character)  # random character
            else:
                final_text = final_text + character
        return final_text

    @staticmethod
    def generate_random_character(ch):
        # when a user does a typo he most likely was using the correct case
        # but this is too linguistic for this case
        if ch.islower():
            return random.choice(string.ascii_lowercase)
        else:
            return random.choice(string.ascii_uppercase)


    def get_n_closest_words(self,word,n):
        # print("Word: ",word)
        # assert(type(word) == str)
        if word == "?" or word == "," or word == ".":
            return [(word,1.0) for _ in range(n)]

        def edit_distance(word1):
            return distance(word1, word)
        closest_words = sorted(self._vocabulary, key=edit_distance)[:n]
        # something is going wrong here
        probs = []
        for close_word in closest_words:
            dist = edit_distance(close_word)
            if dist == 0:
                probs.append(1)
            else:
                probs.append(1.0/(dist + 1))
        return list(zip(closest_words, probs))
    def get_candidate_corrections_with_levenshtein(self, sentence_prob):
        assert (len(sentence_prob[0]) > 0)
        word_alternatives = []
        for word in sentence_prob[0]:
            if type(word) != str :continue
            close_vocab_words = self.get_n_closest_words(word,7)
            word_alternatives.append(close_vocab_words)
        candidates = []
        for i in range(self._beam_search_candidates_amount):
            sentence = []
            for words_to_choose_from in word_alternatives:
                word_and_prob = max(words_to_choose_from,key=lambda x: x[1])
                sentence.append(word_and_prob)
            probability_of_sentence = 1
            result = []
            for word_prob in sentence:
                probability_of_sentence *= word_prob[1]
                result.append(word_prob[0])
            candidates.append((result,probability_of_sentence))
        return candidates


    def score(self,state):
        # Calculate the probability of the word sequence using the bigram model
        # or trigram model and the levenshtein distance(of the last word of state)
        # State-> Tuple(Sentence->Words[],Lev_Prob_Of_sentence))
        sentence = state[0]
        lev_probability_of_sentence = state[1]
        lm_probability = 1.0
        if self._beam_search_use_bigram:
            for i in range(1, len(sentence)):
                prev_word, word = sentence[i - 1], sentence[i]
                lm_probability = lm_probability * self._bigram_model.get((word,prev_word), 0.0)
        else:
            for i in range(2, len(sentence)):
                prev_prev_word,prev_word,word = sentence[i-2],sentence[i - 1], sentence[i]
                lm_probability = lm_probability * self._trigram_model.get((word,prev_prev_word, prev_word), 0.0)
        #-l1*log(P(w1|t1))-l2*log(P(t1_k))-> Slide 18 Part_01
        result = self._beam_search_weights_for_prob[1] * log2(lev_probability_of_sentence)
        if lm_probability != 0:
           result += self._beam_search_weights_for_prob[0] * lm_probability
        return -result

    def is_out_of_vocabulary(self,word):
        return not (word in self._vocabulary)
    @staticmethod
    def WER(predictions, references):
        wer = load("wer")
        return wer.compute(predictions=predictions, references=references)
    @staticmethod
    def CER(predictions, references):
        cer = load("cer")
        return cer.compute(predictions=predictions, references=references)

    def beam_search_decode(self,initial_state, max_depth, beam_width, generate_candidates_fn, score_fn):
        candidates = [(initial_state, 1.0)]
        print("========BEAM SEARCH=======")
        print("For sentence: ",initial_state)
        for depth in range(max_depth):
            new_candidates = []
            for candidate, prob in candidates:
                for next_state in generate_candidates_fn((candidate,prob)):
                    new_prob = prob * score_fn(next_state)
                    new_candidates.append((next_state[0],new_prob*next_state[1]))

            # print('\n***** NEW candidates *****')
            #print(new_candidates)
            new_candidates = sorted(new_candidates, key=lambda x: x[1], reverse=True)
            # print('***** Sorted')
            #print(new_candidates)
            #print(f'***** Chosen candidates (top-{beam_width})')
            candidates = new_candidates[:beam_width]
            #print(candidates)
        assert (len(candidates) > 0)
        best_sequence, best_prob = max(candidates, key=lambda x: x[1])
        return " ".join(best_sequence)


corrector = AutoCorrector()
corrector.run_with_default_settings(dict_bigram_probabilities,dict_trigram_probabilities,dict_keys_vocabulary)
# print(stopwords.words("english"))
# corrector._vocabulary = dict_keys_vocabulary
# print(corrector.get_n_closest_words(".",10))
print("".join(["A","B"]))




