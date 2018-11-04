import simplejson
import urllib
import csv
from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.overpass import overpassQueryBuilder, Overpass

"""
Data Collection of nodes for a given area.
Functions:
Downloads Data using overpass api 
Create adjacency list (Graph)
Save data to file to help resources when reloading app
"""


class NodeCollector:

    def __init__(self, input_city, input_state):
        self.destination = [input_city.capitalize(), input_state.capitalize()]
        self.nominatim = Nominatim()
        self.overpass = Overpass()
        self.nodes = None
        self.highways = None
        self.adjacent_list = {}
        self.filtered_list = {}

    """ 
    Download OSM <way> and <node> elements from given city, state 
    """
    def download_query_data(self):
        destination_string = ', '.join(self.destination)  # creates string used to get destination ID 'city, state'
        area_id = self.nominatim.query(destination_string).areaId()  # gets the destination ID of area

        # --------- OverPass Query Call ---------
        destination_query = overpassQueryBuilder(area=area_id, elementType=['node', 'way'], out='body')
        result = self.overpass.query(destination_query).toJSON()
        # ----------------------------------------

        """
        The JSON returned for the query has two main parts
        
        1) The list of all the nodes for the given area as well as the 
        attributes associated with that node (eg. lat, lon, type)
        
        2) Array type structures for all road types (highway, trail, residential etc.) constructed of node IDs
        [type: highway, nodes: [1, 2, 3, 4, 5, 6]]
        
        Note: there is also some junk data collected that can be removed initially from the query result which can
        improve efficiency, but needs to be looked further into.
        """

        elements = result['elements']  # Above information is tagged with an element type

        # part 1 of the query result
        queried_nodes = [element for element in elements
                         if (element.get('type') == 'node')]

        # part 2 of the query result modified to include roads that are accessible to bike riders
        queried_highways = [element for element in elements
                            if (element.get('type') == 'way') and (element.get('tags')) and (
                                element.get('tags').get('highway')
                                in ['service', 'tertiary', 'residential', 'secondary', 'cycleway'] or element.get(
                                    'tags').get('route') == 'bicycle')]

        self.nodes = queried_nodes
        self.highways = queried_highways

    """
    creates the adjacency list from the queried_highways. Since we do not have an actual list of all the edges,
    creating the adjacency list requires us to identify edges.
     
    We iterate each highway and get the number of nodes in that highway, we then iterate each node and identify whether
    it is the first node in the highway, a node within the inside (between first and last node) of the highway, or the 
    last node in the highway.
    
    Three Conditions:
    1) if the current node is the first node, then its only neighbor is the next node, adj_list[current_node] = [next_node]
    
    2) if the current node is within the highway, the its neighbors are the node that come before and after it 
    adj_list[current_node] = [next_node, previous node]
    
    3) if the current node is the last node, then its only neighbor is the previous node, adj_list[current_node] = [previous_node]
    
    """
    def create_adjacency_list(self):
        # Build Adjacency List
        adjacency_list = {}

        # for each highway get the number of nodes it contains
        for highway in self.highways:
            nodes = highway.get('nodes')  # all the nodes in the highway
            number_of_nodes = len(nodes)  # number of nodes in the highway

            for node_index in range(number_of_nodes):
                # first node
                if node_index == 0:
                    current_node = nodes[node_index]
                    next_node = nodes[node_index + 1]

                    if adjacency_list.get(current_node) is None:
                        adjacency_list[current_node] = [next_node]

                    else:
                        if next_node not in adjacency_list.get(current_node):
                            adjacency_list[current_node].append(next_node)

                # middle node
                if 0 < node_index < number_of_nodes - 1:
                    current_node = nodes[node_index]
                    next_node = nodes[node_index + 1]
                    previous_node = nodes[node_index - 1]

                    if adjacency_list.get(current_node) is None:
                        adjacency_list[current_node] = [next_node, previous_node]

                    else:
                        if next_node not in adjacency_list.get(current_node):
                            adjacency_list[current_node].append(next_node)

                        if previous_node not in adjacency_list.get(current_node):
                            adjacency_list[current_node].append(previous_node)

                # last node
                if node_index == number_of_nodes:
                    current_node = nodes[node_index]
                    previous_node = nodes[node_index - 1]

                    if adjacency_list.get(current_node) is None:
                        adjacency_list[current_node] = list()
                    elif adjacency_list.get(current_node) is not None:
                        if previous_node not in adjacency_list.get(current_node):
                            adjacency_list.get(current_node).append(previous_node)

        self.adjacent_list = adjacency_list

    """
    Loads elevation info previously downloaded using elevation download method
    Note: Believe Josh Wrote this method
    """
    # TODO: Clean Me
    def reload_elevation_info(self):
        # Load Elevations
        elevation_list = {}

        with open('nodeElevations.txt', 'r') as r:
            for line in r:
                comma_delimited_line = line.split(',')
                elevation_list[comma_delimited_line[0]] = comma_delimited_line[1]

        # print("elevation:", len(elevation_list))
        # print("adjacencyList:", len(self.adjacent_list))
        # print("elevation nodes in adjList", sum([int(n) in self.adjacent_list for n in elevation_list]))

        node_elevation_and_coordinates = {}

        for node_key in elevation_list.keys():
            node_elevation_and_coordinates[int(node_key)] = [float(elevation_list[node_key]), self.filtered_list[int(node_key)]]

        print("adjList nodes in elevation", sum([str(n) in elevation_list for n in self.adjacent_list]))

        filtered_adjacency_list = {}

        for key in self.adjacent_list:
            if str(key) in elevation_list:
                filtered_adjacency_list[key] = []
                for neighbor in self.adjacent_list[key]:
                    if str(neighbor) in elevation_list:
                        filtered_adjacency_list[key].append(neighbor)

        print("filtered_adjacencyList:", len(filtered_adjacency_list))

        csv_nodes = []

        for id in node_elevation_and_coordinates.keys():
            lat, lon = node_elevation_and_coordinates[id][1]
            csv_nodes.append([id, lat, lon])

        with open("nodes.csv", 'w+') as f:
            csvWriter = csv.writer(f, delimiter=',')
            csvWriter.writerows(csv_nodes)

    """
    -------------------------------------- Resource Demanding ----------------------------------------------------------
    Collects elevation info for all nodes in query area using google cloud platform elevation API 
    You may be wondering 'why there are 2 dictionaries labeled unfiltered node list and filtered node list!?'
    Essentially the highways containing the collection of nodes include nodes outside of the queried area that we do not 
    have information on (lat, lon) so we must filter them out and fill missing information with a place holder value.
    Download information for all nodes in this filtered list and write to a file comma delimited (nodeID, elevation)
    """
    # TODO: fill missing information with a place holder value (Read Above)
    def download_elevation_info(self, node_list, key):
        # creates dictionary of nodes containing information that will later be used for elevation collection
        unfiltered_node_list = {}
        filtered_node_list = {}

        # Populates the filtered node list (Nodes actually within query area)
        for element in self.nodes:
            node_id = element.get('id')
            node_lat = element.get('lat')
            node_lon = element.get('lon')
            unfiltered_node_list[node_id] = (node_lat, node_lon)

        for node_id in self.adjacent_list:
            filtered_node_list[node_id] = unfiltered_node_list.get(node_id)

        self.filtered_list = filtered_node_list

        # Get elevation for every node
        api_key = key
        with open('nodeElevations.txt', 'a+') as f:
            for node in node_list:
                if node_list.get(node) is not None:
                    lat = node_list.get(node)[0]
                    lon = node_list.get(node)[1]
                    url_builder = 'https://maps.googleapis.com/maps/api/elevation/json?locations=' + str(lat) + "," + \
                                  str(lon) + '&key=' + api_key
                    response = simplejson.load(urllib.request.urlopen(url_builder))

                    for result_set in response['results']:
                        f.write(str(node) + ',' + str(result_set['elevation']) + '\n')


if __name__ == '__main__':
    pass