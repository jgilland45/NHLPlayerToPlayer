import type { Driver, Session } from 'neo4j-driver';

const getTeammatesOfPlayer = async (driver: Driver, playerId: string): Promise<Array<string>> => {
    const trimmedPlayerId = playerId?.trim();
    const numericPlayerId = Number(trimmedPlayerId);

    if (!trimmedPlayerId || !Number.isInteger(numericPlayerId) || numericPlayerId <= 0) {
        return [];
    }

    const session: Session = driver.session();

    try {
        // get teammates of the player from Neo4j database
        const result = await session.executeRead((tx) =>
            tx.run(
                `
                MATCH n = (p:Player {id: $playerId})-[rel:TEAMMATE]-(teammate:Player)
                return
                rel.gameType AS gametype,
                rel.season AS season,
                rel.teamId AS teamid,
                p.id AS p1id,
                teammate.id AS p2id;`,
                { playerId: numericPlayerId },
            ),
        );

        const data: Array<string> = result.records.map(
            (record) => record.get('p2id').toString()
        );

        return data;
    } catch (error) {
        console.error('Error getting teammates of player:', error);
        return [];
    } finally {
        await session.close();
    }
};

export { getTeammatesOfPlayer };