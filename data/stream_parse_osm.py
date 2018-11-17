import xml.etree.ElementTree as etree
import json
import sqlite3


def parse_nodes(filename, db, drop=False):
    """ Parse <node> elements in an OSM XML file, updating a database
    with the 'node' rows contained within.
    """
    conn = sqlite3.connect(db)
    c = conn.cursor()

    # Drop table if it already exists
    if drop:
        c.execute('DROP TABLE nodes') # comment this out if nodes already exists

    # Set up nodes table
    c.execute("PRAGMA cache_size=-8000")
    c.execute('CREATE TABLE nodes (id int,  lat real, lon real)')

    nodes = []
    lines_read = 0

    # Parse node elements
    for event, elem in etree.iterparse(filename):
        if elem.tag=='node':
            node_id = elem.get('id')
            lat = elem.get('lat')
            lon = elem.get('lon')

            if all([val is not None for val in [node_id, lat, lon]]):
                nodes.append((int(node_id), float(lat), float(lon)))
        lines_read += 1

        # Every 1 million rows, insert row batch into table
        if lines_read % 10**6 == 0:
            print(lines_read, 'lines read.')
            print('example node:', nodes[0])

            c.executemany('INSERT INTO nodes VALUES (?,?,?)', nodes)
            conn.commit()
            nodes = []

        # Once we reach the <way> elements, we are done parsing nodes
        if elem.tag=='way':
            print('Done:', i)
            c.close()
            conn.close()
            return

        # clear elem to avoid running out of memory
        elem.clear()

    print('Done')
    c.close()
    conn.close()
    return


def parse_ways(filename, db, drop=False, debug=False):
    """ Parse <way> elements in an OSM XML file, updating a database
    with the 'way' and 'edge' rows contained within.
    """
    conn = sqlite3.connect(db)
    c = conn.cursor()

    # Set up table
    if drop:
        c.execute('DROP TABLE edges') # comment this out if nodes already exists
        c.execute('DROP TABLE ways') # comment this out if nodes already exists

    c.execute("PRAGMA cache_size=-8000")
    c.execute('CREATE TABLE edges (start_node_id int,  end_node_id int, way_id int)')
    c.execute('CREATE TABLE ways (id int, highway text, bicycle text, cycleway text)')

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
            c.execute('INSERT INTO ways VALUES (?,?,?,?)', way_row)

            # Edge rows will contain rows for each pair of adjacent nodes
            edge_rows = format_edges(way)
            if debug: print(edge_rows)
            c.executemany('INSERT INTO edges VALUES (?,?,?)', edge_rows)

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
        str(way['bicycle']),
        str(way['cycleway']),
        str(way['highway'])
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
    # Parse nodes and rows from sample file
    sample = '/Users/jsennett/Downloads/map.osm'
    parse_nodes(sample, 'sample.db', drop=True, debug=True)
    parse_ways(sample, 'sample.db', drop=True, debug=False)


def parse_massachusetts():
    # Parse nodes and rows from massachusetts
    mass = '/Users/jsennett/Downloads/massachusetts-latest.osm'
    parse_nodes(mass, 'mass.db', drop=True, debug=False)
    parse_ways(mass, 'mass.db', drop=True, debug=False)


if __name__ == '__main__':
    # Parse mass file, creating the 'mass.db' sqlite database file
    parse_massachusetts()
