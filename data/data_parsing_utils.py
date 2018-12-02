import xml.etree.ElementTree as etree
import json
import psycopg2
from psycopg2.extras import execute_values
import data_ingestion_utils


def parse_nodes(filename, credentials):
    """ Parse <node> elements in an OSM XML file, updating a database
    with the 'node' rows contained within.
    """
    data_ingestion_utils.create_node_table(credentials)
    node_insert_sql = 'INSERT INTO nodes (id, lat, lon) VALUES %s'

    conn = psycopg2.connect(**credentials)
    c = conn.cursor()

    # Initial values
    nodes = []
    lines_read = 0
    nodes_found = 0

    # Parse node elements
    for event, elem in etree.iterparse(filename):
        if elem.tag=='node':
            node_id = elem.get('id')
            lat = elem.get('lat')
            lon = elem.get('lon')

            if all([val is not None for val in [node_id, lat, lon]]):
                nodes.append((int(node_id), float(lat), float(lon)))
                nodes_found += 1
        lines_read += 1

        # Every 1 million rows, insert row batch into table
        if lines_read % 10**6 == 0:
            print(lines_read, 'lines read.')
            print('example node:', nodes[0])
            execute_values(c, node_insert_sql, nodes)
            conn.commit()
            nodes = []

        # Once we reach the <way> elements, we are done parsing nodes
        # Commit any remaining nodes, then exit.
        if elem.tag=='way':
            execute_values(c, node_insert_sql, nodes)
            conn.commit()
            print('Done')
            c.close()
            conn.close()

        # clear elem to avoid running out of memory
        elem.clear()

    # Ensure we close our connection, in case we do not find a <way> tag
    execute_values(c, node_insert_sql, nodes)
    c.close()
    conn.close()
    return


def parse_ways(filename, credentials, debug=False):
    """ Parse <way> elements in an OSM XML file, updating a database
    with the 'way' and 'edge' rows contained within.
    """
    conn = psycopg2.connect(**credentials)
    c = conn.cursor()

    # Set up tables
    data_ingestion_utils.create_edge_table(credentials)
    data_ingestion_utils.create_way_table(credentials)
    print("Edge and way tables created.")

    way_insert_sql = 'INSERT INTO ways (id, highway, bicycle, cycleway) VALUES %s'
    edge_insert_sql = 'INSERT INTO edges (way_id, start_node_id, end_node_id, highway, bicycle, cycleway) VALUES %s'

    elements_read = 0
    ways_found, edges_found = 0, 0
    mid_way = False
    way_rows_batch, edge_rows_batch = [], []

    for event, elem in etree.iterparse(filename, events=('start', 'end')):

        # Every 1 million rows, print out progress.
        if event == 'start':
            elements_read += 1
            if elements_read % 10**6 == 0:
                print(elements_read, 'elements read.')

        # Elements not relevant to parsing ways should be skipped; note that a
        # node within a way has the tag <nd>, an independent node is <node>
        if elem.tag not in ['way', 'nd', 'tag']:
            elem.clear()
            continue

        # When we find the start of a new way, start tracking its features
        if event == 'start' and elem.tag == 'way':
            mid_way = True
            way = {
                'id': elem.get('id', ''),
                'nodes': [],
                'highway': '',
                'bicycle': '',
                'cycleway': ''}

        # We found a node in a way
        if mid_way and elem.tag == 'nd':
            way['nodes'].append(elem.get('ref'))

        # We found a tag with way characteristics (eg road type)
        if mid_way and elem.tag == 'tag':
            key = elem.get('k')
            val = elem.get('v')
            if key in ['highway', 'bicycle', 'cycleway']:
                way[key] = val

        # We reached the end of a way; turn it into rows and add the rows to the database
        if (mid_way and event == 'end' and elem.tag == 'way'):

            # Filter out ways that are not relevant (that are not highways)
            if way['highway'] not in ['', 'footway', 'path', 'steps', 'construction', 'proposed', 'disused']:

                # A way row will contain the road characteristics
                way_row = format_way(way)
                way_rows_batch.append(way_row)
                ways_found += 1

                # Every 100k ways, insert into the database
                if len(way_rows_batch) > 10**5:
                    print(ways_found, "ways found and inserted")
                    execute_values(c, way_insert_sql, way_rows_batch)
                    conn.commit()
                    way_rows_batch = []

                # Every 1 million rows, insert into the database
                # Edge rows will contain rows for each pair of adjacent nodes
                edge_rows = format_edges(way)
                edge_rows_batch += edge_rows
                if len(edge_rows_batch) > 10**6:
                    execute_values(c, edge_insert_sql, edge_rows_batch)
                    conn.commit()
                    edges_found += len(edge_rows)
                    print(edges_found, "edges found and inserted")
                    edge_rows_batch = []

            # Reset stream parsing values
            mid_way = False
            nodes = []
            way = {}
            elem.clear()

    # Commit any last rows
    execute_values(c, way_insert_sql, way_rows_batch)
    execute_values(c, edge_insert_sql, edge_rows_batch)
    conn.commit()
    print('Done')

    # Close the connection
    c.close()
    conn.close()
    return


def format_way(way):
    ''' Given a way dictionary, output a database row tuple for the way.

    Ways have the schema:
      id BIGINT NOT NULL UNIQUE,
      highway text,
      bicycle text,
      cycleway text,
    '''
    return (
        int(way['id']),
        str(way['highway']),
        str(way['bicycle']),
        str(way['cycleway'])
    )


def format_edges(way):
    ''' Given a way dictionary, output an array of row tuples for edges.

    Edge rows have the schema:
      way_id BIGINT NOT NULL,
      start_node_id BIGINT NOT NULL,
      end_node_id BIGINT NOT NULL,
      highway text,
      bicycle text,
      cycleway text,

    Ignore ways with less than two nodes, since no edges can be drawn between.
    Return edges in both directions to allow for bi-directional travel.
    '''
    n = len(way['nodes'])
    if n < 2:
        # If less than 2 nodes, we can't form any edges.
        return []
    else:
        # Every pair of adjacent nodes is an edge
        edges = []
        for i in range(n - 1):
            edges.append((int(way['id']),
                          int(way['nodes'][i]),
                          int(way['nodes'][i + 1]),
                          str(way['highway']),
                          str(way['bicycle']),
                          str(way['cycleway'])))
        for i in range(1, n):
            edges.append((int(way['id']),
                          int(way['nodes'][i]),
                          int(way['nodes'][i - 1]),
                          str(way['highway']),
                          str(way['bicycle']),
                          str(way['cycleway'])))
        return edges


def parse_sample_file():
    # Parse nodes, ways, and edges from sample file
    sample = '/Users/jsennett/Downloads/map.osm'
    parse_nodes(sample, credentials, debug=True)
    parse_ways(sample, credentials, debug=True)


def parse_massachusetts():
    # Parse nodes, ways, and edges from massachusetts
    mass = '/Users/jsennett/Downloads/massachusetts-latest.osm'
    parse_nodes(mass, credentials, debug=False)
    parse_ways(mass, credentials, debug=False)
