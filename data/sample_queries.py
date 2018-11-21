import time
import pymysql

def query_nodes_in_rectangle(db):

    conn = pymysql.connect(db)
    c = conn.cursor()

    c.execute("SELECT * FROM nodes WHERE " +
                "lat > 42.2704 AND " +
                "lat < 42.4648 AND " +
                "lon > -72.6924 AND " +
                "lon < -72.3182")
    results = c.fetchall()
    print(results[:10])
    print(len(results), "rows found.")

    c.close()
    conn.close()

def index_node_table(db):

    conn = pymysql.connect(db)
    c = conn.cursor()

    c.execute("CREATE INDEX lat_idx ON nodes(lat)")
    c.execute("CREATE INDEX lon_idx ON nodes(lon)")
    c.execute("CREATE INDEX lat_lon_idx ON nodes(lat, lon)")
    c.execute("CREATE INDEX lon_lat_idx ON nodes(lon, lat)")
    conn.commit()
    print("Indexes created.")
    c.close()
    conn.close()


def sample_table(table, limit, db, filter=''):
    """ Get some rows from a table; useful for exploring and debugging. """
    # Connect
    conn = pymysql.connect(db)
    c = conn.cursor()

    # Query
    c.execute("SELECT * FROM %s %s LIMIT %i" % (table, filter, limit))
    rows = c.fetchall()

    # Close
    c.close()
    conn.close()
    return rows


def count_rows(table, db, filter=''):
    """ Count rows in a table; useful for exploring and debugging. """
    # Connect
    conn = pymysql.connect(db)
    c = conn.cursor()

    # Query
    c.execute("SELECT COUNT(1) FROM %s %s" % (table, filter))
    count = c.fetchone()

    # Close
    c.close()
    conn.close()
    return count

def preview_tables(db):
    # Preview tables
    nodes = sample_table('nodes', 25, db)
    edges = sample_table('edges', 25, db)
    ways = sample_table('ways', 25, db)
    ways_with_attributes = sample_table('ways', 25, db, "WHERE bicycle != '' AND cycleway != ''")

    from pprint import pprint
    pprint(nodes)
    pprint(edges)
    pprint(ways)
    pprint(ways_with_attributes)

    num_nodes = count_rows('nodes', db)
    num_edges = count_rows('edges', db)
    num_ways = count_rows('ways', db)
    num_ways_with_attributes = count_rows('ways', db, "WHERE bicycle != '' AND cycleway != ''")

    print(num_nodes, "nodes rows")
    print(num_edges, "edges rows")
    print(num_ways, "ways rows")
    print(num_ways_with_attributes, "ways with all attributes")


if __name__ == '__main__':
    start = time.time()
    query_nodes_in_rectangle()
    print(time.time() - start, "seconds")
    # 468443 rows found.
    # 18.889117002487183

    start = time.time()
    index_node_table()
    print(time.time() - start, "seconds")
    # # 70 seconds to create indexes

    start = time.time()
    query_nodes_in_rectangle()
    print(time.time() - start, "seconds")
    # 468443 rows found.
    # 7.956459999084473 seconds
