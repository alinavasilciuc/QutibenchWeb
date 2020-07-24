import pandas as pd
import re

#hide
def get_pareto_df(df, groupcol, xcol, ycol):
    pareto_line_df = df.groupby(groupcol)[xcol].max().to_frame("x")
    pareto_line_df['y'] = df.groupby(groupcol)[ycol].agg(lambda x: x.value_counts().index[0])
    pareto_line_df.sort_values('y', ascending=False, inplace=True)
    pareto_line_df['x'] = pareto_line_df.x.cummax()
    pareto_line_df.drop_duplicates('x', keep='first', inplace=True)
    pareto_line_df['group'] = pareto_line_df.index
    return pareto_line_df

def label_point(x, y, val, ax, rot=0):
    """ from https://stackoverflow.com/questions/46027653/adding-labels-in-x-y-scatter-plot-with-seaborn"""
    a = pd.concat({'x': x, 'y': y, 'val': val}, axis=1)
    for i, point in a.iterrows():
        ax.text(point['x']+.02, point['y'], str(point['val']), rotation=rot)


def dataframe_contains(input_df: pd.DataFrame, column: str, value: str)->pd.DataFrame:
    """
    Given a dataframe, this function returns a subset of that dataframe by column
    
    Parameters
    ----------
    input_df : pd.DataFrame
        Input dataframe from which the subset will be taken.       
    column : str
        Column name by which the subsetting will be taken.  
    value : str
        String that contains what we need from the column. 
        Eg.:'dog'
            'banana|apple|peach'

    Returns
    -------
    output_df:  pd.DataFrame
        This dataframe will be a subset from the input dataframe according to the column value given.  
        
    """
    output_df = input_df[input_df[column].str.contains(pat=value, case=False)]
    return output_df

#---------------------------------------------------------------------------------

def replace_data_df(df_: pd.DataFrame(), column:str, list_tuples_data_to_replace: list )-> pd.DataFrame():
    """Method to replace a substring inside a cell inside a dataframe
    Given a dataframe and a specific column, this method replaces a string for another, both from the list of tuples
       
    Parameters
    ----------
     df_: pd.DataFrame()
        Dataframe with data to be replaced.
    column: str
        Column whithin dataframe where all replacements will take place.
    list_tuples_data_to_replace: list
        List with tuples which will contain what to replace by what.
        Eg.:list_tuples_data_to_replace = [(a,b), (c,d), (...) ] -> 'a' will be replaced by 'b', 'c' will be replaced by 'd', and so on.

    Returns
    -------
    df_out: pd.DataFrame()
       Dataframe with all indicated values replaced.
        
    """
    df_out = df_.copy()
    for j, k in list_tuples_data_to_replace:
        df_out[column] = df_out[column].str.replace(j, k)
    return df_out
#-------------------------------------------------

def process_csv_for_heatmaps_plot(csv_file: str, machine_learning_task: str)->pd.DataFrame:
    """This method gets the csv for the theoretical predictions file and melts it to make it presentable in the heatmaps plot"""
    
    ## Reading csv file and converting data to (Neural network, Platform, Value)
    df = pd.read_csv(csv_file)

    df_out = pd.DataFrame()
    columns = (df.loc[:, df.columns!='hardw']).columns #select all columns except first
    for column in columns:
        df_=pd.melt(df, id_vars=['hardw'], value_vars=column) #melt df1 into a df1 of 2 columns
        df_out=pd.concat([df_out,df_])
    df_out.columns= ['y','x','values'] #setting new column names
    #replace 0s for NaN values because with 0s the grid doesn't show up
    df_out['values'] = df_out['values'].replace({ 0.0:np.nan})
   
     # Choose the neural networks corresponding to the Machine Learning task asked for.
    if re.search(machine_learning_task, 'imagenet', re.IGNORECASE):
        df_out = dataframe_contains(input_df= df_out, column='x', value='goog|mob|res|effic')

    elif re.search(machine_learning_task, 'mnist', re.IGNORECASE):
        df_out = dataframe_contains(input_df= df_out, column='x', value='mlp')

    elif re.search(machine_learning_task, 'cifar-10', re.IGNORECASE):
        df_out = dataframe_contains(input_df= df_out, column='x', value='cnv')
    
    else: 
        print('The machine learning task was not recognized, please try another one.') 
        return 0
    
    return df_out

#-------------------------------------------------