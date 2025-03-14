
import pandas as pd
import csv
import matplotlib.pyplot as plt

df = pd.read_csv('/home/gaia/Documents/MATLAB/SdF/frane_info_graph.csv', sep=';')

print(df.head())
print(df.columns)


plt.plot(df['ti'], df['m0'], marker='o', color='b')

plt.xlabel('ti')
plt.ylabel('m0')

plt.show()



plt.plot(df['lds'], df['m0'], marker='o', color='b')

plt.xlabel('lds')
plt.ylabel('m0')

plt.show()


plt.plot(df['ti'], df['amp0'], marker='o', color='b')

plt.xlabel('ti')
plt.ylabel('amp0')

plt.show()

plt.plot(df['lds'], df['amp0'], marker='o', color='b')

plt.xlabel('lds')
plt.ylabel('amp0')

plt.show()