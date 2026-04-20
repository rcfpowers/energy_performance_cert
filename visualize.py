import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

df = pd.read_csv('/home/onyxia/work/dpe_2021_2026.csv')
df = df.sort_values("date_etablissement_dpe").drop_duplicates(subset="numero_dpe", keep="last")
print(df.columns)

df["surface_total"] = np.where(
    df["type_batiment"].isin(["maison", "appartement"]),
    df["surface_habitable_logement"],
    0
    #df["surface_habitable_immeuble"]
)

df["date_etablissement_dpe"] = pd.to_datetime(df["date_etablissement_dpe"])

dpe_counts = df.groupby(["etiquette_dpe"]).size().reset_index(name="count")

print(df["etiquette_dpe"].unique())

colors = ["#008000", "#50C878", "#ADFF2F", "#FFFF00", "#FFA500", "#FF4500", "#FF0000"]

batiment_label = df.groupby(["type_batiment", "etiquette_dpe"]).size().reset_index(name="count")

bins = [0, 30, 80, 100, float("inf")]
labels = ["moins de 30m2", "entre 30 et 80m2", "entre 80 et 100m2", "plus de 100m2"]

mask = df["type_batiment"].isin(["maison", "appartement"])

df["surface_category"] = pd.cut(
    df.loc[mask, "surface_total"],
    bins=bins,
    labels=labels,
    right=False
)
surface_label = df.groupby(["surface_category", "etiquette_dpe"]).size().reset_index(name="count")
surface_label["surface_category"] = surface_label["surface_category"].astype(str)
surface_label = surface_label[surface_label["surface_category"] != "nan"]

# Group by month and etiquette_dpe
df["month"] = df["date_etablissement_dpe"].dt.to_period("M")
monthly_label = df.groupby(["month", "etiquette_dpe"]).size().unstack(fill_value=0)
monthly_label.index = monthly_label.index.to_timestamp()

dpe_map = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7}
df["etiquette_dpe_num"] = df["etiquette_dpe"].map(dpe_map)
month_batiment_label = df.groupby(["month", "type_batiment"])["etiquette_dpe_num"].mean().unstack(fill_value=0)


perc = monthly_label.div(monthly_label.sum(axis=1), axis=0) * 100
perc = perc[["A", "B", "C", "D", "E", "F", "G"]]

for label in perc.columns:
    min_val = perc[label].min()
    max_val = perc[label].max()
    min_month = perc[label].idxmin()
    max_month = perc[label].idxmax()
    print(f"{label} → min: {min_val:.1f}% ({min_month.strftime('%Y-%m')})  |  max: {max_val:.1f}% ({max_month.strftime('%Y-%m')})")

fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(dpe_counts["etiquette_dpe"], dpe_counts["count"], color=colors)

ax.set_title("DPE certificates by energy label")
ax.set_xlabel("Etiquette DPE")
ax.set_ylabel("Count")
plt.tight_layout()
plt.savefig("dpe_by_label.png", dpi=150)
plt.show()

batiments = df['type_batiment'].unique()

for bat in batiments:
    df_temp = batiment_label[batiment_label["type_batiment"] == bat]
    df_temp = df_temp.set_index("etiquette_dpe").fillna(0)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(df_temp.index, df_temp["count"], color=colors, width=0.8)

    ax.set_title(f"DPE certificates by energy label - {bat}")
    ax.set_xlabel("Etiquette DPE")
    ax.set_ylabel("Count")
    plt.tight_layout()
    plt.savefig(f"dpe_by_label_{bat}.png", dpi=150)  # unique filename per type
    plt.show()


monthly_surface = df[df["type_batiment"].isin(["maison", "appartement"])] \
    .groupby(["surface_category", "month", "etiquette_dpe"]) \
    .size().reset_index(name="count")

categories = df['surface_category'].unique()

for cat in categories:
    df_temp = surface_label[surface_label["surface_category"] == cat]
    df_temp = df_temp.set_index("etiquette_dpe")
    df_temp.index = df_temp.index.astype(str)  # drop categorical type
    df_temp = df_temp.fillna(0)
        
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(df_temp.index, df_temp["count"], color=colors, width=0.8)

    ax.set_title(f"DPE certificates by surface group - {cat}")
    ax.set_xlabel("Etiquette DPE")
    ax.set_ylabel("Count")
    plt.tight_layout()
    plt.savefig(f"dpe_by_surface_{cat}.png", dpi=150)  # unique filename per type
    plt.show()

for cat in monthly_surface["surface_category"].unique():
    df_temp = monthly_surface[monthly_surface["surface_category"] == cat]
    
    df_pivot = df_temp.pivot_table(
        index="month", 
        columns="etiquette_dpe", 
        values="count", 
        fill_value=0
    )[["A", "B", "C", "D", "E", "F", "G"]]  # enforce order

    fig, ax = plt.subplots(figsize=(16, 5))
    df_pivot.plot(kind="bar", stacked=True, ax=ax, color=colors, width=0.8)

    ax.set_title(f"DPE certificates issued per month by energy label - {cat}")
    ax.set_xlabel("Month")
    ax.set_ylabel("Count")
    ax.legend(title="Etiquette DPE", bbox_to_anchor=(1.01, 1), loc="upper left")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(f"dpe_monthly_by_label_{cat}.png", dpi=150)
    plt.show()

fig, ax = plt.subplots(figsize=(16, 5))
perc.plot(kind="bar", stacked=True, ax=ax, color=colors, width=0.8)

ax.set_title("DPE certificates issued per month by energy label as %")
ax.set_xlabel("Month")
ax.set_ylabel("Count")
ax.legend(title="Etiquette DPE", bbox_to_anchor=(1.01, 1), loc="upper left")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("dpe_monthly_by_label_%.png", dpi=150)
plt.show()

fig, ax = plt.subplots(figsize=(16, 5))
monthly_label.plot(kind="bar", stacked=True, ax=ax, color=colors, width=0.8)

ax.set_title("DPE certificates issued per month by energy label")
ax.set_xlabel("Month")
ax.set_ylabel("Count")
ax.legend(title="Etiquette DPE", bbox_to_anchor=(1.01, 1), loc="upper left")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("dpe_monthly_by_label.png", dpi=150)
plt.show()

fig, ax = plt.subplots(figsize=(16, 5))
month_batiment_label.plot(kind="line", ax=ax, color=colors)
ax.set_title("DPE certificates issued per month by energy label by batiment type")
ax.set_xlabel("Month")
ax.set_ylabel("Count")
ax.legend(title="Etiquette DPE", bbox_to_anchor=(1.01, 1), loc="upper left")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("dpe_batiment_monthly_by_label.png", dpi=150)
plt.show()

# Build total count per month and surface category
monthly_total = df[df["type_batiment"].isin(["maison", "appartement"])] \
    .groupby(["surface_category", "month"]) \
    .size().reset_index(name="count")

monthly_total["surface_category"] = monthly_total["surface_category"].astype(str)
monthly_total = monthly_total[monthly_total["surface_category"] != "nan"]

df_line = monthly_total.pivot_table(
    index="month",
    columns="surface_category",
    values="count",
    fill_value=0
)

fig, ax = plt.subplots(figsize=(16, 5))
df_line.plot(ax=ax, linewidth=2, marker="o", markersize=3)

ax.set_title("DPE certificates issued per month by surface category")
ax.set_xlabel("Month")
ax.set_ylabel("Count")
ax.legend(title="Surface category", bbox_to_anchor=(1.01, 1), loc="upper left")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("dpe_monthly_by_surface.png", dpi=150)
plt.show()

monthly_total = monthly_total[monthly_total["surface_category"] != "entre 30 et 80m2"]

df_line = monthly_total.pivot_table(
    index="month",
    columns="surface_category",
    values="count",
    fill_value=0
)

fig, ax = plt.subplots(figsize=(16, 5))
df_line.plot(ax=ax, linewidth=2, marker="o", markersize=3)

ax.set_title("DPE certificates issued per month by surface category")
ax.set_xlabel("Month")
ax.set_ylabel("Count")
ax.legend(title="Surface category", bbox_to_anchor=(1.01, 1), loc="upper left")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("dpe_monthly_by_surface_no_30_80.png", dpi=150)
plt.show()