from items import Items
import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from sklearn import cluster
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineLoadingInfo, QWebEngineScript
from PyQt6.QtCore import QRunnable, QUrl, QFile
from PyQt6.QtCore import pyqtSignal, QObject, Qt, QEventLoop, QThreadPool, QTimer
from keybert import KeyBERT
from common import Connection

stats = {}


started_urls = {}


def extract_text(view: QWebEngineView, loadinfo, settings):

    url = view.page().url().toString()
    if url.startswith('about:'):
        return
    status = loadinfo.status()

    def handle_txt(txt):
        if txt is None:
            return
        if len(txt.strip()) < 1:
            return
        # print(txt)
        # from keywords import corpus
        task = GetText(txt, settings.corpus)
        task.run()
        QThreadPool.globalInstance().start(task, 3)

    script = '''
    document.body.innerText;'''

    def run_javascript():
        view.page().runJavaScript(script, handle_txt)

    if status == QWebEngineLoadingInfo.LoadStatus.LoadStartedStatus:
        print("load status", status)
        QTimer.singleShot(200, run_javascript)
    if status == QWebEngineLoadingInfo.LoadStatus.LoadSucceededStatus:
        print("load status", status)
        run_javascript()


# K-Means


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
    a = centroids.T[index].sort_values(ascending=False).reset_index().values
    centroid_dict = dict()

    for i in range(0, len(a)):
        centroid_dict.update({a[i, 0]: a[i, 1]})

    return centroid_dict


def rank_items(items, centroids):
    corpus = [item.title + '' + item.description for item in items]
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(corpus)
    features = vectorizer.get_feature_names_out()
    tf_idf = pd.DataFrame(data=X.toarray(), columns=features)
    num_rows = len(corpus)
    for i in range(len(centroids)):
        r = centroids.iloc[[i]]
        matrix = pd.concat([r] * num_rows, ignore_index=True)
        t = tf_idf.mul(matrix, axis='columns', fill_value=0)
        sum = t.sum(axis='columns')
        for index, value in sum.items():
            if i == 0:
                items[index].rank = value
            elif items[index].rank < value:
                items[index].rank = value

    return items

class GetText(QRunnable):
    def __init__(self, txt, corpus, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.txt = txt.strip()
        self.corpus = corpus

    def run(self):
        if len(self.txt) > 0:
            if len(self.corpus) == 0 or self.corpus[-1] != self.txt:
                print("Added to corpus")
                self.corpus.append(self.txt)


def get_centroids(corpus):
    if len(corpus) == 0:
        print("No text found: len(corpus) == 0")
        return
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
    if (k > 3):
        # import math
        # best_result = math.floor((k+1)/2)
        best_result = k
    # kmeans = kmeans_results.get(best_result)
    print("k: {} best:{} kmeans:{}".format(k, best_result, kmeans_results))
    kmeans = kmeans_results.get(best_result)
    centroids = pd.DataFrame(kmeans.cluster_centers_)
    centroids.columns = final_df.columns
    return centroids


def generateWordClouds(centroids):
    from wordcloud import WordCloud
    word_clouds = []
    for i in range(0, len(centroids)):
        wordcloud = WordCloud(max_font_size=100, background_color='white')
        centroid_dict = centroidsDict(centroids, i)
        wordcloud.generate_from_frequencies(centroid_dict)
        word_clouds.append(wordcloud)

    return word_clouds
