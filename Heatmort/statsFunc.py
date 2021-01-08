## Statistics
import statsmodels.formula.api as smf
import statsmodels.api as sm
import numpy as np
from sklearn.model_selection import StratifiedKFold, KFold
import pandas as pd

def meanNormRMSE(predictions, targets):
    return (np.sqrt((predictions-targets) **2).mean())/targets.mean()


def crossValidateKfoldFormula(X,y,number_of_coefs,formula,folds,stratified):
    """
    This function creates K-fold stratified samples and runs an OLS
    regression on it.
    Returns cross validated coefficients, adj R^2 and RMSE.
    """

    X=np.array(X) # Initialize X array
    y=np.array(y) # Initialize y array

    if stratified == 'Yes':
        skf = StratifiedKFold(n_splits=folds) # initalize the stratification
        split=skf.split(X,y) # Stratified split based on X,y
    else:
        skf=KFold(n_splits=folds)
        split=skf.split(X) # Split data based on X
    
    # Initialize new arrays to store coefficients, adjR2 and NRMSE.
    mean_norm_rmse=np.zeros([folds,1])
    adj_r_sq=np.zeros([folds,1])
    coefficients=np.zeros([folds,number_of_coefs+1])

    for index, [train_index,test_index] in enumerate(split):
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]    

        #model = sm.OLS(y_train, X_train).fit()
        train_data = pd.DataFrame({"y":y_train, "x":X_train})
        test_data = pd.DataFrame({"y":y_test, "x":X_test})
        model = smf.ols(formula = formula, data = train_data).fit()

        coefficients[index,:]=model.params
        adj_r_sq[index]=model.rsquared_adj
        predictions=model.predict(test_data['x'])
        mean_norm_rmse[index]=meanNormRMSE(predictions,test_data['y'])

    cross_validated_coefficients=np.mean(coefficients,axis=0)
    cross_validated_adj_r_sq=adj_r_sq.mean()
    cross_validated_rmse=mean_norm_rmse.mean()
    return cross_validated_adj_r_sq,cross_validated_rmse#, coefficients, pvals, adj_r_sq

def multicol(data):
    corr = np.corrcoef(data, rowvar=0) 
    value, vector = np.linalg.eig(corr)
    return value, vector

def crossValidateKfold(X,y,number_of_coefs,reg_type,folds,stratified):
    """
    This function creates K-fold stratified samples and runs an OLS
    regression on it.
    Returns cross validated coefficients, adj R^2 and RMSE.
    """

    X=np.array(X) # Initialize X array
    y=np.array(y) # Initialize y array

    if reg_type=='second order':
        X=np.hstack((X,np.square(X)))

    X = sm.add_constant(X)
    
    if stratified == 'Yes':
        skf = StratifiedKFold(n_splits=folds) # initalize the stratification
        split=skf.split(X,y) # Stratified split based on X,y
    else:
        skf=KFold(n_splits=folds)
        split=skf.split(X) # Split data based on X
    
    # Initialize new arrays to store coefficients, adjR2 and NRMSE.
    mean_norm_rmse=np.zeros([folds,1])
    adj_r_sq=np.zeros([folds,1])
    coefficients=np.zeros([folds,number_of_coefs+1])

    for index, [train_index,test_index] in enumerate(split):
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]

        model = sm.OLS(y_train, X_train).fit()

        coefficients[index,:]=model.params
        adj_r_sq[index]=model.rsquared_adj
        predictions=model.predict(X_test)
        mean_norm_rmse[index]=meanNormRMSE(predictions,y_test)

    cross_validated_coefficients=np.mean(coefficients,axis=0)
    cross_validated_adj_r_sq=adj_r_sq.mean()
    cross_validated_rmse=mean_norm_rmse.mean()
    return cross_validated_adj_r_sq,cross_validated_rmse #, coefficients, pvals, adj_r_sq

def multicol(data):
    corr = np.corrcoef(data, rowvar=0) 
    value, vector = np.linalg.eig(corr)
    return value, vector