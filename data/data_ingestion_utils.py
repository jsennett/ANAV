import simplejson
import urllib.request
import psycopg2
from psycopg2.extras import execute_values


def create_node_table(credentials):

    conn = psycopg2.connect(**credentials)
    c = conn.cursor()

    try:
        c.execute("DROP TABLE IF EXISTS nodes")
        c.execute("""
                  CREATE TABLE nodes (
                  id BIGINT NOT NULL UNIQUE,
                  lat numeric NOT NULL,
                  lon numeric NOT NULL,
                  PRIMARY KEY (id))""")
        print("table created.")
    finally:
        conn.commit()
        c.close()
        conn.close()
        print("connection closed.")


def create_way_table(credentials):

    conn = psycopg2.connect(**credentials)
    c = conn.cursor()

    try:
        c.execute("DROP TABLE IF EXISTS ways")
        c.execute("""
                  CREATE TABLE ways (
                  id BIGINT NOT NULL UNIQUE,
                  highway text,
                  bicycle text,
                  cycleway text,
                  PRIMARY KEY (id))""")
        print("table created.")
    finally:
        conn.commit()
        c.close()
        conn.close()
        print("connection closed.")


def create_edge_table(credentials):

    conn = psycopg2.connect(**credentials)
    c = conn.cursor()

    try:
        c.execute("DROP TABLE IF EXISTS edges")
        c.execute("""
                  CREATE TABLE edges (
                  id BIGSERIAL PRIMARY KEY,
                  way_id BIGINT NOT NULL,
                  start_node_id BIGINT NOT NULL,
                  end_node_id BIGINT NOT NULL,
                  highway text,
                  bicycle text,
                  cycleway text
                  )""")
        print("table created.")
    finally:
        conn.commit()
        c.close()
        conn.close()
        print("connection closed.")


def add_spatial_node_column(credentials):

    conn = psycopg2.connect(**credentials)
    c = conn.cursor()

    try:
        c.execute("ALTER TABLE nodes ADD COLUMN coord geometry(POINT, 4326)")
        c.execute("UPDATE nodes SET coord = ST_SetSRID(ST_MakePoint(lon, lat), 4326)")
        c.execute("CREATE INDEX coord_gist ON nodes USING GIST (coord)")
    finally:
        conn.commit()
        print("coord column added.")
        c.close()
        conn.close()
        print("connection closed.")


def flag_irrelevant_nodes(credentials):

    conn = psycopg2.connect(**credentials)
    c = conn.cursor()

    try:
        c.execute("ALTER TABLE nodes ADD COLUMN is_road BOOLEAN")
        c.execute("UPDATE nodes SET is_road = TRUE WHERE id IN (SELECT id FROM ways WHERE highway != ''))")
    finally:
        conn.commit()
        print("coord column added.")
        c.close()
        conn.close()
        print("connection closed.")


def sample_table(credentials, table='nodes', columns='*', limit=10, filter=''):
    """ Get some rows from a table; useful for exploring and debugging. """
    # Connect
    conn = psycopg2.connect(credentials)
    c = conn.cursor()

    # Query
    rows = []
    sql = "SELECT %s FROM %s %s LIMIT %s"
    input = (columns, table, filter, limit)

    try:
        c.execute(sql, input)
        rows = c.fetchall()
    finally:
        c.close()
        conn.close()

    return rows


def count_rows(table, credentials, filter=''):
    """ Count rows in a table; useful for exploring and debugging. """
    # Connect
    conn = psycopg2.connect(**credentials)
    c = conn.cursor()

    # Query
    c.execute("SELECT COUNT(1) FROM %s %s" % (table, filter))
    count = c.fetchone()

    # Close
    c.close()
    conn.close()
    return count


def update_elevation(credentials, api_key, debug=False):

    url_head = 'https://maps.googleapis.com/maps/api/elevation/json?locations='
    url_tail = "&key=" + api_key

    # Get nodes from database
    conn = psycopg2.connect(**credentials)
    c = conn.cursor()
    batch_size = 300

    intervals = range(0, 14233) # intervals of 300 row batches 
    for interval in intervals:

        # Select a batch of rows
        batch_ns = (batch_size * interval, batch_size * (interval + 1))
        sql = "SELECT n, lat, lon FROM nodes WHERE n > %s AND n <= %s"
        c.execute(sql, (batch_ns))
        rows = c.fetchall()

        # Once we reach the end of the table, we won't have any rows left.
        if len(rows) == 0:
            break

        if debug:
            print('First row in batch:', rows[0])
            print('Last row in batch:', rows[-1])
            print('Rows fetched from database:', len(rows))

        # get elevation data for these rows
        url_middle = '|'.join([str(row[1]) + ',' + str(row[2]) for row in rows])
        query = url_head + url_middle + url_tail

        # Google API requires queries of length < 8192
        assert(len(query) < 8192) 
        response = simplejson.load(urllib.request.urlopen(query))

        if debug:
            print("status:", response.get('status'))
            print('number of elevations found:', len(response.get('results')))

        assert(response.get('status') == 'OK')
        assert(len(response.get('results', [])) == len(rows))

        # Combine id with elevation
        ns = [row[0] for row in rows]
        elevations = [row['elevation'] for row in response['results']]
        ns_to_elevations = list(zip(ns, elevations))

        sql_insert = "INSERT INTO elevation (n, elevation) VALUES %s"
        execute_values(c, sql_insert, ns_to_elevations)
        conn.commit()
        print("********** Nodes updated with elevation", batch_ns, "**********")

    c.close()
    conn.close()
