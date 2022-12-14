'''
File:   modelCommon.py
Author: John Smutny
Course: ECE-5424: Advanced Machine Learning
Date:   11/19/2022
Description:
    Support file to 'main.py'
    Collection of functions common to all used models such as normalization,
    scoring the resulting clusters, and creating 'Position Concentration PIE
    Charts'.
'''

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.preprocessing import StandardScaler, normalize
from sklearn.decomposition import PCA
import numpy as np

from sklearn.metrics import calinski_harabasz_score as C_H_score
from sklearn.metrics import silhouette_score as S_score
from sklearn.metrics import davies_bouldin_score as D_B_score
from sklearn.preprocessing import MinMaxScaler


def normalizeData(np_array):
    scaler = MinMaxScaler()
    x_scaled = scaler.fit_transform(np_array.tolist())

    x_normalized = normalize(x_scaled)

    return x_normalized


def createElbowPlots(numFeatures: int, X, YEARS: list):
    print("**** Generate an Elbow Plot showing the data reduction curve.")
    pca = PCA(n_components=numFeatures)
    pca.fit(X)

    # Display the Elbow Plot explaining the optimal # of PCA components
    plt.figure()
    plt.plot(np.cumsum(pca.explained_variance_ratio_))
    plt.xlabel('Number of PCA Components')
    plt.ylabel('Explained Variance (%)')
    plt.savefig('../model/ref/Elbow_Plot_PCA-{}-{}.png'.format(YEARS[0],
                                                       YEARS[1],
                                                       dpi=100))


def pcaTransform(df: pd.DataFrame, VARIANCE: int) -> pd.DataFrame:
    print("*** Apply PCA: Data Reduction")
    X = df

    # Perform PCA on transformed dataset by using components with a
    # percentage of the explained dataset variance.
    pca = PCA(n_components=VARIANCE)
    pca.fit(X)
    print(
        "explained variance ratio by Components: {:.2f}%"
            "\n\tComponent (0-100%): {}".format(
            sum(pca.explained_variance_ratio_*100),
            pca.explained_variance_ratio_*100)
    )

    X_transform = pca.transform(X)
    return X_transform


def calcPositionConc(df: pd.DataFrame, MODEL_NAME, YEARS: list, THREE_POS_FLAG):
    # TODO - Consider making the PIE charts 3 positions no matter what to
    #  simplify interpretation.
    ####################################
    # Calculate the position concentration in each cluster.
    #   Output files describing the player position concentrations in each
    #   cluster. Outputs 1) a .csv with 0-1 percentages of each position in
    #   each cluster and 2) a .png PIE chart visual of the data in output
    #   artifact 1).
    #
    # Requirements:
    #   Clusters must be labeled as 0 to x
    #   Function assumes that the player's are clustered based on 5 positions.

    # TODO - Hardcode the order of the 'pos' fields from smallest -> largest.
    #  When INCLUDE_POS_FLAG=FALSE, avoid having the order on the pie chart
    #  be random.
    col = ['Total']

    # Add 'pos' columns for PIE chart in a specific order.
    if THREE_POS_FLAG:
        col.extend(['G', 'F', 'C'])
    else:
        col.extend(['PG', 'SG', 'SF', 'PF', 'C'])

    df_conc = pd.DataFrame(columns=col)

    # i = cluster # (1-5)
    # j = specific position
    fig, ax = plt.subplots(nrows=1, ncols=len(df['Pos'].unique()), squeeze=True)
    for i in range(0, len(col[1:])):
        plotOffset = i + 1
        df_x = df[df['Cluster'] == i]
        count = [len(df_x)]

        for j in col[1:]:
            count.append(round(len(df_x[(df_x['Pos'] == j)])/count[0], 3))

        # Publish Pie chart of concentrations
        # TIP - Use the hyperparameter 'autopct='%.1f'' to print values.
        # TODO - Do better styling https://www.pythoncharts.com/matplotlib/pie-chart-matplotlib/
        ax[plotOffset-1].set_title("Cluster {}".format(i))
        if i == 1:
            ax[plotOffset-1].pie(count[1:], labels=col[1:], normalize=True)
        else:
            ax[plotOffset-1].pie(count[1:], normalize=True)

        # Save the concentrations to publish a .csv
        df_conc = df_conc.append(
                        pd.Series(count, index=df_conc.columns),
                        ignore_index=True)

    # Publish the resulting concentrations
    df_conc.to_csv("../model/ref/CONC_{}_Season_Stats_{}-{}.csv".format(
        MODEL_NAME,
        YEARS[0],
        YEARS[1]))

    # Publish resulting PIE charts of the position concentrations
    fig.legend(title="Position Concentrations {}-{}".format(
                YEARS[0],
                YEARS[1]))
    fig.savefig("../model/PIE_{}_Season_Stats_{}-{}".format(
                MODEL_NAME,
                YEARS[0],
                YEARS[1]))
    fig.clf()

    print("** Model {} Position Extraction: COMPLETE".format(MODEL_NAME))


#========================================

def calcSilhouetteCoefficient(df_data: pd.DataFrame, df_labels: pd.DataFrame):
    score = S_score(df_data.to_numpy().tolist(),
                    df_labels.to_numpy().tolist(),
                    metric='euclidean')

    return round(score, 3)


def calcCalinskiHarabaszScore(df_data: pd.DataFrame, df_labels: pd.DataFrame):
    score = C_H_score(df_data.to_numpy().tolist(),
                      df_labels.to_numpy().tolist())

    return round(score, 3)


def calcDaviesBouldinIndex(df_data: pd.DataFrame, df_labels: pd.DataFrame):
    score = D_B_score(df_data.to_numpy().tolist(),
                      df_labels.to_numpy().tolist())

    return round(score, 3)

def reportClusterScores(df: pd.DataFrame, YEARS: list, INCLUDE_POS):
    '''
    Various calculations of cluster tightness to judge how well the
    clustering models worked.
    1) Calinski-Harabasz Score: "Variance Ratio Criterion - a higher score
                                    relates to a model with better defined
                                    clusters."
                                Range: [0, inf]
    2) Silhouette Coefficient:  "higher score relates to a model with better
                                    defined clusters."
                                Range: [-1, 1]
    3) Davies-Bouldin Index: "Zero is the lowest possible score. Values closer
                                to zero indicate a better partition."
                                Range: [0, inf]
    REFERENCE: https://scikit-learn.org/stable/modules/clustering.html

    :param df: Input dataframe including ALL features, not just features used in
                modeling
    :param INCLUDE_POS: FLAG to state if a ployer's position was considered
                in modeling
    '''

    # Drop features that were not used in modeling
    REMOVE_FEATURES = ['ID', 'Player', 'Tm', 'Pos']
    if not INCLUDE_POS:
        if len(df[df['Pos'] == 'G']) > 0:
            REMOVE_FEATURES.extend(["Pos_G", "Pos_F", "Pos_C"])
        else:
            REMOVE_FEATURES.extend(["Pos_PG", 'Pos_SG',
                                    "Pos_SF", "Pos_PF",
                                    "Pos_C"])
    REMOVE_FEATURES.extend(['Cluster'])

    # Divide the existing dataset into FEATURES and LABELS for scoring.
    df_data = df.drop(columns=REMOVE_FEATURES)
    df_labels = df['Cluster']

    tightness1 = calcCalinskiHarabaszScore(df_data, df_labels)
    print("Calinski_Harabasz_Score = {:2}".format(tightness1))

    tightness2 = calcSilhouetteCoefficient(df_data, df_labels)
    print("SilhouetteCoefficient_Score = {:2}".format(tightness2))

    tightness3 = calcDaviesBouldinIndex(df_data, df_labels)
    print("Davies-Bouldin Index = {:2}".format(tightness3))

    return ["{}-{}".format(YEARS[0], YEARS[1]),
            tightness1, tightness2, tightness3]


def combinePlayers():
    '''
    Run this function once on an already established dataset of player
    statistics gathered from various sources.

    INPUTS:
    1) Players.csv - Original Player biography information from kaggle user
                        drgilermo.
                    https://www.kaggle.com/datasets/drgilermo/nba-players
                    -stats?select=Players.csv
    2) Players_PENDING.xlsx - Hand gathered data from
                                www.basketball-reference.com containing player
                                Height, Weight and other background
                                information. Height/Weight are extracted by
                                year. Each sheet in the .xlsx file is a
                                different year.
    '''

    PATH1 = "../data/input/Players.csv"
    PATH2 = "../data/input/Players_PENDING.xlsx"

    YEARS = ['2018', '2019', '2020', '2021', '2022']
    year = YEARS[0]


    df_p1 = pd.read_csv(PATH1)

    names = ['name', 'Height', 'Weight']
    df_p2 = pd.read_excel(PATH2, sheet_name=year, usecols='B,D:E')
    df_p2 = df_p2.rename(columns={'Name': 'Player',
                                  'Height': 'height',
                                  'Weight': 'weight'})

    df_p1 = df_p1.join(df_p2.set_index('Player'), on='Player')

    df_p1.to_csv('../data/input/Players_1950_2022.csv')


def calcEntropy():

    import scipy.stats as sci

    modelList = ['Hierarchy', 'kMeans', 'SOM']
    YEAR_PAIRS = [[1971, 1980],
                     [1981, 1990],
                     [1991, 2000],
                     [2001, 2010],
                     [2011, 2020]]

    #writer = pd.ExcelWriter('Entropy2.xlsx', engine='xlsxwriter')
    df_Entropy = pd.DataFrame(columns=modelList)

    for model in modelList:
        for YEARS in YEAR_PAIRS:
            df = pd.read_csv("CONC_{}_Season_Stats_{}-{}.csv".format(model,
                                                                     YEARS[0],
                                                                     YEARS[1]),
                             index_col=0)
            df = df.drop(columns='Total')


            # loop through all clusters. Get average entropy of the clusters
            entropyAvg = []
            for row in range(len(df)):
                array = df.iloc[row, :5].to_numpy()

                entropyAvg.append(sci.entropy(array))

            #df_Entropy.loc[YEARS[1], model] = sum(entropyAvg)/len(entropyAvg)
            df_Entropy.loc["{}s".format(YEARS[0]-1), model] = \
                round(sum(entropyAvg) / len(entropyAvg), 3)
            df_Entropy.loc["{}s".format(YEARS[0] - 1),
                           "{}-Range".format(model)] =  \
                round(max(entropyAvg) - min(entropyAvg), 3)


    df_Entropy.to_excel('Entropy-ClusterAvgs.xlsx')

