# import seaborn as sns
# from pandas import concat
# import matplotlib.pyplot as plt


# def sns_boxplot(X, y, y_label: str = "target", show=True, ax=None):
#     df_sns = concat([X, y], axis=1).melt(id_vars=y_label)
#     if ax is None:
#         ax = sns.boxplot(df_sns, x="variable", y="value", hue=y_label)
#         plt.setp(ax.get_xticklabels(), rotation=90)
#     else:
#         sns.boxplot(df_sns, x="variable", y="value", hue=y_label, ax=ax)
#         plt.setp(ax.get_xticklabels(), rotation=90)
#     if show:
#         plt.show()
