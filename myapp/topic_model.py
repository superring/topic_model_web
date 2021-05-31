import glob
import urllib
import MeCab
import subprocess
import gensim
import math
import pandas as pd
import matplotlib
import matplotlib.pylab as plt
from wordcloud import WordCloud
import pyLDAvis
import pyLDAvis.gensim_models as gensimvis
import warnings

import string
import random
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class Topic:
    def __init__(self) -> None:
        self.font = "myapp/ArialUnicodeMS.ttf"
        pass
    

    # 形態素解析用の関数定義。固有名詞、名詞、動詞、形容詞を中心に
    def analyzer(self, text, mecab, stopwords=[], target_part_of_speech=['proper_noun', 'noun', 'verb', 'adjective']):

        node = mecab.parseToNode(text)
        words = []
        
        while node:

            features = node.feature.split(',')
            surface = features[6]

            if (surface == '*') or (len(surface) < 2) or (surface in stopwords):
                node = node.next
                continue

            noun_flag = (features[0] == '名詞')
            proper_noun_flag = (features[0] == '名詞') & (features[1] == '固有名詞')
            verb_flag = (features[0] == '動詞') & (features[1] == '自立')
            adjective_flag = (features[0] == '形容詞') & (features[1] == '自立')


            if ('proper_noun' in target_part_of_speech) & proper_noun_flag:
                words.append(surface)
            elif ('noun' in target_part_of_speech) & noun_flag:
                words.append(surface)
            elif ('verb' in target_part_of_speech) & verb_flag:
                words.append(surface)
            elif ('adjective' in target_part_of_speech) & adjective_flag:
                words.append(surface)

            node = node.next

        return words

    def modeling(self, text_path, separator, num_topics=6, no_below=0, no_above=0.5):
        # 形態素解析用のストップワードの定義
        req = urllib.request.Request('http://svn.sourceforge.jp/svnroot/slothlib/CSharp/Version1/SlothLib/NLP/Filter/StopWord/word/Japanese.txt')
        with urllib.request.urlopen(req) as res:
            self.stopwords = res.read().decode('utf-8').split('\r\n')
        while '' in self.stopwords:
            self.stopwords.remove('')
        
        # LDAのための辞書とコーパス作成
        cmd = 'echo `mecab-config --dicdir`"/mecab-ipadic-neologd"'
        path = (subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                shell=True).communicate()[0]).decode('utf-8')
        self.mecab = MeCab.Tagger("-d {0}".format(path))

        text = open(text_path, 'r', encoding='utf-8').read()

        texts_words = {}

        # 記事単位：改行で区切る
        if separator == "1":
            # 文章単位：句読点で区切る
            text = text.replace('\n', '。')
            text = text.split('。')
        else:
            text = text.split('\n')
        
        for i, t in enumerate(text):
            texts_words[i] = [w for w in self.analyzer(t, self.mecab, stopwords=self.stopwords, target_part_of_speech=['noun', 'proper_noun'])]

        self.dictionary = gensim.corpora.Dictionary(texts_words.values())
        self.dictionary.filter_extremes(no_below=no_below, no_above=no_above)
        # dictionary.filter_n_most_frequent(5)
        corpus = [self.dictionary.doc2bow(words) for words in texts_words.values()]

        # LDAの実行
        self.lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                                    id2word=self.dictionary,
                                                    num_topics=num_topics,
                                                    random_state=0)

        # 可視化
        ncols = math.ceil(num_topics/2)
        nrows = math.ceil(self.lda_model.num_topics/ncols)
        fig, axs = plt.subplots(ncols=ncols, nrows=nrows, figsize=(15,7))
        axs = axs.flatten()

        def color_func(word, font_size, position, orientation, random_state, font_path):
            return 'darkturquoise'

        for i in range(self.lda_model.num_topics):

            x = dict(self.lda_model.show_topic(i, 30))
            im = WordCloud(
                font_path=self.font,
                background_color='white',
                color_func=color_func,
                random_state=0
            ).generate_from_frequencies(x)
            axs[i].imshow(im)
            axs[i].axis('off')
            axs[i].set_title('Topic '+str(i))

        plt.tight_layout()
        id_str = id_generator()
        visulize_path = "media/documents/visualize_" + id_str + ".png"
        plt.savefig(visulize_path)

        # pyLDAvisによる可視化
        vis_detail_path = "media/documents/pyldavis_output_" + id_str + ".html"
        vis = gensimvis.prepare(self.lda_model, corpus, self.dictionary, sort_topics=False)
        pyLDAvis.save_html(vis, vis_detail_path)

        return visulize_path, vis_detail_path
    
    # 予測用関数の定義
    def topic_prediction(self, string_input):

        # Fit and transform
        words = self.analyzer(string_input, self.mecab, stopwords=self.stopwords, target_part_of_speech=['noun', 'proper_noun'])
    
        # コーパス作成
        corpus = [self.dictionary.doc2bow(words)]
    #     # tfidfを計算
    #     tfidf = gensim.models.TfidfModel(corpus)
    #     # tfidfのコーパスを作成
    #     corpus_tfidf = tfidf[corpus]
    
        output = list(self.lda_model[corpus])[0]
        topics = sorted(output,key=lambda x:x[1],reverse=True)
        return topics[0][0]