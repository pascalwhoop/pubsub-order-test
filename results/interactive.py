# %% [markdown]

# ## Results analysis
# This is an interactive python file in VSCode. See [their support](https://code.visualstudio.com/docs/python/jupyter-support-py) for how this works
#
# Goal: Analyse the results from my experiments. More precisely, get a view on the lateness distribution of messages depending on the rate of transmission


# %%
import pandas as pd
import json
import matplotlib as plt

# %%
# get this with 
# curl https://quixotic-elf-256313.appspot.com/state > experiments.json 
with open("experiments.json") as f:
    data = json.load(f)

# %%
offset_keys = [k for k in data.keys() if k.startswith("L-")]
offset_keys

stages = list(range(0, 6))

for k in offset_keys:
    df = pd.DataFrame(data[k])
    # plt.figure()
    # df.plot.hist(bins=range(0,10))
    print(df[0].value_counts())

# %%
def counter_to_df(data, counter_name) -> pd.DataFrame:
    return pd.DataFrame.from_dict(
        {k.split(".")[0]: int(data[k]) for k in data if counter_name in k},
        columns=[counter_name],
        orient="index",
    )


# grab keys, crop type away then create indexed DF and give column a fitting name
ooo = counter_to_df(data, "ooo")
total = counter_to_df(data, "total")
max = counter_to_df(data, "max")
ooi = counter_to_df(data, "ooi")


# %%

# build a big df that contains all the sessions data
counter_big_df = (
    ooi.join(total, how="outer")
    .join(max, how="outer")
    .join(ooo, how="outer")
    .fillna(0)
    .astype("int64")
)
#   .assign(ooo_percentage = lambda df: round(df["ooo"] / df["total"] * 100, 2))\
#   .assign(ooi_percentage = lambda df: round(df["ooi"] / df["total"] * 100, 2))\

# %%

# sum the different sessions values to get more data to look at for the 6 different nth styles
# loop over stages
sums = []
for stage in range(0, 6):
    filter_substring = f":{stage}"
    indexes = [f for f in counter_big_df.index if filter_substring in f]

    sums.append(counter_big_df[counter_big_df.index.isin(indexes)].sum())

counter_sums_df = (
    pd.DataFrame(sums)
    .assign(ooo_percentage=lambda df: round(df["ooo"] / df["total"] * 100, 2))
    .assign(ooi_percentage=lambda df: round(df["ooi"] / df["total"] * 100, 2))
    .drop(["ooi", "total", "max", "ooo"], axis=1)
    .assign(message_interval_in_sec=pd.Series(["2s", "1s", "1/2s", "1/10s", "1/50s", "1/100s"]))
)
# counter_sums_df
# counter_sums_df.plot.bar()

# %%
counter_sums_df.plot.bar(x="message_interval_in_sec", y=["ooo_percentage", "ooi_percentage"])


# %% [markdown]

# okay so we now have a nice graph. What does it show? Well, out of index happens 
# rather quickly. But the OOO take precedence over OOI (the code only allows one or the other and OOO takes precedence).
# Hence, starting at 1/10s, OOO rises and therefore, OOI goes down (in fact, most messages are likely OOO and OOI)
# 
# But I want a distribution *how* late the messages come in.
# that way one can make intelligent decisions to day "waiting N messages captures 99% of all messages when given TX rate Y"

# ## Offset distributions calculation

# %%

def list_to_counted_offsets(key, list) -> pd.DataFrame():
        total = len(list)
        return (
            pd.DataFrame(list, columns=["off_count"])["off_count"]
            .value_counts()
            .to_frame()
            .assign(offset = lambda df: df.index)
            .assign(total_count=total)
            .assign(dataset=key)
        )


def lists_to_df(data, list_name) -> pd.DataFrame:
    just_lists = {k.split(".")[0]: data[k] for k in data if list_name in k}
    dataframes = [list_to_counted_offsets(k, just_lists[k]) for k in just_lists]
    return dataframes


    # return pd.DataFrame.from_dict(, columns=[list_name], orient="index")


offset_count_dfs = pd.concat(lists_to_df(data, "offs"))

# %%

datasets = pd.unique(offset_count_dfs["dataset"])
datasets

ax = None
for d in datasets[0:8]:
    if ax is None:
        ax = (offset_count_dfs
        .loc[offset_count_dfs["dataset"] == d]
        .plot
        .scatter(x='offset', y='off_count', colormap='Paired', label=d, loglog=True)
        )
    else:
        (offset_count_dfs
        .loc[offset_count_dfs["dataset"] == d]
        .plot
        .scatter(x='offset', y='off_count', label=d, ax=ax)
        )


#
#df.plot.scatter(x='c', y='d', color='DarkGreen', label='Group 2', ax=ax);
