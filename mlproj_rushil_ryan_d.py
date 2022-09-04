# -*- coding: utf-8 -*-
"""mlproj-rushil-ryan-d.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1IW-OXahYjKoSK7ZzKWGCo7Zctd5LbWtC
"""

import pandas as pd

import numpy as np
from sklearn import linear_model # Linear Regression
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error # Will use later
from datetime import date
from statsmodels.tsa.ar_model import AutoReg # Time Series/Autoregression

# 
def get_essential_data(data_set=pd.read_csv('https://econdata.s3-us-west-2.amazonaws.com/Reports/Core/RDC_Inventory_Core_Metrics_County_History.csv')):
    '''Calls and access the rows of data commonly used throughout the program'''
    date = data_set['month_date_yyyymm']
    median_price_sqft = data_set['median_listing_price_per_square_foot']
    median_price = data_set['median_listing_price']
    return (date, median_price_sqft, median_price)
 
def translate_time(yyyymm):
    '''Translate the time in the csv file or inputted by the user into a usable format'''
    year_string = str(yyyymm)
    year = year_string[:4]
    y = float(year)
    month = year_string[4:] 
    m = float(month) / 12
    float_year = y + m
    return float_year

# Does an 80/20 Train/Test split on the data needed
def train_and_test(data_set, location, type_location, proportion=0.2):
    training = []; testing = []
    X_train = []; Y_train = []; Z_train = []; X_test = []; Y_test = []; Z_test = []
    (date, median_price_sqft, median_price) = get_essential_data(data_set)
    data_needed = get_location_data(data_set, location.lower(), type_location)
    testing = data_needed[:int(len(data_needed) * proportion)].copy()
    training = data_needed[int(len(data_needed) * proportion):].copy()
    for train_point in training:
        X_train.append(train_point[0])
        Y_train.append(train_point[1])
        Z_train.append(train_point[2])
    for test_point in testing:
        X_test.append(test_point[0])
        Y_test.append(test_point[1])
        Z_test.append(test_point[2])
    # Below Commented Out Statement used to test the accuracy of the Linear Model
    # for test in testing:
    #     predicted = predict_cost_LinReg(location, test[0], X_train, Y_train)
    #     predicted_AR = predict_cost_AR(location, test[0], X_train, Y_train, Z_train)
    #     actual = test[1]
        # print("Year: ", test[0], "\nExpected Value LinReg: ", predicted, "\nExpected Value AR: ", predicted_AR, "\nActual Value:", test[1])
    return (X_train, Y_train, Z_train)
        
# Obtains the data of a specific location based on the type of location chosen and the location name
def get_location_data(data_set, location_input, type_location):
    locations = data_set['county_name']
    (date, median_price_sqft, median_price) = get_essential_data()
    states_dict = {'alabama': 'al', 'alaska': 'ak', 'arizona': 'az', 'arkansas': 'ar', 'california': 'ca', 'connecticut': 'ct', 'delaware': 'de', 'district of columbia': 'dc', 'florida': 'fl', 'georgia': 'ga', 'hawaii': 'hi', 'idaho': 'id', 'illinois': 'il', 'indiana': 'in', 'ia': 'iowa', 'ks': 'kansas', 'ky': 'kentucky', 'louisiana': 'la', 'maine': 'me', 'maryland': 'md', 'massachusetts': 'ma', 'michigan': 'mi', 'minnesota': 'mn', 'mississippi': 'ms', 'missouri': 'mo', 'montana': 'mt', 'nebraska': 'ne', 'nevada': 'nv', 'new hampshire': 'nh', 'new jersey': 'nj', 'new mexico':'nm', 'new york': 'ny', 'north carolina': 'nc', 'north dakota': 'nd', 'ohio': 'oh', 'oklahoma': 'ok', 'oregon': 'or', 'pennsylvania': 'pa', 'rhode island': 'ri', 'south carolina': 'sc', 'south dakota': 'sd', 'tennessee': 'tn', 'texas': 'tx', 'utah': 'ut', 'vermont': 'vt', 'virginia': 'va', 'washington': 'wa', 'west virginia': 'wv', 'wisconsin': 'wi', 'wyoming': 'wy'}
    counter = 0
    if type_location == 'state':
        states_data = []
        for state_str in locations:
            state_str = str(state_str)
            state = state_str[-2:]
            if states_dict[location_input] == state:
                states_data.append([translate_time(date[counter]), median_price[counter], median_price_sqft[counter]])
            counter += 1
        return states_data
    else:
        county_data = []
        for i in range(len(data_set)):
            if locations[i] == location_input:
                county_data.append([translate_time(date[counter]), median_price[counter], median_price_sqft[counter]])
            counter += 1
        return county_data

# Prediction Functions 
        
# Linear Regression
def predict_cost_LinReg(location, year, x, y):
    X_trained = np.array(x).reshape(-1, 1); Y_trained = np.array(y).reshape(-1, 1)
    '''Using linear regression, predicts the future price of a home in a specified location'''
    regressor = LinearRegression()
    regressor.fit(X_trained, Y_trained)
    future_median = regressor.predict([[year]])
    return future_median

# Autoregression
def predict_cost_AR(data, year, x, y, z):
    current_year= float(date.today().year)
    current_month = float((date.today().month) / 12)
    current = current_year + current_month
    lead = int(year - current)
    lead *= 12
    test_removed = int(len(y) * .2)
    y.reverse()
    # print(y)
    # print(str(len(y) + test_removed + lead) + " months ahead of now")
    '''Using a time series analysis called autoregression, predicts the future price of a home using a certain amount of lags, or previous data points'''
    AR_model = AutoReg(y, lags=1)
    AR_model_fitted = AR_model.fit()
    prediction = AR_model_fitted.predict(start=len(y), end=(len(y) + test_removed +  lead), dynamic=False)
    # print(prediction[-1])
    '''link: https://pythondata.com/forecasting-time-series-autoregression/; does something called autoregression'''
    return prediction[-1]
# # Lasso Regressions
# def predict_cost_Lasso(location, year, x, y, z):
#     '''Using Lasso regression, predicts the future price of a home using a time and median listing price per square foot feature; performs a linear regression to gather the median listing price per square foot that corresponds with the median listing price overall'''
#     sqft_prediction = LinearRegression()
#     sqft_prediction_fitted = sqft_prediction.fit(x, z)
#     sqft_prediction_fitted = sqft_prediction.predict([[year]])
    
#     lasso_model = linear_model.Lasso(alpha=1)
#     lasso_model_fitted = lasso_model.fit(x, y, z)
#     prediction = lasso_model_fitted.predict([[year, sqft_prediction_fitted]])
#     return prediction
    
# General Function to run the program via the Console
if __name__ == "__main__":
    data = pd.read_csv('https://econdata.s3-us-west-2.amazonaws.com/Reports/Core/RDC_Inventory_Core_Metrics_County_History.csv', usecols=['month_date_yyyymm', 'county_name','median_listing_price', 'median_listing_price_per_square_foot'])
    running = True
    print("---Predict a House's Cost in the Future!---\n")
    while running:
        type_location = input("Would you like to predict a certain county or an entire state? Enter either 'county' or 'state' to specify your query: ")
        if type_location == 'state':
            location = input("Enter the full name of the state you wish to look at: ")
        elif type_location == 'county':
            location = input("Specify the county, along with the two letter state abbreviation: ") 
        else:
            print("Not a valid input, try again.")
            continue
        (X_data, Y_data, Z_data) = train_and_test(data, location, type_location)
        time = input("Enter the year you wish to look at, or the year and the month in the format YYYYMM (must be in the future): ")
        if len(time) == 6:
            time = translate_time(time)
        print("Cost based on Linear Regression:", predict_cost_LinReg(location, float(time), X_data, Y_data))
        print("Cost based on Autoregression (time series analysis):", predict_cost_AR(location, float(time), X_data, Y_data, Z_data))
        retry = input("Query another location/date? (Y/N): ", )
        if retry.lower() == "y":
            continue
        elif retry.lower() != "n":
            print("Not a valid input. Please try again.")
        else:
            running = False
  
print("\nThanks for using our program! Goodbye!")
