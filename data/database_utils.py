import psycopg2
from psycopg2.extras import execute_values


def nodes_within_radius(credentials, lat=42.359055, lon=-71.093500, radius=.1, limit=250000):

    # Make sure that user-input coordinates are valid
    # if not ((-73.6 < lon < -69.8) and (41.0 > lat > 43.0)):
    if lon < -73.6 or lon > -69.8 or lat < 41.0 or lat > 43.0:
        print("Invalid coordinates; not in MA:", (lat, lon))
        return []

    conn = psycopg2.connect(**credentials)
    c = conn.cursor()

    results = []
    sql = """
            SELECT
                start_node_id, start_node_lat, start_node_lon,
                end_node_id, end_node_lat, end_node_lon,
                distance, highway_group, bicycle_group, incline
            FROM edges
            WHERE ST_DWithin(start_node_coord, ST_SetSRID(ST_Point(%s, %s), 4326), %s)
            LIMIT %s;
          """
    input = (lon, lat, radius, limit)

    try:
        c.execute(sql, input)
        results = c.fetchall()
    except:
        print("exception - query cancelled.")
    finally:
        c.close()
        conn.close()

    return results


def nearest_node(credentials, lat=42.359055, lon=-71.093500, meters=100):

    # Make sure that user-input coordinates are valid
    # if not ((-73.6 < lon < -69.8) and (41.0 > lat > 43.0)):
    if lon < -73.6 or lon > -69.8 or lat < 41.0 or lat > 43.0:
        print("Invalid coordinates; not in MA:", (lat, lon))
        return ()

    conn = psycopg2.connect(**credentials)
    c = conn.cursor()

    results = () # initialize results, in case we are unable to fetch them
    sql = """
            SELECT
                start_node_id, start_node_lat, start_node_lon,
                end_node_id, end_node_lat, end_node_lon,
                distance, highway_group, bicycle_group, incline
            FROM edges
            WHERE ST_Distance_Sphere(start_node_coord, ST_MakePoint(%s, %s)) <= %s
            ORDER BY start_node_coord <-> ST_SetSRID(ST_MakePoint(%s, %s),4326)
            LIMIT 1;
          """
    input = (lon, lat, meters, lon, lat)

    try:
        c.execute(sql, input)
        results = c.fetchone()
    finally:
        c.close()
        conn.close()

    return results
