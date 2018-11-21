import xml.etree.ElementTree as etree
import json
import pymysql


def parse_nodes(filename, credentials, debug=False):
    """ Parse <node> elements in an OSM XML file, updating a database
    with the 'node' rows contained within.
    """
    conn = pymysql.connect(**credentials)
    c = conn.cursor()

    # Set up nodes table
    c.execute('DROP TABLE IF EXISTS nodes') # comment this out if nodes already exists
    c.execute(
        """
        CREATE TABLE nodes
        (id BIGINT NOT NULL,
        lat real NOT NULL,
        lon real NOT NULL,
        PRIMARY KEY (id));
        """
    )

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
            if debug: print(nodes)
            c.executemany('INSERT INTO nodes VALUES (%s,%s,%s)', nodes)
            conn.commit()
            nodes = []

        # Once we reach the <way> elements, we are done parsing nodes
        # Commit any remaining nodes, then exit.
        if elem.tag=='way':
            c.executemany('INSERT INTO nodes VALUES (%s,%s,%s)', nodes)
            conn.commit()
            print('Done')
            c.close()
            conn.close()
            return

        # clear elem to avoid running out of memory
        elem.clear()

    # Ensure we close our connection, in case we do not find a <way> tag
    c.close()
    conn.close()
    return


def parse_ways(filename, credentials, debug=False):
    """ Parse <way> elements in an OSM XML file, updating a database
    with the 'way' and 'edge' rows contained within.
    """
    conn = pymysql.connect(**credentials)
    c = conn.cursor()

    # Set up table
    c.execute('DROP TABLE IF EXISTS edges') # comment this out if nodes already exists
    c.execute('DROP TABLE IF EXISTS ways') # comment this out if nodes already exists

    c.execute("""
                CREATE TABLE edges (
                    start_node_id BIGINT,
                    end_node_id BIGINT,
                    way_id BIGINT
                    )
              """
              )
    c.execute("""
                CREATE TABLE ways (
                    id BIGINT,
                    highway text,
                    bicycle text,
                    cycleway text
                    )
              """
              )

    lines_read = 0
    ways_found = 0
    mid_way = False
    for event, elem in etree.iterparse(filename, events=('start', 'end')):

        # Every 1 million rows, print out progress.
        lines_read += 1
        if lines_read % 10**6 == 0:
            print(lines_read, 'lines read.')

        # Elements not relevant to parsing ways; note that a
        # node within a way has the tag <nd>, not <node>
        if elem.tag in ['node', 'member', 'relation']:
            elem.clear()
            continue

        # We found a new way
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

        # We found a tag, with way characteristics (eg road type)
        if mid_way and elem.tag == 'tag':
            key = elem.get('k')
            val = elem.get('v')
            if key in ['highway', 'bicycle', 'cycleway']:
                way[key] = val

        # We reached the end of a way; turn it into rows and add the rows to the database
        if mid_way and event == 'end' and elem.tag == 'way':

            # A way row will contain the road characteristics
            way_row = format_way(way)
            if debug: print(way_row)
            c.execute('INSERT INTO ways VALUES (%s,%s,%s,%s)', way_row)

            # Edge rows will contain rows for each pair of adjacent nodes
            edge_rows = format_edges(way)
            if debug: print(edge_rows)
            c.executemany('INSERT INTO edges VALUES (%s,%s,%s)', edge_rows)

            # Reset stream parsing values
            ways_found += 1
            mid_way = False
            nodes = []
            way = {}
            elem.clear()

            # Every 1000 rows, commit changes to update the database in batches
            if ways_found > 0 and ways_found % 10**4 == 0:
                conn.commit()
                print(ways_found, "ways found")

    # Commit any last rows
    conn.commit()
    print('Done')

    # close the connection
    c.close()
    conn.close()
    return


def format_way(way):
    ''' Given a way dictionary, output a database row tuple for the way '''
    # (id int, highway text, bicycle text, cycleway text)
    return (
        int(way['id']),
        str(way['highway']),
        str(way['bicycle']),
        str(way['cycleway'])
    )

def format_edges(way):
    ''' Given a way dictionary, output an array of row tuples for edges
        For example, given a way with id X with nodes [A, B, C], our edges are:
            [ (X, A, B), (X, B, C), (X, C, B), (X, B, A) ]
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
                          int(way['nodes'][i + 1])))
        for i in range(1, n):
            edges.append((int(way['id']),
                          int(way['nodes'][i]),
                          int(way['nodes'][i - 1])))
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


if __name__ == '__main__':
    # Set credentials for MySQL connection
    import os
    credentials = {
        'host': 'localhost',
        'user': 'root',
        'password': os.environ['MYSQL_PASSWORD'],
        'database': 'Anav'
    }

    # Parse mass file, creating MySQL database tables
    parse_massachusetts()
