# -*- coding: utf-8 -*-
"""Feature Engineering.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1w_XjVyWjbCW4O8MCp_eissOiipKW16mL
"""

from google.colab import drive
import pandas as pd
import numpy as np

drive.mount('/content/drive')

"""### Time-related

action = pd.read_csv('/content/drive/MyDrive/Research/Programming/2022/action_log.csv',delimiter=';')
affect = pd.read_csv('/content/drive/MyDrive/Research/Programming/2022/affect.csv',delimiter=';')
submission = pd.read_csv('/content/drive/MyDrive/Research/Programming/2022/submission.csv',delimiter=';')
user = pd.read_csv('/content/drive/MyDrive/Research/Programming/2022/user.csv',delimiter=';')
user['pre_test'] = pd.to_numeric(user['pre_test'].str.replace(',', ''))
user['mid_test'] = pd.to_numeric(user['mid_test'].str.replace(',', ''))
"""

df = pd.read_csv('/content/drive/MyDrive/Research/Programming/2022/action_log.csv',delimiter=';')

# convert action_date column to datetime format
df['action_date'] = pd.to_datetime(df['action_date'])


df['time_of_day'] = pd.cut(df['action_date'].dt.hour,
                           bins=[6, 12, 18, 24],
                           labels=['Morning', 'Afternoon', 'Evening'],
                           include_lowest=False,
                           ordered=False)


# generate Extreme Time of Day feature
df['extreme_time_of_day'] = pd.cut(df['action_date'].dt.hour,
                                   bins=[0, 4, 8, 21, 24],
                                   labels=['late_night', 'early_morning', 'non_extreme_hours', 'late_night'],
                                   ordered=False)

# generate Day of Week feature
df['day_of_week'] = df['action_date'].dt.day_name()
df['day_of_week'] = df['day_of_week'].apply(lambda x: 'Weekend' if x in ['Saturday', 'Sunday'] else 'Weekday')

# Create dummy variables
time_of_day_dummies = pd.get_dummies(df['time_of_day'], prefix='time_of_day')
extreme_time_of_day_dummies = pd.get_dummies(df['extreme_time_of_day'], prefix='extreme_time_of_day')
day_of_week_dummies = pd.get_dummies(df['day_of_week'], prefix='day_of_week')

# concatenate dummy variables with original dataframe
df = pd.concat([df, time_of_day_dummies, extreme_time_of_day_dummies, day_of_week_dummies], axis=1)

"""## Percentage Correctness"""

df = pd.read_csv('/content/drive/MyDrive/Research/Programming/2022/action_log.csv',delimiter=';')

df

# Create new columns for the desired features
df["last_3_attempts_incorrect"] = df.groupby("user_id")["test_succeeded"].rolling(3).sum().reset_index(level=0, drop=True)
df["last_5_attempts_incorrect"] = df.groupby("user_id")["test_succeeded"].rolling(5).sum().reset_index(level=0, drop=True)
df["last_8_attempts_incorrect"] = df.groupby("user_id")["test_succeeded"].rolling(8).sum().reset_index(level=0, drop=True)
df["last_3_attempts_correct"] = df.groupby("user_id")["test_succeeded"].rolling(3).apply(lambda x: x[::-1].cumsum()[::-1][0], raw=True).reset_index(level=0, drop=True)
df["last_5_attempts_correct"] = df.groupby("user_id")["test_succeeded"].rolling(5).apply(lambda x: x[::-1].cumsum()[::-1][0], raw=True).reset_index(level=0, drop=True)
df["last_8_attempts_correct"] = df.groupby("user_id")["test_succeeded"].rolling(8).apply(lambda x: x[::-1].cumsum()[::-1][0], raw=True).reset_index(level=0, drop=True)

# Replace NaN values with 0
df.fillna(0, inplace=True)

df

"""## Attempt Count"""

# create new columns for the features
df['cumulative_correct'] = 0
df['cumulative_incorrect'] = 0

# initialize variables to keep track of correct and incorrect answers
correct_count = 0
incorrect_count = 0
current_task_id = None

# loop through the rows of the DataFrame
for i, row in df.iterrows():
    # if the user_id changed, reset the counts
    if row['user_id'] != current_task_id:
        correct_count = 0
        incorrect_count = 0
        current_task_id = row['user_id']
    
    # update the counts based on the test_succeeded
    if row['test_succeeded'] == 1:
        correct_count += 1
    else:
        incorrect_count += 1
    
    # update the new columns in the DataFrame
    df.at[i, 'cumulative_correct'] = correct_count
    df.at[i, 'cumulative_incorrect'] = incorrect_count

df