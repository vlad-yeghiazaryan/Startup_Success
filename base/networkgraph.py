import networkx as nx
from matplotlib import pyplot as plt
import seaborn as sns


class NetworkGraph():
    def __init__(self, corr_matrix, threshold=0.5):
        self.corr_matrix = corr_matrix
        self.threshold = threshold
        self.network = self.create_network(corr_matrix)
        self.remove_network_edges()
        self.customize_network_view()

    @staticmethod
    def create_network(corr_matrix):
        # convert matrix to list of edges and rename the columns
        edges = corr_matrix.stack().reset_index()
        edges.columns = ['value_1', 'value_2', 'correlation']

        # remove self correlations
        edges = edges.loc[edges['value_1'] != edges['value_2']].copy()

        # create a new graph from edge list
        Gx = nx.from_pandas_edgelist(
            edges, 'value_1', 'value_2', edge_attr=['correlation'])
        return Gx

    def remove_network_edges(self):
        # list to store edges to remove
        remove = []
        # loop through edges in Gx and find correlations which are below the threshold
        for asset_1, asset_2 in self.network.edges():
            corr = self.network[asset_1][asset_2]['correlation']
            # add to remove node list if abs(corr) < threshold
            if abs(corr) < self.threshold:
                remove.append((asset_1, asset_2))
        self.network.remove_edges_from(remove)
        self.removed_edges = remove
        removed_nodes = list(nx.isolates(self.network))
        self.network.remove_nodes_from(removed_nodes)
        return remove

    def customize_network_view(self):
        # assign colours to edges depending on positive or negative correlation
        # assign edge thickness depending on magnitude of correlation
        self.edge_colours = []
        self.edge_width = []
        for key, value in nx.get_edge_attributes(self.network, 'correlation').items():
            self.edge_colours.append(self.assign_colour(value))
            self.edge_width.append(self.assign_thickness(value))

        # assign node size depending on number of connections (degree)
        self.node_size = []
        for key, value in dict(self.network.degree).items():
            self.node_size.append(self.assign_node_size(value))

    @staticmethod
    def assign_colour(correlation):
        if correlation <= 0:
            return "#ffa09b"  # red
        else:
            return "#9eccb7"  # green

    @staticmethod
    def assign_thickness(correlation, benchmark_thickness=2, scaling_factor=3):
        return benchmark_thickness * abs(correlation)**scaling_factor

    @staticmethod
    def assign_node_size(degree, scaling_factor=50):
        return degree * scaling_factor

    def assign_edge_colours(self, network):
        self.edge_colours = []
        # assign edge colours
        for key, value in nx.get_edge_attributes(network, 'correlation').items():
            self.edge_colours.append(self.assign_colour(value))
        return self.edge_colours

    def draw_network_graph(self, layout_type='circular_layout', figsize=(10, 10), with_labels=True,
                           title=None, title_fontsize=18, node_color="#e1575c", mst_node_size=200,
                           mst_edge_width=1.2, **kwds):
        """Draws a netwrok graph using the correlation matrix.
        layout_type: string
                    Options: circular_layout, fruchterman_reingold_layout, 
                             minimum_spanning_tree
        """
        network = self.network
        node_size = self.node_size
        edge_colours = self.edge_colours
        edge_width = self.edge_width
        if layout_type == 'minimum_spanning_tree':
            layout_type = 'fruchterman_reingold_layout'
            network = nx.minimum_spanning_tree(self.network)
            edge_colours = self.assign_edge_colours(network)
            node_size = mst_node_size
            edge_width = mst_edge_width

        sns.set(rc={'figure.figsize': figsize})
        font_dict = {'fontsize': title_fontsize}
        layout = getattr(nx, layout_type)

        nx.draw(network, pos=layout(network), with_labels=with_labels,
                node_size=node_size, node_color=node_color, edge_color=edge_colours,
                width=edge_width, **kwds)
        plt.title(title, fontdict=font_dict)
