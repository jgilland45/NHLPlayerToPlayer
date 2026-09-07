import express, { type Express, type Request, type Response } from 'express';
import cors from 'cors';
import neo4j from 'neo4j-driver';
import pg from 'pg';

import { searchNHLPlayersByName } from './apiCalls/nhlSearch.ts';
import { getTeammatesOfPlayer } from './apiCalls/neo4jGetters.ts';
import type { PlayerOutput } from './models/players.ts';
import { getNamesFromPlayerIds } from './apiCalls/postgresGetters.ts';

const app: Express = express();
const port = process.env.PORT || 3000;

const neo4jUri: string = process.env.NEO4J_URI || 'bolt://localhost:7687';
const neo4jUser: string = process.env.NEO4J_USER || 'neo4j';
const neo4jPassword: string = process.env.NEO4J_PASSWORD || 'password';

const neo4jDriver: neo4j.Driver = neo4j.driver(neo4jUri, neo4j.auth.basic(neo4jUser, neo4jPassword));

const pgpool = new pg.Pool({
    user: process.env.POSTGRES_USER || 'postgres',
    password: process.env.POSTGRES_PASS || 'password',
    host: 'localhost',
    port: 5432,
    database: 'nhlptphockeydata',
});

app.use(cors());
app.use(express.json());

app.get('/', (req: Request, res: Response) => {
    res.send('Hello World!');
});

app.post('/api/searchPlayers', async (req: Request, res: Response) => {
    const playerName = req.body.playerName;

    try {
        const outputPlayers: Array<PlayerOutput> = await searchNHLPlayersByName(playerName);
        res.json(outputPlayers);
    } catch (error) {
        console.error('Error searching NHL players:', error);
        res.status(500).json({ error: 'An error occurred while searching for players.' });
    }
});

app.post('/api/getTeammatesOfPlayer', async (req: Request, res: Response) => {
    const playerId = req.body.playerId;

    try {
        const teammateIds: Array<string> = await getTeammatesOfPlayer(neo4jDriver, playerId);
        const teammatePlayerOutputs: Array<PlayerOutput> = await getNamesFromPlayerIds(pgpool, teammateIds);
        res.json(teammatePlayerOutputs);
    } catch (error) {
        console.error('Error getting teammates of player:', error);
        res.status(500).json({ error: 'An error occurred while fetching teammates.' });
    }
});

const server = app.listen(port, () => {
    console.log(`Example app listening on port ${port}`);
});

const shutdown = async () => {
    server.close();
    await pgpool.end();
    await neo4jDriver.close();
};

process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);