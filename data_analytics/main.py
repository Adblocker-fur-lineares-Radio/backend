import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


ads = pd.read_csv("data/adtime.csv", delimiter=";")
ads['date'] = pd.to_datetime(ads['date'], format='%m/%d/%Y %H:%M:%S')
ads['minute'] = ads['date'].dt.minute

stations = ads['stationName'].unique().tolist()
# stations.sort()

print(stations)

df = pd.DataFrame()
for station in stations:
    df[station] = (ads.loc[ads.stationName == station, 'minute']
                   .reset_index(drop=True))

print(df)

# fig, axs = plt.subplots(nrows=len(stations), ncols=1, sharex=True)
#
# for i, station in enumerate(stations):
#     axs[i].hist(df[station])
#     axs[i].set_title(station)
#
# plt.tight_layout()
# plt.show()

for station in stations:
    data = np.histogram(df[station].to_numpy())
    plt.plot(data, label=station)

plt.show()
