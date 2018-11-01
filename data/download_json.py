from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.overpass import overpassQueryBuilder, Overpass
import json

class Main:

    def query(self):
        """ Download OSM <way> and <node> elements from Amherst, Massachustets """
        nominatim = Nominatim()
        area_Id = nominatim.query('Amherst, Massachusetts').areaId()

        # Query Way Data
        overpass = Overpass()
        query = overpassQueryBuilder(area=area_Id, elementType=['node', 'way'], out='body')
        result = overpass.query(query).toJSON()

        elements = result['elements']

        queried_highways = [element for element in elements
                            if (element.get('type') == 'way') and (element.get('tags')) and (
                                element.get('tags').get('highway')
                                in ['service', 'tertiary', 'residential', 'secondary', 'cycleway'] or element.get(
                                    'tags').get('route') == 'bicycle')]

        queried_nodes = [element for element in elements
                         if (element.get('type') == 'node')]

        # Build Adjacency List
        adjacencyList = dict()

        for element in queried_highways:
            nodes = element.get('nodes')  # all the nodes in each element
            number_of_nodes = len(nodes)

            for x in range(number_of_nodes):
                if x == 0:
                    current_node = nodes[x]
                    next_node = nodes[x + 1]

                    if adjacencyList.get(current_node) is None:
                        adjacencyList[current_node] = list()
                        adjacencyList[current_node].append(next_node)
                    elif adjacencyList.get(current_node) is not None:
                        if next_node not in adjacencyList.get(current_node):
                            adjacencyList[current_node].append(next_node)

                if 0 < x < number_of_nodes - 1:
                    current_node = nodes[x]
                    next_node = nodes[x + 1]
                    previous_node = nodes[x - 1]

                    if adjacencyList.get(current_node) is None:
                        adjacencyList[current_node] = list()
                        adjacencyList[current_node].append(next_node)
                        adjacencyList[current_node].append(previous_node)
                    elif adjacencyList.get(current_node) is not None:
                        if next_node not in adjacencyList.get(current_node):
                            adjacencyList[current_node].append(next_node)
                        if previous_node not in adjacencyList.get(current_node):
                            adjacencyList[current_node].append(previous_node)

                if x == number_of_nodes:
                    current_node = nodes[x]
                    previous_node = nodes[x - 1]

                    if adjacencyList.get(current_node) is None:
                        adjacencyList[current_node] = list()
                    elif adjacencyList.get(current_node) is not None:
                        if previous_node not in adjacencyList.get(current_node):
                            adjacencyList.get(current_node).append(previous_node)

        # for key in adjacencyList:
        #    print(str(key) + ": " + str(adjacencyList[key]))

        # creates dictionary of unfiltered nodes -  key node id - value tuple(lat, lon)
        unfiltered_node_list = dict()

        for element in queried_nodes:
            node_id = element.get('id')
            node_lat = element.get('lat')
            node_lon = element.get('lon')
            tup = (node_lat, node_lon)
            unfiltered_node_list[node_id] = tup

        # print("Number of nodes: " + str(len(unfiltered_node_list)))  # unfiltered nodes

        # for key in node_list:
        #    print(str(key) + ": " + str(node_list[key]))

        # creates the filtered node list
        filtered_node_list = dict()

        for node in adjacencyList:
            filtered_node_list[node] = unfiltered_node_list.get(node)

        # Load Elevations
        elevation_list = dict()

        with open('nodeElevations.txt', 'r') as r:
            for line in r:
                comma_delimited_line = line.split(',')
                elevation_list[comma_delimited_line[0]] = comma_delimited_line[1]

        # for key in elevation_list:
        #     print(str(key) + ": " + str(elevation_list[key]))

        print("elevation:", len(elevation_list))
        print("adjacencyList:", len(adjacencyList))
        print("filtered_node_list:", len(filtered_node_list))
        print("unfiltered_node_list:", len(unfiltered_node_list))

        print("elevation nodes in adjList", sum([int(n) in adjacencyList for n in elevation_list]))

        node_elevation_and_coordinates = {}
        for n in elevation_list.keys():
            node_elevation_and_coordinates[int(n)] = [float(elevation_list[n]), filtered_node_list[int(n)]]

        print("adjList nodes in elevation", sum([str(n) in elevation_list for n in adjacencyList]))

        # uncomment to overwrite files
        # with open('nodes.txt', 'w') as f:
        #     json.dump(node_elevation_and_coordinates, f)
        #
        filtered_adjacencyList = {}
        for key in adjacencyList:
            if str(key) in elevation_list:
                filtered_adjacencyList[key] = []
                for neighbor in adjacencyList[key]:
                    if str(neighbor) in elevation_list:
                        filtered_adjacencyList[key].append(neighbor)

        print("filtered_adjacencyList:", len(filtered_adjacencyList))

        # with open('edges.txt', 'w') as f:
        #     json.dump(filtered_adjacencyList, f)


        # print(node_elevation_and_coordinates)
        # print(len(node_elevation_and_coordinates))

        csv_nodes = []
        for id in node_elevation_and_coordinates.keys():
            lat, lon = node_elevation_and_coordinates[id][1]
            csv_nodes.append([id, lat, lon])

        import csv
        with open("nodes.csv", 'w+') as f:
            csvWriter = csv.writer(f, delimiter=',')
            csvWriter.writerows(csv_nodes)

        # print(filtered_adjacencyList)
        # filtered_node_list - Node, Tuple(Lat, Lot)
        # nodeElevations.txt - Node, Elevation

        # print("Number of nodes: " + str(len(filtered_node_list)))  # filtered nodes

        # for key in filtered_node_list:
            # print(str(key) + ": " + str(filtered_node_list[key]))
        """
        # Get elevation for every node
        api_key = ''
        with open('nodeElevations.txt', 'a+') as f:
            for node in filtered_node_list:
                if filtered_node_list.get(node) is not None:
                    lat = filtered_node_list.get(node)[0]
                    lon = filtered_node_list.get(node)[1]
                    url_builder = 'https://maps.googleapis.com/maps/api/elevation/json?locations=' + str(lat) + "," + str(lon) + '&key=' + api_key
                    response = simplejson.load(urllib.request.urlopen(url_builder))

                    for resultset in response['results']:
                        f.write(str(node) + ',' + str(resultset['elevation']) + '\n')
        """

if __name__ == '__main__':
    query = Main()
    query.query()
