# backend/db/graph_session.py
import asyncio
import functools
from neo4j import GraphDatabase
from backend.core.config import settings

class GraphDB:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def _execute_query(self, query, parameters):
        """
        The actual synchronous database call, wrapped in a transactional
        unit of work that the driver can automatically retry on transient errors.
        """
        def unit_of_work(tx, query, parameters):
            result = tx.run(query, parameters)
            # Consume the result inside the transaction to avoid issues.
            return [record for record in result]

        with self._driver.session() as session:
            return session.execute_write(unit_of_work, query, parameters)

    async def run_query(self, query, parameters=None):
        """Runs a query in a thread pool to avoid blocking the event loop."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._execute_query, query, parameters)

    def _execute_unit_of_work(self, work_function, **kwargs):
        """The synchronous executor for a multi-step transactional function."""
        with self._driver.session() as session:
            # The work_function will receive the transaction object (tx)
            # and should perform all its database operations using it.
            return session.execute_write(work_function, **kwargs)

    async def run_unit_of_work(self, work_function, **kwargs):
        """Runs a multi-step function as a single, atomic, and retryable transaction."""
        loop = asyncio.get_running_loop()
        # FIX: Use functools.partial to correctly pass keyword arguments
        # to the function running in the thread pool executor. run_in_executor
        # itself does not support passing kwargs.
        partial_func = functools.partial(self._execute_unit_of_work, work_function, **kwargs)
        return await loop.run_in_executor(None, partial_func)

# Create a single, importable instance of the graph database connection
graph_db = GraphDB(
    uri=settings.NEO4J_URI,
    user=settings.NEO4J_USER,
    password=settings.NEO4J_PASSWORD
)

# Dependency for FastAPI
def get_graph_db():
    return graph_db