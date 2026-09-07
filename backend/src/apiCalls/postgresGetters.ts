import pg from 'pg';

import type { PlayerOutput } from "../models/players.ts";

const getNamesFromPlayerIds = async (pool: pg.Pool, playerIds: string[]): Promise<PlayerOutput[]> => {
    const trimmedPlayerIds = playerIds.map((id) => id?.trim()).filter((id) => id);

    if (trimmedPlayerIds.length === 0) {
        return [];
    }

    try {
        const query = `
            SELECT player_id, name
            FROM players
            WHERE player_id = ANY($1)
        `;

        const result = await pool.query(query, [trimmedPlayerIds]);

        const players: PlayerOutput[] = result.rows.map((row) => ({
            playerId: row.player_id,
            name: row.name,
        }));

        return players;
    } catch (error) {
        console.error('Error getting player names from PostgreSQL:', error);
        return [];
    }
};

export { getNamesFromPlayerIds };