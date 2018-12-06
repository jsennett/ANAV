import psycopg2
from psycopg2.extras import execute_values
from geographiclib.geodesic import Geodesic


def edges_within_radius(credentials, lat=42.359055, lon=-71.093500, radius=1000, limit=None):
    """
    Return edges within a search radius around a point.
    This will query the database, returning a list of edges
    each with the relevant information for the edge.

    @input
    credentials: dict - database credentials
    lat: float - latitude of midpoint
    lon: float - longitude of midpoint
    radius: float - radius, in meters
    limit: int, or NoneType - number of rows to limit in query
    """
    # If no limit or negative limit, convert to limit to an unreachable limit
    if limit is None or limit <= 0:
        limit = 10000000 # larger than our table

    conn = psycopg2.connect(**credentials)
    c = conn.cursor()

    # ST_DWithin uses SRID units (degrees), so we need to convert
    # meters to approximate degrees (1 degree ~ 111,000 meters)
    radius_in_degrees = radius / 111000.0

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
    input = (lon, lat, radius_in_degrees, limit)

    try:
        c.execute(sql, input)
        results = c.fetchall()
    finally:
        c.close()
        conn.close()

    return results


def nearest_node(credentials, lat=42.359055, lon=-71.093500, meters=100):
    """
    Note: it is slow (~1 min) to search for a the nearest node to a point
    that does not exist in the database.
    """
    conn = psycopg2.connect(**credentials)
    c = conn.cursor()

    results = () # initialize results, in case we are unable to fetch them
    sql = """
            SELECT start_node_id, start_node_lat, start_node_lon
            FROM edges
            ORDER BY start_node_coord <-> ST_SetSRID(ST_MakePoint(%s, %s),4326)
            LIMIT 1;
          """
    input = (lon, lat)

    try:
        c.execute(sql, input)
        result = c.fetchone()
    finally:
        c.close()
        conn.close()

    # If the nearest node is further than our allowed distance,
    # we cannot find a closest node. This ends up being faster
    # than including a search radius within the SQL query
    if result is not None:

        dist = Geodesic.WGS84.Inverse(lat, lon, result[1], result[2])['s12']
        if dist > meters:
            return None

    return result
