
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




VERBOSE=True
words_from_abc_australia = abc.words()
# filtering out the stopwords is not needed as it gets rid of the words that make a sentence flow
words_from_abc_australia = list(map(lambda x: x.lower(),words_from_abc_australia))
corpus_length = len(words_from_abc_australia)
count = Counter(words_from_abc_australia)
vocabulary = count.keys()

bigrams = list(ngrams(words_from_abc_australia,2,pad_left=True,pad_right=True))
bigram_counter = Counter()
bigram_counter.update([gram for gram in bigrams])
laplace_vals_bigram = {}
#alpha
for i in range(len(bigrams)):
    laplace_vals_bigram[bigrams[i]] = (bigram_counter[bigrams[i]] + 1) / (count[bigrams[i][0]] + len(vocabulary))
if VERBOSE:
    for x in laplace_vals_bigram.keys():
        print("L2=",laplace_vals_bigram[x])

trigrams = list(ngrams(words_from_abc_australia,3,pad_left=True,pad_right=True))
trigram_counter = Counter()
trigram_counter.update([gram for gram in trigrams])
laplace_vals_trigram = {}
for i in range(len(trigrams)):
    laplace_vals_trigram[trigrams[i]] = (trigram_counter[trigrams[i]] + 1) / (bigram_counter[(trigrams[0],trigrams[1])] + len(vocabulary))

if VERBOSE:
    for x in laplace_vals_trigram.keys():
        print("L3=",laplace_vals_trigram[x])

### Context-Aware Spelling Corrector






# print(get_candidate_corrections_with_levenshtein("imterestieg",vocabulary))


# i need a state class cause im getting confused all the time
# could also do a result class but won't

class AutoCorrector:
    _texts = [] #= [("","")]
    # this makes it so that we can use anything where we can do .get((w1,w2))
    # to get the probability
    _bigram_model = dict()
    _trigram_model = dict()

    _sentences_to_evaluate_on = 5
    _mistake_probability = 0.1
    _beam_search_max_depth = 10
    _beam_search_beam_width = 4
    _beam_search_candidates_amount = 10
    _beam_search_use_bigram = True
    _beam_search_weights_for_prob = (0.65,0.35)
    _sentences = []
    _sentences_with_typos = []

    _vocabulary = []
    def run_with_default_settings(self,bigram_model,trigram_model,vocab):
        print("Will soon run")
        self._bigram_model = bigram_model
        self._trigram_model = trigram_model
        print(type(bigram_model))
        print(type(trigram_model))
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
        self._sentences = random_sentences
    def add_typos_to_sentences(self):
        self._sentences_with_typos = list(map(lambda sentence: self.add_typos_to_sentence(sentence),self._sentences))

    ### (VI) Evaluate your context-aware spelling corrector in terms of
    # Word Error Rate (WER) and
    # Character Error Rate (CER).
    def correct_sentences(self):
        assert (len(self._sentences) == len(self._sentences_with_typos))
        print("========Correcting sentences=========")
        print("\n")
        predictions = []
        references = []
        for index in range(len(self._sentences)):
            correct = self._sentences[index].lower()
            with_typos = self._sentences_with_typos[index].lower()
            corrected = self.correct_sentence(with_typos)
            print("Initial Sentence->",correct)
            print("With added typos",with_typos)
            print("Final correct sentence",corrected)
            predictions.append(corrected)
            references.append(correct)
        word_error_rate = AutoCorrector.WER(predictions,references)
        character_error_rate = AutoCorrector.CER(predictions,references)
        print("For mistake probability: ",self._mistake_probability)
        print("Our model's WER is: ", word_error_rate)
        print("Our model's CER is: ", character_error_rate)
    def correct_sentence(self, with_typos):
        # have not yet added <start>, <end>
        initial_state = word_tokenize(with_typos)
        initial_state = list(map(lambda word: word.lower(), initial_state))
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
            return [(word,1.0) for word in range(n)]

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
        # probs = list(map(lambda w: 1 if edit_distance(w) == 0 else (1 / edit_distance(w)), closest_words))
        return list(zip(closest_words, probs))
    def get_candidate_corrections_with_levenshtein(self, sentence_prob):
        assert (len(sentence_prob[0]) > 0)
        word_alternatives = []
        for word in sentence_prob[0]:
            #this is a hansaplast, i have a problem with the state representation
            if type(word)!= str:continue
            close_vocab_words = self.get_n_closest_words(word,7)
            word_alternatives.append(close_vocab_words)

        candidates = []
        for i in range(self._beam_search_candidates_amount):
            sentence = []
            for words_to_choose_from in word_alternatives:
                # it chooses by complete randomness that is the problem, now it is maxed
                word_and_prob = max(words_to_choose_from,key=lambda x: x[1])
                sentence.append(word_and_prob)
            probability_of_sentence = 1
            result = []
            for word_prob in sentence:
                probability_of_sentence *= 1/word_prob[1]
                result.append(word_prob[0])

            candidates.append((result,probability_of_sentence))
        # print("Candidates are",candidates)
        return candidates


    def score(self,state):
        # Calculate the probability of the word sequence using the bigram model
        # or trigram model and the levenshtein distance(of the last word of state)
        # print("State is:",state)
        sentence = state[0]
        lev_probability_of_sentence = state[1]
        lm_probability = 1.0
        for i in range(1, len(sentence)):
            prev_word, word = sentence[i - 1], sentence[i]
            if self._beam_search_use_bigram:
                lm_probability = lm_probability * self._bigram_model.get((prev_word, word), 0.0)
            else:
                lm_probability = lm_probability * self._trigram_model.get((prev_word, word), 0.0)
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
            print(new_candidates)
            new_candidates = sorted(new_candidates, key=lambda x: x[1], reverse=True)
            # print('***** Sorted')
            print(new_candidates)
            print(f'***** Chosen candidates (top-{beam_width})')
            candidates = new_candidates[:beam_width]
            print(candidates)
        assert (len(candidates) > 0)
        best_sequence, best_prob = max(candidates, key=lambda x: x[1])
        return " ".join(best_sequence)

corrector = AutoCorrector()
print(type(laplace_vals_bigram))
print(type(laplace_vals_trigram))
corrector.run_with_default_settings(laplace_vals_bigram,laplace_vals_trigram,vocabulary)





