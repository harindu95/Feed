import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from sklearn import cluster
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QRunnable, QUrl
from PyQt6.QtCore import pyqtSignal, QObject, Qt, QEventLoop, QThreadPool
from keybert import KeyBERT
from common import Connection

stats = {}

def show_clusters(task,view:QWebEngineView):
    images = task.word_clouds
    html = "<html><body>{}</body></html>"
    body = ""
    x = 0
    for img in images:
        svg = img.to_svg()
        section = "<div>{}<p>Cluster {}</p></div>".format(svg, x)
        body += section
        x += 1

    html = html.format(body)
    view.page().setHtml(html, QUrl("about:wordcloud"))

def extract_keywords(view: QWebEngineView,callback=show_clusters):
    def handle_txt(txt):
        task = KeywordTask(txt, stats)
        task.c.done.connect(lambda task=task,view=view: callback(task,view))
        QThreadPool.globalInstance().start(task)
        # print(txt)
    from common import plain_text
    if view.page().url().toString() != "about:wordcloud":
        if "youtube" in view.page().url().toString():
            # view.page().toHtml(lambda html: print(plain_text(html)))
            # view.page().toPlainText(lambda txt: print(txt))
            return
        # print(view.page().url().toString())
        view.page().toPlainText(handle_txt)
    # print(text)


# K-Means

corpus = []


def run_KMeans(max_k, data):
    max_k += 1
    kmeans_results = dict()
    for k in range(1, max_k):
        kmeans = cluster.KMeans(n_clusters=k, init='k-means++',
                                n_init=10, tol=0.0001, random_state=1, algorithm='full')

        kmeans_results.update({k: kmeans.fit(data)})

    return kmeans_results


def printAvg(avg_dict):
    for avg in sorted(avg_dict.keys(), reverse=True):
        print("Avg: {}\tK:{}".format(avg.round(4), avg_dict[avg]))


def get_top_features_cluster(features, tf_idf_array, prediction, n_feats):
    labels = np.unique(prediction)
    dfs = []
    for label in labels:
        id_temp = np.where(prediction == label)  # indices for each cluster
        # returns average score across cluster
        x_means = np.mean(tf_idf_array[id_temp], axis=0)
        # indices with top 20 scores
        sorted_means = np.argsort(x_means)[::-1][:n_feats]
        best_features = [(features[i], x_means[i]) for i in sorted_means]
        df = pd.DataFrame(best_features, columns=['features', 'score'])
        dfs.append(df)
    return dfs


def plotWords(dfs, n_feats):
    # plt.figure(figsize=(8, 4))
    for i in range(0, len(dfs)):
        # plt.title(("Most Common Words in Cluster {}".format(i)), fontsize=10, fontweight='bold')
        # sns.barplot(x = 'score' , y = 'features', orient = 'h' , data = dfs[i][:n_feats])
        print(dfs[i])
        # plt.show()

def centroidsDict(centroids, index):
    a = centroids.T[index].sort_values(ascending = False).reset_index().values
    centroid_dict = dict()

    for i in range(0, len(a)):
        centroid_dict.update( {a[i,0] : a[i,1]} )

    return centroid_dict




class KeywordTask(QRunnable):

    def __init__(self, txt, stats, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.txt = txt
        self.stats = stats
        self.word_clouds = []
        self.c = Connection()

    def process_corpus(self):
        index = 0
        corpus = [self.txt, 'Second document two']
        # Replaces the ASCII '�' symbol with '8'
        corpus[index] = corpus[index].replace(u'\ufffd', '8')
        corpus[index] = corpus[index].replace(
            ',', '')          # Removes commas
        corpus[index] = corpus[index].rstrip(
            '\n')              # Removes line breaks
        # Makes all letters lowercase
        corpus[index] = corpus[index].casefold()

        # removes specials characters and leaves only words
        corpus[index] = re.sub('\W_', ' ', corpus[index])
        # removes numbers and words concatenated with numbers IE h4ck3r. Removes road names such as BR-381.
        corpus[index] = re.sub("\S*\d\S*", " ", corpus[index])
        # removes emails and mentions (words with @)
        corpus[index] = re.sub("\S*@\S*\s?", " ", corpus[index])
        # removes URLs with http
        corpus[index] = re.sub(r'http\S+', '', corpus[index])
        corpus[index] = re.sub(r'www\S+', '', corpus[index])
        return corpus

    def run(self):
        corpus.append(self.txt)
        # if len(corpus) < 2:
        #     return
        vectorizer = TfidfVectorizer(stop_words='english')
        X = vectorizer.fit_transform(corpus)
        features = vectorizer.get_feature_names_out()
        tf_idf = pd.DataFrame(data=X.toarray(), columns=features)
        final_df = tf_idf

        # Running Kmeans
        if len(corpus) < 8:
            k = len(corpus)
        else:
            k = 8
        kmeans_results = run_KMeans(k, final_df)

        best_result = k
        if(k > 3):
            import math
            # best_result = math.floor((k+1)/2) 
            best_result = k
        # kmeans = kmeans_results.get(best_result)
        print("k: {} best:{} kmeans:{}".format(k,best_result, kmeans_results))
        kmeans = kmeans_results.get(best_result)

        final_df_array = final_df.to_numpy()
        prediction = kmeans.predict(final_df)
        n_feats = 50
        dfs = get_top_features_cluster(
            features, final_df_array, prediction, n_feats)      

        centroids = pd.DataFrame(kmeans.cluster_centers_)
        centroids.columns = final_df.columns
        self.generateWordClouds(centroids)
        self.c.done.emit()


        # kw_model = KeyBERT()
        # keywords = kw_model.extract_keywords(self.txt)
        # for keyword,freq in keywords:
        #     if keyword in self.stats:
        #         self.stats[keyword] += freq
        #     else:
        #         self.stats[keyword] = freq
        # print("{} rows".format(final_df.shape[0]))
        # print(final_df.T.nlargest(20, 0))
        # print(self.stats)
    
    def generateWordClouds(self,centroids):
        from wordcloud import WordCloud
        
        for i in range(0, len(centroids)):
            wordcloud = WordCloud(max_font_size=100, background_color = 'white')
            centroid_dict = centroidsDict(centroids, i)        
            wordcloud.generate_from_frequencies(centroid_dict)
            self.word_clouds.append(wordcloud)

        