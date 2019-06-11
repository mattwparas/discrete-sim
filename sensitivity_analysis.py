# import libraries
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
# %matplotlib inline

# set font
# plt.rcParams['font.family'] = 'sans-serif'
# plt.rcParams['font.sans-serif'] = 'Helvetica'

# set the style of the axes and the text color
plt.rcParams['axes.edgecolor']='#333F4B'
plt.rcParams['axes.linewidth']=0.8
plt.rcParams['xtick.color']='#333F4B'
plt.rcParams['ytick.color']='#333F4B'
plt.rcParams['text.color']='#333F4B'

# create some fake data
percentages = pd.Series([20, 15, 18, 8, 6, 7, 10, 2, 10, 4], 
                        index=['Rent', 'Transportation', 'Bills', 'Food', 
                               'Travel', 'Entertainment', 'Health', 'Other', 'Clothes', 'Phone'])



index1 = [ 'Average Ischemic Stroke Treatment Time',
'Average Hemorrhagic Stroke Treatment Time',
'Average Non-Stroke Treatment Time',
'Arrival Rate of Stroke Patients to PSC',
'Arrival Rate of Non-Stroke Patients from PSCs to CSC ICU',
'Arrival Rate of Stroke Patients to CSC (not from PSC)',
'Arrival Rate of Non-Stroke Patients to CSC (not from PSC)']


small = [
2.605,
0.515,
8.855,
2.015,
10.715,
13.715,
10.715]

medium = [
2.848,
0.538,
8.088,
1.208,
7.188,
9.598,
7.188]

large = [
3.202,
0.592,
6.972,
0.962,
5.822,
7.932,
5.822,
]

# create some fake data
percentages = pd.Series(large, 
                        index=index1)


df = pd.DataFrame({'percentage' : percentages})
df = df.sort_values(by='percentage')

# we first need a numeric placeholder for the y axis
my_range=list(range(1,len(df.index)+1))

fig, ax = plt.subplots(figsize=(5,3.5))

# create for each expense type an horizontal line that starts at x = 0 with the length 
# represented by the specific expense percentage value.
plt.hlines(y=my_range, xmin=0, xmax=df['percentage'], color='#007ACC', alpha=0.2, linewidth=5)

# create for each expense type a dot at the level of the expense percentage value
plt.plot(df['percentage'], my_range, "o", markersize=5, color='#007ACC', alpha=0.6)

# set labels
ax.set_xlabel('Percentage Point Increase', fontsize=15, fontweight='black', color = '#333F4B')
ax.set_ylabel('')

# set axis
ax.tick_params(axis='both', which='major', labelsize=12)
plt.yticks(my_range, df.index)

# add an horizonal label for the y axis 
fig.text(-0.23, 0.96, 'Sensitivity Summary', fontsize=15, fontweight='black', color = '#333F4B')

# change the style of the axis spines
ax.spines['top'].set_color('none')
ax.spines['right'].set_color('none')
ax.spines['left'].set_smart_bounds(True)
ax.spines['bottom'].set_smart_bounds(True)

# set the spines position
ax.spines['bottom'].set_position(('axes', -0.04))
ax.spines['left'].set_position(('axes', 0.015))

plt.savefig('large_sensitivity.png', dpi=1000, bbox_inches='tight')