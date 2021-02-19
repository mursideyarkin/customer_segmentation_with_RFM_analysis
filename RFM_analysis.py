###################################################
# PROJECT: CUSTOMER SEGMENTATION WITH RFM ANALYSIS
####################################################

# 1. IMPORTING LIBRARIES AND DATA SET:

import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)

df = pd.read_excel("online_retail_II.xlsx", sheet_name="Year 2010-2011")
df.head()

# 2. CHECKING DATAFRAME:

# observations and fetures:
print(df.shape)

# column data types:
print(df.dtypes)

# Number of NaN values per column:
print(df.isnull().sum())

# There are null observations in the dataset, especially in the Customer ID column.
# Since this analysis will be consumer-based, we need to remove these observations from the dataset.
# Therefore, we will eliminate these observations in the next step (data preprocessing).

# Basic descriptive statistics:
print(df.quantile([0, 0.05, 0.50, 0.95, 0.99, 1]).T)
# There are negative values in the Quantity and Price columns.These transactions are canceled orders.
# In the next step (data preprocessing), we'll eliminate these observations.

# 3. DATA PREPROCESSING:

# Data preparation step 1: Removing null oberservations
df.dropna(inplace=True)

# Data preparation step 1: Removing canceled orders
df = df[~df["Invoice"].str.contains("C", na=False)]
df = df[(df['Quantity'] > 0)]

# Checking dataframe:
df.describe([0.01,0.25,0.50,0.75,0.99]).T

# Look at 99% quantile of Quantity and Price columns and compare with the maximum values.
# We can say that there are some outliers. Let's find out these outliers and replace them with the highest limit.

# Defining functions for outliers
def outlier_thresholds(dataframe, variable):
    quartile1 = dataframe[variable].quantile(0.01)
    quartile3 = dataframe[variable].quantile(0.99)
    interquantile_range = quartile3 - quartile1
    up_limit = quartile3 + 1.5 * interquantile_range
    low_limit = quartile1 - 1.5 * interquantile_range
    return low_limit, up_limit

# Defining functions to replace outliers
def replace_with_thresholds(dataframe, variable):
    low_limit, up_limit = outlier_thresholds(dataframe, variable)
    # dataframe.loc[(dataframe[variable] < low_limit), variable] = low_limit
    dataframe.loc[(dataframe[variable] > up_limit), variable] = up_limit

# Data preparation step 2: Replacing outliers in the Quantity and Price columns with the upper limit
replace_with_thresholds(df, "Quantity")
replace_with_thresholds(df, "Price")
# Checking dataframe:
df.describe([0.01,0.25,0.50,0.75,0.99]).T

# Data preparation step 3: Calculating total price per transaction
df["TotalPrice"] = df["Quantity"] * df["Price"]

# Data preparation step 4: Defining today date as max(InvoiceDate) + 2 days
today_date = dt.datetime(2011, 12, 11)
print(f" Maximum invoice date: {df.InvoiceDate.max()} \n Today date: {today_date}")

# 4. CALCULATING THE RFM METRICS:

rfm = df.groupby("Customer ID").agg({"InvoiceDate": lambda date: (today_date - date.max()).days,
                                     "Invoice": lambda num: num.nunique(),
                                      "TotalPrice": lambda price: price.sum()}) #total price per customer

rfm.columns = ['Recency', 'Frequency', "Monetary"]
rfm.reset_index(inplace=True)
rfm.head()

# 4. CALCULATING THE RFM SCORES:

# Cutting RFM metrics into 5 groups and labeling them:
rfm["RecencyScore"] = pd.qcut(rfm["Recency"], 5, labels=[5, 4, 3, 2, 1])
rfm["FrequencyScore"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm["MonetaryScore"] = pd.qcut(rfm["Monetary"], 5, labels=[1, 2, 3, 4, 5])

# Concating scores and assign it to new column:
rfm["RFM_SCORE"] = (rfm['RecencyScore'].astype(str) +
                    rfm['FrequencyScore'].astype(str) +
                    rfm['MonetaryScore'].astype(str))

# 5. NAMING RFM SCORES and DEFINING CUSTOMER SEGMENT:

# Segment names:
seg_map = {
    r'[1-2][1-2]': 'Hibernating',
    r'[1-2][3-4]': 'At_Risk',
    r'[1-2]5': 'Cant_Loose',
    r'3[1-2]': 'About_to_Sleep',
    r'33': 'Need_Attention',
    r'[3-4][4-5]': 'Loyal_Customers',
    r'41': 'Promising',
    r'51': 'New_Customers',
    r'[4-5][2-3]': 'Potential_Loyalists',
    r'5[4-5]': 'Champions'}

# Segment assigning:
rfm['Segment'] = rfm['RecencyScore'].astype(str) + rfm['FrequencyScore'].astype(str)
rfm['Segment'] = rfm['Segment'].replace(seg_map, regex=True)

# Finding customer segment:

Customer_ID = 12347.0
rfm[rfm["Customer ID"] == Customer_ID]["Segment"]