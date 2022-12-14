'''
File:   kMeans.py
Author: Jason Cusati
Course: ECE-5424: Advanced Machine Learning
Date:   11/28/2022
Description:
    kMeans model to analyze NBA positions.
'''

import pandas as pd
import lib.modelCommon as common

import sklearn
import numpy as np
import matplotlib.pyplot as plt
# %matplotlib inline
from mpl_toolkits.mplot3d import Axes3D
import seaborn
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import collections
#import plotly.graph_objects as go


def modifyDataForModel(df: pd.DataFrame,
                       INCLUDE_POS_FLAG, THREE_POS_FLAG) -> pd.DataFrame:
    # Remove Features
    REMOVE_FEATURES = ['ID', 'Year', 'Player', 'Tm', 'Pos']

    # Also delete position features if they should not be used in modeling.
    if not INCLUDE_POS_FLAG:
        if THREE_POS_FLAG:
            REMOVE_FEATURES.extend(["Pos_G", "Pos_F", "Pos_C"])
        else:
            REMOVE_FEATURES.extend(["Pos_PG", 'Pos_SG',
                                    "Pos_SF", "Pos_PF",
                                    "Pos_C"])

    df = df.drop(columns=REMOVE_FEATURES)

    return df


def plotInertia(inertia: [], years: list):
    fig = go.Figure(data=go.Scatter(x=np.arange(1, 50), y=inertia))
    fig.update_layout(title=f"Inertia vs Cluster Number {years[0]} to {years[1]}", xaxis=dict(range=[0, 50], title="Cluster Number"),
                      yaxis={'title': 'Inertia'},
                      annotations=[
                          dict(
                              x=4,
                              y=inertia[3],
                              xref="x",
                              yref="y",
                              text="Elbow!",
                              showarrow=True,
                              arrowhead=7,
                              ax=20,
                              ay=-40
                          )
                      ])
    fig.show()


def runKmeans(df: pd.DataFrame, YEARS: list, INCLUDE_POS, THREE_POS_FLAG,
              APPLY_PCA: bool, VARIANCE: float):
    print("---- Start kMeans Clustering model ----")
    mod_data = modifyDataForModel(df, INCLUDE_POS, THREE_POS_FLAG)
    X = common.normalizeData(mod_data.to_numpy())

    if APPLY_PCA:
        common.createElbowPlots(len(mod_data.columns), X, YEARS)
        X = common.pcaTransform(X, VARIANCE)

    print("** Data for Model Modification: COMPLETE")

    inertia = []
    for i in range(5, 6):
        print(f"** Model3 (KMeans): RUN kMeans with {i} clusters \n")
        kmeans = KMeans(n_clusters=i,
                        init='k-means++',
                        max_iter=300,
                        n_init=10,
                        random_state=0)
        pred_y = kmeans.fit_predict(X)

        inertia.append(kmeans.inertia_)
        df.loc[:, f'Cluster{i}'] = pred_y

        print("Inertia:\t")
        print(kmeans.inertia_)

        print("Clusters (result of k-means)")
        print(collections.Counter(pred_y))

        print("Ground truth")
        print(collections.Counter(df['Pos']))
        plt.figure(figsize=(10, 6))
        plt.scatter(df['Pos'], X[:, 1])
        plt.scatter(kmeans.cluster_centers_[:, 0],
                    kmeans.cluster_centers_[:, 1],
                    s=300,
                    c='red')
        plt.show()

    #plotInertia(inertia, YEARS)

    # Ensure that all labels are corrected to be in range [0, 4]
    df.loc[:, 'Cluster'] = df['Cluster5']

    common.calcPositionConc(df, "kMeans", YEARS, THREE_POS_FLAG)

    return common.reportClusterScores(df, YEARS, INCLUDE_POS)
