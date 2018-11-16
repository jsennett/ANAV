import xml.etree.ElementTree as etree
import json
import sqlite3


def parse_nodes(filename):

    conn = sqlite3.connect('nodes.db')
    c = conn.cursor()

    # Set up table
    c.execute('DROP TABLE nodes') # comment this out if nodes already exists
    c.execute("PRAGMA cache_size=-8000")
    c.execute('CREATE TABLE nodes (id int,  lat real, lon real)')

    nodes = []
    i = 0

    for event, elem in etree.iterparse(filename):
        if elem.tag=='node':
            node_id = elem.get('id')
            lat = elem.get('lat')
            lon = elem.get('lon')

            if all([val is not None for val in [node_id, lat, lon]]):
                nodes.append((int(node_id), float(lat), float(lon)))
        i += 1

        # Every 1 million rows, insert row batch into table
        if i % 10**6 == 0:
            print(i / (10**6), 'million lines read.')
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

    print('Done:', i)
    c.close()
    conn.close()
    return


if __name__ == '__main__':

    filename = '/Users/jsennett/Downloads/massachusetts-latest.osm'
    parse_nodes(filename)
