import simplejson
import urllib.request
import csv
from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.overpass import overpassQueryBuilder, Overpass

"""
Data Collection of nodes for a given area.
Functions:
Downloads Data using overpass api included in the OSMPythonTools module
Create adjacency list (Graph)
Save data to file to help resources when reloading app
"""


class NodeCollector:

    def __init__(self, input_city, input_state):
        self.destination = [input_city.capitalize(), input_state.capitalize()]
        self.nominatim = Nominatim()
        self.overpass = Overpass()
        self.nodes = {}
        self.highways = {}
        self.adjacent_list = {}
        self.elevation_query_list = {}

    def get_nodes(self):
        return self.nodes

    def get_highways(self):
        return self.highways

    def get_adjacency_list(self):
        return self.adjacent_list

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

        # Populates the node list (Nodes actually within query area)
        for element in queried_nodes:
            node_id = element.get('id')
            node_lat = element.get('lat')
            node_lon = element.get('lon')
            self.nodes[node_id] = (node_lat, node_lon)

        # part 2 of the query result modified to include roads that are accessible to bike riders
        # https://wiki.openstreetmap.org/wiki/Key:highway
        queried_highways = [element for element in elements
                            if (element.get('type') == 'way') and (element.get('tags')) and (
                                element.get('tags').get('highway')
                                in ['service', 'tertiary', 'residential', 'secondary', 'cycleway', 'trunk', 'primary']
                                or element.get('tags').get('route') == 'bicycle')]

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
            csv_writer = csv.writer(f, delimiter=',')
            csv_writer.writerows(csv_nodes)

    """
    Collects elevation info for all nodes in query area using google cloud platform elevation API 
    input: [(id, lat, lon), (id, lat, lon), … ]
    output: [(id, lat, lon, elev), (id, lat, lon, elev), … ]
    """
    @staticmethod
    def download_elevation_info(node_list, api_key):
        service_url = 'https://maps.googleapis.com/maps/api/elevation/json?locations='
        url_tail = "&key=" + api_key

        # formats block into a string so it can be queried easily
        # to the parsed blocks list
        block = []

        for single_node in node_list:
            block.append(single_node[1] + "," + single_node[2])

        parsed_block = '|'.join(block)

        # queries elevation api and returns query_results
        query_results = []
        current_node_index = 0

        query = service_url + parsed_block + url_tail
        response = simplejson.load(urllib.request.urlopen(query))

        for result_set in response['results']:
            result = (node_list[current_node_index][0], node_list[current_node_index][1],
                      node_list[current_node_index][2], result_set['elevation'])
            query_results.append(result)
            current_node_index += 1
        # print(node_list)  # input
        # print(query_results)  # output
        return query_results


if __name__ == '__main__':

    # city = input("City: ")
    # state = input("State: ")
    city = "Amherst"
    state = "Massachusetts"
    collector = NodeCollector(city, state)

    limit = 0
    node_list = []

    with open('../nodes.csv', 'r') as f:
        for line in f:
            split_line = f.readline().strip('\n').split(',')
            node = (split_line[0], split_line[1], split_line[2])
            node_list.append(node)
            limit += 1

            if limit == 320:
                break

    with open('../api_key.txt', 'r') as key:
        api_key = key.readline()

    node_input = node_list
    output = collector.download_elevation_info(node_list, api_key)

    print(node_input)
    print(output)








