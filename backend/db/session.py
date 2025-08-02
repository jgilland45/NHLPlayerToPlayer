# backend/db/graph_session.py
from neo4j import GraphDatabase
from backend.core.config import settings

class GraphDB:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def run_query(self, query, parameters=None):
        with self._driver.session() as session:
            result = session.run(query, parameters)
            return [record for record in result]

# Create a single, importable instance of the graph database connection
graph_db = GraphDB(
    uri=settings.NEO4J_URI,
    user=settings.NEO4J_USER,
    password=settings.NEO4J_PASSWORD
)

# Dependency for FastAPI
def get_graph_db():
    return graph_db