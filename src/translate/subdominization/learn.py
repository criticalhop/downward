#!/usr/bin/python

import numpy as np
import pandas as pd

import pickle

import sklearn

from sklearn import tree
from sklearn import preprocessing
from sklearn import metrics
from sklearn import datasets
from sklearn import metrics

from sklearn.pipeline import make_pipeline
from sklearn.naive_bayes import BernoulliNB
from sklearn.naive_bayes import GaussianNB
from sklearn.base import BaseEstimator
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.svm import SVC

from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegressionCV

from sklearn.model_selection import KFold
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report



class LearnRules():
    
    def __init__(self, isBalanced=False, modelType='LRCV', fileTraining ='', njobs=-1, testSize=0.05):
        '''
        Constructor take parameters:
        isBalanced, Boolean for balance the target of prediction in training phase
        modelType = 'LRCV', 'LG', 'RF' , 'SVMCV','NBB', 'NBG'. 'DT'; 
                       Logistic Regression, 
                       Logistic Regression with Cross VAlidation, 
                       Random Forest, 
                       Support Vector MAchine with CV grid search,
                       Naive Bayes classifier with Bernoulli estimator
                       Naive Bayes classifier with Gaussian estimator 
                       DT is decision Tree 
        you ahve to give:
                  'fileTraining' that is a CSV file containing in each line the feature vectors (validation of rules), and the las column the target to be predicted
                  
        njobs, to paralellice the training phase, default njobs=-1 to get the availables cores
        testSize, is to define the size of test set. Default value calculates the test set random, with a 5% of the training set.
        '''
        
        self.tesSize=testSize
        self.njobs=njobs
        self.modelType=modelType
        
        if (fileTraining !='') :
            self.isBalanced=  'balanced' if isBalanced else None

            dataset= pd.read_csv(fileTraining, header=None)

            # separate in features an target
            X, y = dataset.iloc[:,:-1], list(dataset.iloc[:, -1])
    
            #if we want to saparate in train an test
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=self.tesSize, random_state=0)
            self.y_test=y_test
            self.X_test=X_test
           
    
            X=X_train
            y=y_train
    
            # Standarize features
            scaler = StandardScaler(with_std=True)
    
            X_std = scaler.fit_transform(X)
            
            
            if (modelType=='LR'):
                # Create decision tree classifer object
                clf = LogisticRegression(random_state=0
                         ,class_weight=self.isBalanced
                         )
                self.model = clf.fit(X_std, y)
                #model_simple = clf.fit(X, y)
                print(np.std(X_std, 0)*self.model.coef_)
            elif (modelType=='LRCV'):
                
                #fold = KFold(len(y), n_folds=20, shuffle=True, random_state=1)
                fold = KFold(n_splits=20, shuffle=True, random_state=1)
                searchCV = LogisticRegressionCV(
                Cs=list(np.power(10.0, np.arange(-10, 10)))
                    ,penalty='l2'
                    ,scoring='roc_auc'
                    ,cv=fold
                    ,random_state=777
                    ,max_iter=10000
                    ,fit_intercept=True
                    ,solver='newton-cg'
                    ,tol=10
                    ,class_weight=self.isBalanced
                    ,n_jobs=self.njobs
                    )

                self.model = searchCV.fit(X_std , y)
                print("the magnitude of this matrix, give an idea of the featres influences")
                print(np.std(X_std, 0)*self.model.coef_)

                
            elif (modelType=='RF'):
                clf_RG = RandomForestClassifier(n_jobs=self.njobs, random_state=0,class_weight=self.isBalanced)
                self.model = clf_RG.fit(X_std, y )   
                
            elif (modelType=='SVMCV'):
                classifier_pipeline=None
                #tuned_parameters = [{'kernel': ['rbf'], 'gamma': [1e-3, 1e-4],
                #     'C': [1, 10, 100, 1000]},
                #    {'kernel': ['linear'], 'C': [1, 10, 100, 1000]}]
                params={'kernel':['linear', 'rbf', 'poly', 'sigmoid'],
                    'C':[1, 5, 10],
                    'degree':[2,3],
                    'gamma':[0.025, 1.0, 1.25, 1.5, 1.75, 2.0],
                    'coef0':[2, 5, 9],
                    'class_weight': [ self.isBalanced]}
                
                clf = GridSearchCV(SVC(), params, cv=3,
                       scoring='roc_auc',n_jobs=self.njobs)
                self.model =clf.fit(X_std , y)
            elif (modelType=='SVM'):
                clf = SVC( class_weight=self.isBalanced)     #print self.model.predict_proba(self.X_test)
                self.model =clf.fit(X_std , y)
            elif (modelType=='NBB'):
                # Create decision tree classifer object
                clf= None
                if (not self.isBalanced):
                    clf = BernoulliNB()
                else:
                    clf= make_pipeline(scaler,BernoulliNB())
                self.model = clf.fit(X_std, y)
            elif (modelType=='NBG'):
                # Create decision tree classifer object
                clf = GaussianNB()
                self.model = clf.fit(X_std, y)
            elif (modelType=='DT'):

                clf  = tree.DecisionTreeClassifier(class_weight=self.isBalanced)
                self.model  = clf.fit(X_std, y)
            else:
                SyntaxError("Error in modelType = 'LRCV', 'LG', 'RF', 'SVM', 'SVMCV', 'NBB', 'NBG' , 'DT'; \nLogistic Regression, Logistic Regression with Cross Validation, \nRandom Forest or Support Vector Machine with CV, \n DT  is decision Tree ")        
        else:
            SystemError("fileTrain should not be empty.")  

    def returnProbClasesList(self,X_t):
        return self.model.predict_proba(X_t)
 
    def returnProbClasesOne(self,x_t):
        if self.model.probability:
            return self.model.predict_proba([x_t])
        else:
            return None
            
    def returnClassesList(self,X_t):
        return self.model.predict(X_t)
 
    def returnClassesOne(self,x_t):
        return self.model.predict([x_t])

    def printStats(self):
        y_pred= self.model.predict_proba(self.X_test)
        y_predClass= self.model.predict(self.X_test)
        print(classification_report(list(self.y_test), y_predClass))
        print(confusion_matrix(self.y_test, y_predClass))
        
        if self.modelType.startswith('LR'):
            print("Coefficin matrix")
            print(self.model.coef_)
        elif (self.modelType.startswith('RF') or self.modelType.startswith('DT')):
            print(self.model.feature_importances_)



