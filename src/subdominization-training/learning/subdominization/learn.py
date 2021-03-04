#!/usr/bin/python

import sys
import os
import numpy as np
import pandas as pd

import sklearn
#import autosklearn.classification
import autosklearn.metrics

from sklearn import datasets
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (brier_score_loss, precision_score, recall_score,
                                     f1_score)
from sklearn.calibration import CalibratedClassifierCV, calibration_curve

from sklearn.pipeline import make_pipeline
import matplotlib.pyplot as plt
from sklearn import tree
from sklearn.naive_bayes import BernoulliNB
from sklearn.naive_bayes import GaussianNB
from sklearn.base import BaseEstimator
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.metrics import average_precision_score
from sklearn.svm import SVC
from sklearn.svm import SVR
from pylab import rcParams
from sklearn import preprocessing
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import RANSACRegressor
from sklearn.model_selection import train_test_split
from sklearn import metrics 
from sklearn.metrics import classification_report

from sklearn.kernel_ridge import KernelRidge

from sklearn.linear_model import LogisticRegression
from sklearn import datasets
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegressionCV
from sklearn.model_selection import KFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor

from sklearn.neighbors import KNeighborsClassifier
from sklearn.neighbors import KNeighborsRegressor

from sklearn.dummy import DummyClassifier

from sklearn import metrics
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
import pickle
from random import *
from sklearn.metrics import r2_score
from sklearn.metrics import make_scorer 

randBinList = lambda n: [randint(0,1) for b in range(1,n+1)]


import helpers


from IPython import embed



class LearnRules():
    
    def __init__(self, isBalanced=False, modelType='LRCV', training_file ='', njobs=1, testSize=0.03, remove_duplicate_features=True, take_max_for_duplicates=True):
        '''
        Constructor take parameters:
        isBalanced, Boolean for balance the target of prediction in training phase
        modelType = 'LRCV', 'LG', 'RF' , 'SVMCV','NBB', 'NBG'. 'DT'; 
                       Logistic Regression, 
                       Logistic Regression with Cross Validation, 
                       Random Forest, 
                       Support Vector MAchine with CV grid search,
                       Naive Bayes classifier with Bernoulli estimator
                       Naive Bayes classifier with Gaussian estimator 
                       DT is decision Tree 
        you ahve to give:
                  'training_file' that is a CSV file containing in each line the feature vectors (validation of rules), and the las column the target to be predicted
                  
        njobs, to paralellice the training phase, default njobs=-1 to get the availables cores
        testSize, is to define the size of test set. Default value calculates the test set random, with a 5% of the training set.
        '''

        self.modelType = modelType
        self.isBalanced = isBalanced
        self.remove_duplicate_features = remove_duplicate_features
        self.take_max_for_duplicates = take_max_for_duplicates
        
        self.is_classifier = False
        
        self.is_empty = True
        
        if (training_file !='') :
            if os.stat(training_file).st_size == 0:
                X_std = [0]
                y = [0]
            else:
                
                dataset = helpers.get_dataset_from_csv(training_file, not remove_duplicate_features, take_max_for_duplicates)
                
                if (dataset is None):
                    return
                    
                self.is_empty = False # we actually train the model
                
                # print dataset.shape
                # separate in features an target
                X, y = dataset.iloc[:,:-1], list(dataset.iloc[:, -1])
        
                # if we want to separate into train and test sets
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=testSize, random_state=0)
        
                X=X_train
                y=y_train
        
                # Standarize features
                scaler = StandardScaler(copy=True, with_mean=True, with_std=True)
        
                X_std = scaler.fit_transform(X)
                
            if max(y) == 0:
                print(training_file, "was never used, returning zero classifier")
                #negative = DummyClassifier(strategy="constant", constant=[1,0])
                negative = DummyClassifier(strategy="constant", constant=0)
                #negative.n_outputs_ = 2
                self.model = negative.fit(X_std, y)
                self.is_classifier = True
            elif min(y) == 1:
                print(training_file, "WARNING! always needed! returning TRUE classifier. Check your data!")
                #negative = DummyClassifier(strategy="constant", constant=[0,1])
                negative = DummyClassifier(strategy="constant", constant=1)
                #negative.n_outputs_ = 2
                self.model = negative.fit(X_std, y)
                self.is_classifier = True
            elif (modelType=='LOGR'):
                # Create decision tree classifer object
                clf = LogisticRegression(random_state=0,
                                         class_weight='balanced' if self.isBalanced else None)
                self.model = clf.fit(X_std, y)
                self.is_classifier = True
                #print(np.std(X_std, 0) * self.model.coef_)
            elif (modelType == "RANSAC"):
                regr = RANSACRegressor()
                self.model = regr.fit(X_std, y)
            elif (modelType=='LINR'):
                regr = LinearRegression(n_jobs=njobs)
                self.model = regr.fit(X, y)
                #print(self.model.coef_)
            elif (modelType=='LOGRCV'):
                #fold = KFold(len(y), n_folds=20, shuffle=True, random_state=1)
                fold = KFold(n_splits=5, shuffle=True, random_state=1)
                searchCV = LogisticRegressionCV(
                            #Cs = list(np.power(10.0, np.arange(-10, 10))),
                            penalty = 'l2',
                            scoring = 'roc_auc',
                            cv = fold,
                            random_state = 777,
                            max_iter = 100,
                            fit_intercept = True,
                            solver = 'newton-cg',
                            multi_class = "multinomial",
                            tol = 0.00001,#10,
                            class_weight = 'balanced' if self.isBalanced else None,
                            n_jobs = njobs
                        )
                self.model = searchCV.fit(X_std , y)
                print("the magnitude of this matrix, gives an idea of the features' influences")
                print(np.std(X_std, 0) * self.model.coef_)
            elif (modelType == 'RF'):
                # set n_jobs to 1 to fix the low CPU usage when computing estimates
                clf_RG = RandomForestClassifier(n_jobs=1, random_state=0, class_weight='balanced' if self.isBalanced else None)
                self.model = clf_RG.fit(X_std, y)
                self.is_classifier = True
            elif (modelType == 'SVCCV'):
                classifier_pipeline=None
                #tuned_parameters = [{'kernel': ['rbf'], 'gamma': [1e-3, 1e-4],
                #     'C': [1, 10, 100, 1000]},
                #    {'kernel': ['linear'], 'C': [1, 10, 100, 1000]}]
                params={'kernel': ['linear', 'rbf', 'poly', 'sigmoid'],
                        'C': [1, 5, 10],
                        'degree': [2,3],
                        'gamma': [0.025, 1.0, 1.25, 1.5, 1.75, 2.0],
                        'coef0': [2, 5, 9],
                        'class_weight': ['balanced' if self.isBalanced else None]}
                
                clf = GridSearchCV(SVC(probability=True),
                                   params,
                                   cv=3,
                                   scoring='roc_auc',
                                   n_jobs=njobs)
                self.model =clf.fit(X_std, y)
                self.is_classifier = True
                #print self.model.predict_proba(X_test)
            elif (modelType=='HCRF'):
                print("TRAINING HCRF")
                dataset_positive = dataset[dataset.iloc[:, -1] > 0]
                dataset_negative = dataset[dataset.iloc[:, -1] == 0]
                sz = int(len(dataset_positive)*0.6)
                if(sz >= len(dataset_negative)-10):
                    dataset_negative_smpl = dataset_negative
                else:
                    dataset_negative_smpl = dataset_negative.sample(n=sz)
                dataset_rb_merged = pd.concat([dataset_positive, dataset_negative_smpl])
                dataset_rebalanced = dataset_rb_merged.sample(frac = 1)
                X_train, y_train = dataset_rebalanced.iloc[:,:-1], list(dataset_rebalanced.iloc[:, -1])
                testSize = 1 - 25000.0/len(y_train)
                if testSize > 0:
                    X_train, X_test, y_train, y_test = train_test_split(X_train, y_train, test_size=testSize, random_state=None)
                from sklearn.ensemble import RandomForestClassifier
                clf = RandomForestClassifier(
                    n_estimators=1000, 
                    max_depth=50, 
                    n_jobs=-1,
                    max_features=0.4,
                    criterion='entropy',
                    class_weight=None)
                                
                name = "RandomForest"
                self.model = clf.fit(X_train, y_train)
                #print self.model.predict_proba(X_test)
                self.is_classifier = True

                from sklearn.metrics import precision_recall_curve
                from sklearn.metrics import plot_precision_recall_curve
                import matplotlib.pyplot as plt
                fig_index = 1

                y_pred = clf.predict(X_test)
                y_pred_nrb = clf.predict(X[:5000])
                y_test_nrb = y[:5000]
                try:
                    rank = sum([x for x in list(y_test_nrb - y_pred_nrb) if x > 0])/len([x for x in list(y_test_nrb) if x > 0])
                except ZeroDivisionError:
                    rank = -1
                try:
                    miss = len([x for x in list(y_test_nrb - y_pred_nrb) if x < 0])/len([x for x in list(y_test_nrb) if x > 0])
                except ZeroDivisionError:
                    miss = -1
                    
                disp = plot_precision_recall_curve(clf, X_test, y_test)
                average_precision = average_precision_score(y_test, y_pred)
                disp.ax_.set_title('2-class Precision-Recall curve: '
                           'AP={0:0.2f}'.format(average_precision))
                print("Saving fig...")
                plt.savefig(f"{training_file}-recall-{average_precision:.2f}-{rank:.4f}-{miss:.3f}.png")
                fig = plt.figure(fig_index, figsize=(10, 10))
                ax1 = plt.subplot2grid((3, 1), (0, 0), rowspan=2)
                ax2 = plt.subplot2grid((3, 1), (2, 0))

                ax1.plot([0, 1], [0, 1], "k:", label="Perfectly calibrated")
                prob_pos = clf.predict_proba(X_test)[:, 1]
                clf_score = brier_score_loss(y_test, prob_pos, pos_label=max(y))
                fraction_of_positives, mean_predicted_value = \
                    calibration_curve(y_test, prob_pos, n_bins=10)

                ax1.plot(mean_predicted_value, fraction_of_positives, "s-",
                     label="%s (%1.3f)" % (name, clf_score))

                ax2.hist(prob_pos, range=(0, 1), bins=10, label=name,
                     histtype="step", lw=2)

                ax1.set_ylabel("Fraction of positives")
                ax1.set_ylim([-0.05, 1.05])
                ax1.legend(loc="lower right")
                ax1.set_title('Calibration plots  (reliability curve)')

                ax2.set_xlabel("Mean predicted value")
                ax2.set_ylabel("Count")
                ax2.legend(loc="upper center", ncol=2)

                plt.tight_layout()
                print("Saving fig...")
                plt.savefig(f"{training_file}-calib.png")
            elif (modelType=='HCSVC'):
                print("TRAINING HC")
                dataset_positive = dataset[dataset.iloc[:, -1] > 0]
                dataset_negative = dataset[dataset.iloc[:, -1] == 0]
                sz = int(len(dataset_positive)*1.5)
                if(sz >= len(dataset_negative)-10):
                    dataset_negative_smpl = dataset_negative
                else:
                    dataset_negative_smpl = dataset_negative.sample(n=sz)
                dataset_rb_merged = pd.concat([dataset_positive, dataset_negative_smpl])
                dataset_rebalanced = dataset_rb_merged.sample(frac = 1)
                X_train, y_train = dataset_rebalanced.iloc[:,:-1], list(dataset_rebalanced.iloc[:, -1])
                testSize = 1 - 7000.0/len(y_train)
                if testSize > 0:
                    X_train, X_test, y_train, y_test = train_test_split(X_train, y_train, test_size=testSize, random_state=None)
                scaler = StandardScaler(copy=True, with_mean=True, with_std=True)
                X_std = scaler.fit_transform(X_train)
                clf = SVC(probability=True, class_weight='balanced')
                name = "SVC"
                self.model = clf.fit(X_std, y_train)
                #print self.model.predict_proba(X_test)
                self.is_classifier = True

                from sklearn.metrics import precision_recall_curve
                from sklearn.metrics import plot_precision_recall_curve
                import matplotlib.pyplot as plt
                fig_index = 1

                y_pred = clf.predict(X_test)
                y_pred_nrb = clf.predict(X[:5000])
                y_test_nrb = y[:5000]
                try:
                    rank = sum([x for x in list(y_test_nrb - y_pred_nrb) if x > 0])/len([x for x in list(y_test_nrb) if x > 0])
                except ZeroDivisionError:
                    rank = -1
                try:
                    miss = len([x for x in list(y_test_nrb - y_pred_nrb) if x < 0])/len([x for x in list(y_test_nrb) if x > 0])
                except ZeroDivisionError:
                    miss = -1
                    
                disp = plot_precision_recall_curve(clf, X_test, y_test)
                average_precision = average_precision_score(y_test, y_pred)
                disp.ax_.set_title('2-class Precision-Recall curve: '
                           'AP={0:0.2f}'.format(average_precision))
                print("Saving fig...")
                plt.savefig(f"{training_file}-recall-{average_precision:.2f}-{rank:.4f}-{miss:.3f}.png")
                fig = plt.figure(fig_index, figsize=(10, 10))
                ax1 = plt.subplot2grid((3, 1), (0, 0), rowspan=2)
                ax2 = plt.subplot2grid((3, 1), (2, 0))

                ax1.plot([0, 1], [0, 1], "k:", label="Perfectly calibrated")
                prob_pos = clf.predict_proba(X_test)[:, 1]
                clf_score = brier_score_loss(y_test, prob_pos, pos_label=max(y))
                fraction_of_positives, mean_predicted_value = \
                    calibration_curve(y_test, prob_pos, n_bins=10)

                ax1.plot(mean_predicted_value, fraction_of_positives, "s-",
                     label="%s (%1.3f)" % (name, clf_score))

                ax2.hist(prob_pos, range=(0, 1), bins=10, label=name,
                     histtype="step", lw=2)

                ax1.set_ylabel("Fraction of positives")
                ax1.set_ylim([-0.05, 1.05])
                ax1.legend(loc="lower right")
                ax1.set_title('Calibration plots  (reliability curve)')

                ax2.set_xlabel("Mean predicted value")
                ax2.set_ylabel("Count")
                ax2.legend(loc="upper center", ncol=2)

                plt.tight_layout()
                print("Saving fig...")
                plt.savefig(f"{training_file}-calib.png")

            elif (modelType=='SVC'):
                clf = SVC(probability=True, class_weight='balanced' if self.isBalanced else None)
                self.model = clf.fit(X_std, y)
                #print self.model.predict_proba(X_test)
                self.is_classifier = True
            elif (modelType=='SVR'):
                clf = SVR()
                self.model = clf.fit(X_std, y)
                #print self.model.predict_proba(X_test)
            elif (modelType=='NBB'):
                # Create decision tree classifer object
                clf= None
                if (not self.isBalanced):
                    clf = BernoulliNB()
                else:
                    clf= make_pipeline(scaler, BernoulliNB())
                self.model = clf.fit(X_std, y)
                self.is_classifier = True
            elif (modelType=='NBG'):
                # Create decision tree classifer object
                clf = GaussianNB()
                self.model = clf.fit(X_std, y)
                self.is_classifier = True
            elif (modelType=='DT'):
                clf = tree.DecisionTreeClassifier(class_weight='balanced' if self.isBalanced else None)
                self.model = clf.fit(X_std, y)
                self.is_classifier = True
            elif (modelType=='DT_RG'):
                clf = tree.DecisionTreeRegressor()
                self.model = clf.fit(X_std, y)
            elif (modelType == "KNN"):
                clf = KNeighborsClassifier(n_neighbors=1)
                self.model = clf.fit(X_std, y)
                self.is_classifier = True
            elif (modelType == "KNN_R"):
                clf = KNeighborsRegressor(n_neighbors=1)
                self.model = clf.fit(X_std, y)
            elif (modelType=='DTGD_RG'):
                clf = GridSearchCV(tree.DecisionTreeRegressor(random_state=0),
                                    param_grid={'min_samples_split': range(2, 10)}, 
                                    scoring=make_scorer(r2_score), 
                                    cv=5, 
                                    refit=True)
                self.model = clf.fit(X_std, y)
            elif (modelType == 'RF_RG'):
                clf = RandomForestRegressor()
                self.model  = clf.fit(X_std, y)
            elif (modelType == 'RFGD_RG'):
                param_grid = { 
                "n_estimators"      : [10,20,30],
                "max_features"      : ["auto", "sqrt", "log2"],
                "min_samples_split" : [2,4,8],
                "bootstrap": [True, False],
                }
                clf = GridSearchCV(RandomForestRegressor(), param_grid, n_jobs=njobs, cv=5)
                self.model = clf.fit(X_std, y)
            elif (modelType=='SVRGD'):
                classifier_pipeline=None
                #tuned_parameters = [{'kernel': ['rbf'], 'gamma': [1e-3, 1e-4],
                #     'C': [1, 10, 100, 1000]},
                #    {'kernel': ['linear'], 'C': [1, 10, 100, 1000]}]
                params={'kernel':['linear', 'rbf', 'poly', 'sigmoid'],
                    'C':[1, 5, 10],
                    'degree':[2,3],
                    'gamma':[0.025, 1.0, 1.25, 1.5, 1.75, 2.0],
                    'coef0':[2, 5, 9],
                    }
                
                clf = GridSearchCV(SVR(), params, cv=3,
                       scoring='roc_auc',n_jobs=njobs)
                self.model =clf.fit(X_std , y)
                #print self.model.predict_proba(self.X_test)
            elif (modelType=='KRNCV_RG'):
                classifier_pipeline=None
                #tuned_parameters = [{'kernel': ['rbf'], 'gamma': [1e-3, 1e-4],
                #     'C': [1, 10, 100, 1000]},
                #    {'kernel': ['linear'], 'C': [1, 10, 100, 1000]}]
                params={'kernel':['linear', 'rbf', 'poly', 'sigmoid'],
                    #'C':[1, 5, 10],
                    'degree':[2,3],
                    'gamma':[0.025, 1.0, 1.25, 1.5, 1.75, 2.0],
                    'coef0':[2, 5, 9],
                    }
                
                clf = GridSearchCV(KernelRidge(), param_grid=params, 
                       cv=3,
                       scoring='roc_auc')
                self.model =clf.fit(X_std , y)
                #print self.model.predict_proba(self.X_test)
            elif (modelType=='KRN_RG'):
                clf = KernelRidge()     
                self.model =clf.fit(X_std , y)
                #print self.model.predict_proba(self.X_test) 
            elif (modelType=='AUTO'):
                automl = autosklearn.classification.AutoSklearnClassifier(
                    time_left_for_this_task=500,
                    per_run_time_limit=160,
                    #time_left_for_this_task=60,
                    #per_run_time_limit=30,
                    tmp_folder='/tmp/autosklearn_regression_tmp_'+training_file.replace("/", "")+str(os.getpid()),
                    output_folder='./autosklearn_regression_out_'+training_file.replace("/","")+str(os.getpid()),
                    memory_limit=30720,
                    #metric=autosklearn.metrics.accuracy
                    #metric=autosklearn.metrics.f1
                    metric=autosklearn.metrics.average_precision
                )
                self.model = automl.fit(X_std, y, dataset_name='hyperc')
                self.is_classifier = True
                predictions = automl.predict(X_test)
                # print(X_test, y_test, predictions)

                print("Accuracy score {:g} using {:s}".
                    format(sklearn.metrics.accuracy_score(y_test, list(predictions)),
                            automl.automl_._metric.name))
            else:
                SyntaxError("Error in modelType = 'LRCV', 'LG', 'RF', 'SVM', 'SVMCV', 'NBB', 'NBG' , 'DT'; \nLogistic Regression, Logistic Regression with Cross Validation, \nRandom Forest or Support Vector Machine with CV, \n DT  is decision Tree ")
        else:
            SystemError("fileTrain should not be empty.")  

    def returnProbClasesList(self, X_t):
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
        y_pred= self.model.predict_proba(X_test)
        y_predClass= self.model.predict(X_test)
        print(classification_report(list(y_test), y_predClass))
        print(confusion_matrix(y_test, y_predClass))
        
        if self.modelType.startswith('LR'):
            print("Coefficin matrix")
            print(self.model.coef_)
        elif (self.modelType.startswith('RF') or self.modelType.startswith('DT')):
            print(self.model.feature_importances_)

    def saveToDisk(self, fileI):
        pickle.dump(self, open(fileI, 'wb'))
#        pickle.dump(self.model, open(file+CLASS_SUFIX, 'wb'))

    @staticmethod
    def getModelFromDisk(fileModel):
        '''
           parameter 'fileModel' previously created and saved to disk, o 
        '''
        return pickle.load(open(fileModel, 'rb')) 

def main():
    strUsage= "Mode 1: python learn.py <MODELTYPE> <FILETRAIN> <FILESAVE> -> train a <MODELTYPE> model from <FILENAME> and  save to <FILESAVE>\n"
    strUsage +="[MODELTYPE]-> train or load a model, with MODELTYPE= LRCV or  LR or RF \n Where LR = Logistic Reg\n LRCV = Log. Reg with CrossValidation\n RF = Random Fores\n Default value MODELTYPE = LRCV\nSVM = Support Vector Machine (SVC)\nSVMCV = Support Vector Machine with CV grid search\nNBB=Naive Bayes classifier with Bernoulli estimator\nNBG=Naive Bayes classifier with Gaussian estimator\n DT  is decision Tree "
    strUsage +="Mode 2: python learn.py  <FILEMODEL> <FILETEST> -> returns the probabilities in SDOUT one 'line prob class 0', 'proba class 1'\n"
 
    if len(sys.argv) == 1:
        print(strUsage)
        tl = randBinList(94)
#        print tl
#        files = open("testfile.txt","w")  
#        files.write((",".join(''.join(str    (e) for e in tl)))+"\n") 
        
    elif len(sys.argv) == 3:
        fileLoadIn= sys.argv[1]
        fileTest=sys.argv[2]
        #lernModel=LearnRules(fileModel=fileLoadIn)
        lernModel=LearnRules.getModelFromDisk(fileLoadIn)
        Xtest= pd.read_csv(fileTest, header=None)

        y_pred= lernModel.returnProbClasesList(Xtest)
        #print y_pred
        #str_scv=''
   
        for line in y_pred:
            print(str(line[0])+","+str(line[1]))

         
        lernModel.printStats()
        print(lernModel.returnProbClasesList(lernModel.X_test))
        
    elif len(sys.argv) <=5 :
        fileIn= sys.argv[2]
        modType = sys.argv[1]      
        
        if len(sys.argv)==4:
            lernModel=LearnRules(training_file=fileIn, modelType=modType, njobs=4)
            lernModel.saveToDisk(sys.argv[3])
        elif(len(sys.argv)==5):
            balanced = sys.argv[4]
            lernModel=LearnRules(training_file=fileIn, modelType=modType, njobs=4,isBalanced=balanced=='balanced')
            lernModel.saveToDisk(sys.argv[3])
    
    else:
        print(strUsage)
        SystemExit("Bad Parameters\n"+strUsage)
            

if __name__ == "__main__":
    main()
