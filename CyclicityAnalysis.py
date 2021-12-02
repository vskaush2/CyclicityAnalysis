import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import itertools


def compute_oriented_area(df, col1, col2):
    vertices_array = df[[col1, col2]].values
    x, y = vertices_array[:, 0], vertices_array[:, -1]
    oriented_vertices_array = np.vstack([vertices_array, vertices_array[0]])
    oriented_area = 0.5 * np.dot(x + oriented_vertices_array[:, 0][1:], oriented_vertices_array[:, -1][1:] - y)
    return oriented_area

def get_accumulated_oriented_area_df(df, col1, col2):
    accumulated_oriented_area_df = pd.DataFrame(columns=['Accumulated Oriented Area'], index=df.index)
    df_diff = df[[col1, col2]].diff().dropna()
    try:
        first_oriented_area_change_time = df_diff[(df_diff[col1] != 0) & (df_diff[col2] != 0)].index[0]
        oriented_area_change_times = df_diff[(df_diff[col1] != 0) | (df_diff[col2] != 0)].loc[first_oriented_area_change_time:].index
        accumulated_oriented_area_df['Accumulated Oriented Area'].loc[oriented_area_change_times] = [compute_oriented_area(df.loc[:time], col1, col2)
                                                                                                 for time in oriented_area_change_times]
    # Accumulated Oriented Areas corresponding to timestamps t where either (x_t- x_{t-1}) is nonzero or (y_t- y_{t-1}) is nonzero.

        accumulated_oriented_area_df.fillna(method='ffill', inplace=True) # If the timestamp t has a null value, we set it equal to the latest available timestamp s before t having a non-null value.

        accumulated_oriented_area_df.fillna(0, inplace=True) # All remaining timestamps with null values are set equal to 0.
    except:
        accumulated_oriented_area_df.fillna(0, inplace=True)
        # If (x_t- x_{t-1}) is zero for all t or (y_t- y_{t-1}) is zero for all t, then accumulated oriented area is 0.
    return accumulated_oriented_area_df

def plot_oriented_polygon(df, col1, col2, figsize=(5,5)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_title("Joint Parametric Plot", size= 20)
    df.plot.scatter(col1, col2, ax=ax)

def plot_leader_follower_relationship(df, leader, follower, figsize=(20,10), include_accumulated_oriented_area_plot=True):
    if include_accumulated_oriented_area_plot:
        fig, axs = plt.subplots(2, figsize=figsize)
        axs[0].set_title("Leader Follower Plot",size=20)
        df[leader].plot(ax=axs[0], linewidth=4.0, color='green', label='Leader: {}'.format(leader))
        df[follower].plot(ax=axs[0], linewidth=4.0, color='red', linestyle='dashed', label='Follower: {}'.format(follower))
        axs[0].legend(prop={'size': 15}, loc='upper right')

        axs[-1].set_title("Accumulated Oriented Area Plot", size=20)
        accumulated_oriented_area_df=get_accumulated_oriented_area_df(df,leader,follower)
        accumulated_oriented_area_df.plot(ax=axs[-1], linewidth=4.0)
    else:
        fig, ax = plt.subplots(1, figsize=figsize)
        ax.set_title("Leader Follower Plot", size=20)
        df[leader].plot(ax=ax, linewidth=4.0, color='green', label='Leader: {}'.format(leader))
        df[follower].plot(ax=ax, linewidth=4.0, color='red', linestyle='dashed',
                          label='Follower: {}'.format(follower))
        ax.legend(prop={'size': 15}, loc='upper right')


def plot_df(df, title='Plot', figsize=(20,10), linewidth=4.0, use_cmap=False):
    fig,ax=plt.subplots(figsize=figsize)
    ax.set_title(title, size=20)
    if use_cmap:
        df.plot(ax=ax,linewidth=linewidth,cmap=plt.get_cmap('hsv'))
    else:
        df.plot(ax=ax, linewidth=linewidth)

    ax.legend(prop={'size': 15}, loc='upper right')

class CyclicityAnalysis:
    def __init__(self,df):
        self.df = df
        self.lead_lag_df = self.get_lead_lag_df()
        self.sorted_lead_lag_df, self.cyclic_order, self.sorted_eigvals, self.sorted_dominant_eigvec_components= self.get_cyclic_order()

    def get_lead_lag_df(self):
        unique_distinct_pairs = itertools.combinations(self.df.columns, r=2)
        lead_lag_df = pd.DataFrame(columns=self.df.columns, index=self.df.columns)
        for pair in unique_distinct_pairs:
            oriented_area = compute_oriented_area(self.df, pair[0], pair[-1])
            lead_lag_df.loc[pair[0], pair[-1]] = oriented_area
            lead_lag_df.loc[pair[-1], pair[0]] = - oriented_area
        lead_lag_df.fillna(0, inplace=True)
        return lead_lag_df

    def plot_lead_lag_df(self, color_label='Oriented Area', color_continuous_scale='Bluered'):
        fig = px.imshow(self.sorted_lead_lag_df,
                        labels = dict(color=color_label),
                        x= self.sorted_lead_lag_df.columns,
                        y =self.sorted_lead_lag_df.columns,
                        color_continuous_scale = color_continuous_scale)
        fig.update_xaxes(side='top')
        return fig

    def get_cyclic_order(self):
        N = len(self.lead_lag_df.columns)
        lead_lag_matrix = self.lead_lag_df.values
        spectra = np.linalg.eig(lead_lag_matrix)
        eigvals = spectra[0]  # Eigenvalues of Lead-Lag Matrix
        eigvecs = spectra[-1].T  # Eigenvectors of Lead-Lag Matrix
        spectra_dict = dict(zip(eigvals, eigvecs))
        sorted_eigvals = sorted(eigvals, key=lambda eigval: np.absolute(eigval), reverse=True)
        # Sorting Eigenvalues by Moduli in Descending Order

        largest_eigval = sorted_eigvals[0] # Largest Eigenvalue by Modulus
        dominant_eigvec = spectra_dict[largest_eigval] # Dominant Eigenvector Corresponding to the Largest Eigenvalue

        enumerate_dominant_eigvec_components_dict = dict(zip(dominant_eigvec, range(N))) # Enumerating Components of Dominant Eigenector

        sorted_dominant_eigvec_components = sorted(dominant_eigvec, key=lambda component: np.angle(component))
        # Sorting Components of Dominant Eigenvector by the Principal Argument in Ascending Order

        cyclic_order_indices = [enumerate_dominant_eigvec_components_dict[component] \
                                for component in sorted_dominant_eigvec_components]

        cyclic_order = [self.lead_lag_df.columns[index] for index in cyclic_order_indices]
        sorted_lead_lag_df = self.lead_lag_df[cyclic_order].T[cyclic_order].T # Resorting Lead-Lag Matrix by Cyclic Order
        return sorted_lead_lag_df, cyclic_order, sorted_eigvals, sorted_dominant_eigvec_components

    def plot_eigenvalue_moduli_and_sorted_dominant_eigenvector_components(self,figsize=(20,10)):
        fig, axs = plt.subplots(1, 2, figsize=figsize)
        moduli = [np.absolute(eigval) for eigval in self.sorted_eigvals]
        axs[0].set_title("Moduli of Lead Lag Matrix Eigenvalues Plot", size=20)
        axs[0].set_xlabel('Eigenvalue Index', size=10)
        axs[0].set_ylabel('Modulus', size=10)
        axs[0].plot(moduli, marker='o', color='red')

        axs[-1].set_title("Component Phase Diagram", size=20)
        axs[-1].set_xlabel('Re(z)', size=10)
        axs[-1].set_ylabel('Im(z)', size=10)
        axs[-1].scatter(np.real(self.sorted_dominant_eigvec_components), np.imag(self.sorted_dominant_eigvec_components), s=50)

        x_bound, y_bound =np.abs(np.max(np.real(self.sorted_dominant_eigvec_components))), \
                          np.abs(np.max(np.imag(self.sorted_dominant_eigvec_components)))
        # Largest of the real imaginary parts of eigenvector components in absolute value

        axs[-1].set_xlim(-x_bound,x_bound)
        axs[-1].set_ylim(-y_bound, y_bound)
        axs[-1].hlines(0, -1, 1, color='black')
        axs[-1].vlines(0, -1, 1, color='black')
        for i in range(len(self.sorted_dominant_eigvec_components)):
            component=(np.real(self.sorted_dominant_eigvec_components[i]), np.imag(self.sorted_dominant_eigvec_components[i]))
            axs[-1].annotate(i, component , size=20) # Cyclic Order Index Annotation


    def get_topN_leader_follower_pairs(self,N=10):
        all_pairs = itertools.product(self.lead_lag_df.columns, repeat=2)
        oriented_areas = self.lead_lag_df.values.flatten()
        oriented_areas_dict = dict(zip(all_pairs,oriented_areas))
        oriented_areas_dict = dict(sorted(oriented_areas_dict.items(),key=lambda x: x[-1],reverse=True))
        topN_leader_follower_pairs = list(oriented_areas_dict.keys())[:N]
        return topN_leader_follower_pairs















