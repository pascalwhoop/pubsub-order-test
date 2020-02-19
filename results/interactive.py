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

def list_to_counted_offsets(name, list) -> pd.DataFrame():
    """
    converts a raw list of offsets 
    """
    return (pd.Series(list, name="abs")
        .value_counts()
        .to_frame()
        .assign(total=len(list))
        .assign(perc=lambda df: df["abs"]/df["total"])
        .drop(["abs", "total"], axis=1)
        .rename(columns={"perc": name})
    )


#build a 
just_lists = {k.split(".")[0]: data[k] for k in data if "offs" in k}
counts_dfs = [list_to_counted_offsets(k, just_lists[k]) for k in just_lists]

counts_dfs[23]

# %%
# now we have the percentage of each offset "magnitude" for each experiment. 
# pandas allows joins on indexes (it's the default actually)
# so all I need to do is to use a reduce function to outer join all df's together on the indexes
from functools import reduce
distributions_df = reduce(lambda a, b: a.join(b, how="outer"), counts_dfs).fillna(0)
distributions_df


# %%
print("log axis on y")
for i in range(6):
    distributions_df.filter(regex=f":{i}").plot(logy=True, figsize=[12,12])

print("loglog axes, showing exponential values better")
for i in range(6):
    distributions_df.filter(regex=f":{i}").plot(loglog=True, figsize=[12,12])

# %% [markdown]
# The graphs shows how the data follows a long tail distribution when looking 
# at the highest rate of TX cases.


# %%

df = distributions_df.filter(regex=f":5").loc[range(20)]
df.plot.bar(figsize=[12,12], logy=True)
#ax = None
#for col in df.columns:
#    if ax is None:
#        ax = df.plot.scatter(x=col, y="index")
#    else:
#        df.plot.scatter(x=col, y="index", ax=ax)


# %%
df2 = distributions_df.filter(regex=f":2").loc[range(20)]
df2.plot.bar(figsize=[12,12], logy=True)