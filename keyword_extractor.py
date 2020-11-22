import argparse
import datetime
import logging
import re
import sys
import time

import pytextrank
import spacy


class KeywordExtractor(object):

    def __init__(self, input_file):
        self._input_file = input_file
        with open(input_file, "r") as infile:
            text = infile.read()
            self._text = re.sub(' +', ' ', text.replace('\n', ' '))

    def top_keywords(self, n = 50):
        nlp = spacy.load("en_core_web_sm")
        nlp.max_length = 4000000
        pos = ['ADJ', 'NOUN', 'PROPN']
        tr = pytextrank.TextRank(pos_kept=pos)
        nlp.add_pipe(tr.PipelineComponent, name="textrank", last=True)
        doc = nlp(self._text)

        keywords = []
        count = 0
        for p in doc._.phrases:
            logging.debug("{:.4f} {:5d}  {}".format(p.rank, p.count, p.text))
            keywords.append(p.text)
            if count == n:
                break
            count += 1
        return keywords

    # def tfidf(self, n):
    #     method = pke.unsupervised.TfIdf()
    #     method.load_document(input=self._input_file, language='en', max_length=4000000)
    #     method.candidate_selection(n=3, stoplist=stoplist)
    #     df = pke.load_document_frequency_file('df.tsv.gz')
    #     method.candidate_weighting(df=df)
    #     keyphrases = method.get_n_best(n=n)
    #     for key in keyphrases:
    #         print(key)
    #     return [item[0] for item in keyphrases]

    # def mpr(self, n):
    #     extractorMultipartiteRank = pke.unsupervised.MultipartiteRank()
    #     extractorMultipartiteRank.load_document(input=self._input_file, max_length=4600000)
    #     pos = {'NOUN', 'PROPN', 'ADJ'}
    #     stoplist = list(string.punctuation)
    #     stoplist += ['-lrb-', '-rrb-', '-lcb-', '-rcb-', '-lsb-', '-rsb-']
    #     stoplist += stopwords.words('english')
    #     extractorMultipartiteRank.candidate_selection(pos=pos, stoplist=stoplist)
    #     extractorMultipartiteRank.candidate_weighting(alpha=1.1,
    #                                                   threshold=0.74, method='average')
    #     keyphrasesMultipartiteRank = extractorMultipartiteRank.get_n_best(n=n)
    #     for key in keyphrasesMultipartiteRank:
    #         print(key)
    #     return [item[0] for item in keyphrasesMultipartiteRank]

    # def tr(self, n):
    #     extractorTextRank = pke.unsupervised.TextRank()
    #     extractorTextRank.load_document(input=self._input_file, language='en', normalization=None, max_length=4600000, stoplist=stoplist)
    #     window = 4
    #     extractorTextRank.candidate_weighting(window=window, top_percent=0.33, normalized=True)
    #     keyphases = extractorTextRank.get_n_best(n=n)
    #     for key in keyphases:
    #         print(key)
    #     return [item[0] for item in keyphases]

    # def kpminer(self, n):
    #     extractor = pke.unsupervised.KPMiner()
    #     extractor.load_document(input='out_combined.txt', language='en', normalization=None, max_length=4600000)
    #     lasf = 5
    #     cutoff = 200
    #     extractor.candidate_selection(lasf=lasf, cutoff=cutoff)
    #     df = pke.load_document_frequency_file('df.tsv.gz')
    #     alpha = 2.3
    #     sigma = 3.0
    #     extractor.candidate_weighting(df=df, alpha=alpha, sigma=sigma)
    #     kephrases = extractor.get_n_best(n=n)
    #     for key in kephrases:
    #         print(key)
    #     return kephrases

    # def trf(self, n):
    #     pos = {'NOUN', 'PROPN', 'ADJ'}
    #     extractor = pke.unsupervised.TextRank()
    #     extractor.load_document(input=self._input_file, language='en', normalization=None, max_length=4600000)
    #     lasf = 2
    #     cutoff = 200
    #     extractor.candidate_selection(lasf=lasf, cutoff=cutoff)
    #     df = pke.load_document_frequency_file('df.tsv.gz')
    #     alpha = 2.3
    #     sigma = 3.0
    #     extractor.candidate_weighting(df=df, alpha=alpha, sigma=sigma)
    #     kephrases = extractor.get_n_best(n=n)
    #     for key in kephrases:
    #         print(key)
    #     return kephrases

    # def yake(self, n):
    #     # 1. create a YAKE extractor.
    #     extractor = pke.unsupervised.YAKE()

    #     # 2. load the content of the document.
    #     extractor.load_document(input=self._input_file,
    #                             language='en',
    #                             normalization=None, max_length=4600000)


    #     # 3. select {1-3}-grams not containing punctuation marks and not
    #     #    beginning/ending with a stopword as candidates.

    #     extractor.candidate_selection(n=3, stoplist=stoplist)

    #     # 4. weight the candidates using YAKE weighting scheme, a window (in
    #     #    words) for computing left/right contexts can be specified.
    #     window = 1
    #     use_stems = True # use stems instead of words for weighting
    #     extractor.candidate_weighting(window=window,
    #                                   stoplist=stoplist,
    #                                   use_stems=use_stems)

    #     # 5. get the n-highest scored candidates as keyphrases.
    #     #    redundant keyphrases are removed from the output using levenshtein
    #     #    distance and a threshold.
    #     threshold = 0.8
    #     keyphrases = extractor.get_n_best(n=n, threshold=threshold)
    #     for key in keyphrases:
    #         print(key)
    #     return [item[0] for item in keyphrases]

    # def topicrank(self, n):
    #     # 1. create a TopicRank extractor.
    #     extractor = pke.unsupervised.TopicRank()

    #     # 2. load the content of the document.
    #     extractor.load_document(input=self._input_file)

    #     # 3. select the longest sequences of nouns and adjectives, that do
    #     #    not contain punctuation marks or stopwords as candidates.
    #     pos = {'NOUN', 'PROPN', 'ADJ'}
    #     stoplist = list(string.punctuation)
    #     stoplist += ['-lrb-', '-rrb-', '-lcb-', '-rcb-', '-lsb-', '-rsb-']
    #     stoplist += stopwords.words('english')
    #     extractor.candidate_selection(pos=pos, stoplist=stoplist)

    #     # 4. build topics by grouping candidates with HAC (average linkage,
    #     #    threshold of 1/4 of shared stems). Weight the topics using random
    #     #    walk, and select the first occuring candidate from each topic.
    #     extractor.candidate_weighting(threshold=0.74, method='average')

    #     # 5. get the 10-highest scored candidates as keyphrases
    #     keyphrases = extractor.get_n_best(n=n)
    #     for key in keyphrases:
    #         print(key)
    #     return [item[0] for item in keyphrases]

    # def pr(self):
    #     # define the valid Part-of-Speeches to occur in the graph
    #     pos = {'NOUN', 'PROPN', 'ADJ'}

    #     # define the grammar for selecting the keyphrase candidates
    #     grammar = "NP: {<ADJ>*<NOUN|PROPN>+}"

    #     # 1. create a PositionRank extractor.
    #     extractor = pke.unsupervised.PositionRank()

    #     # 2. load the content of the document.
    #     extractor.load_document(input='out_combined.txt',
    #                             language='en',
    #                             normalization=None, max_length=4600000)

    #     # 3. select the noun phrases up to 3 words as keyphrase candidates.
    #     extractor.candidate_selection(grammar=grammar,
    #                                   maximum_word_number=3)

    #     # 4. weight the candidates using the sum of their word's scores that are
    #     #    computed using random walk biaised with the position of the words
    #     #    in the document. In the graph, nodes are words (nouns and
    #     #    adjectives only) that are connected if they occur in a window of
    #     #    10 words.
    #     extractor.candidate_weighting(window=10,
    #                                   pos=pos)

    #     # 5. get the 10-highest scored candidates as keyphrases
    #     keyphrases = extractor.get_n_best(n=50)
    #     for key in keyphrases:
    #         print(key)
    #     return [item[0] for item in keyphrases]

# import pke
# from nltk.corpus import stopwords
# from pke import compute_document_frequency
# import string

# compute df counts and store as n-stem -> weight values
# compute_document_frequency(input_dir='collection',
#                            output_file='df.tsv.gz',
#                            extension='txt',           # input file extension
#                            language='en',                # language of files
#                            normalization="stemming",    # use porter stemmer
#                            stoplist=stopwords.words('english'))
# stoplist = [k.strip() for k in open('Smartstoplist.txt').readlines()]
def main():
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(stream = sys.stdout, format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    parser = argparse.ArgumentParser(description='Extract keywords from an input text.')
    parser.add_argument('input_file', metavar='input_file', type=str,
                        help='Input file containing text. Each text document should be on its own line.')
    parser.add_argument('-n', metavar='n', dest='n', type=int, default=50,
                        help='Number of top keywords.')
    parser.add_argument('-o', '--output-file', metavar='output_file', dest='output_file', type=str,
                        help='Output file containing the top \'n\' keywords in the input text.')
    args = parser.parse_args()

    start = time.time()
    keyword_extractor = KeywordExtractor(args.input_file)
    top_keywords = keyword_extractor.top_keywords(args.n)
    # top_keywords = keyword_extractor.tr(args.n)
    end = time.time()

    duration = datetime.timedelta(seconds=end-start)
    print(f"It took {str(duration)} seconds to extract keywords from a total of {len(keyword_extractor._text)} words.")

    if not args.output_file:
        for i, keyword in enumerate(top_keywords):
            print(f"{i:>3} | {keyword}")
        return

    with open(args.output_file, "w") as output_file:
        for keyword in top_keywords:
            output_file.write(keyword + '\n')

if __name__ == '__main__':
    main()
