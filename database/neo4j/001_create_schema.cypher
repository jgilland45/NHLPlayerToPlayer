// Run once against the target Neo4j database before ingestion.
CREATE CONSTRAINT player_id_unique IF NOT EXISTS
FOR (player:Player)
REQUIRE player.id IS UNIQUE;