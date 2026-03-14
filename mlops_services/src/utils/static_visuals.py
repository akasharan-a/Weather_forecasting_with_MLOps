import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

###Settings
seaborn_style = "darkgrid"
background = "dark_background"
title_color = 'white'
###


sns.set_style(seaborn_style)
plt.style.use(background) 

# Example time series data

def line_chart(data , x:str ,y:list,xlabel=None, ylabel=None, title=None):
    fig, ax = plt.subplots()
    for yi in y:
        sns.lineplot(x= x, y=yi, data=data, ax=ax, label= yi)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title,color= title_color)
    ax.legend()

    fig.xticks(rotation=45)
    fig.tight_layout()
    return fig