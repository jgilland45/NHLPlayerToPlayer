import express, { type Express, type Request, type Response } from 'express';
import cors from 'cors';

import { searchNHLPlayersByName } from './apiCalls/nhlSearch.ts';
import type { PlayerOutput } from './models/players.ts';

const app: Express = express();
const port = process.env.PORT || 3000;

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

app.listen(port, () => {
    console.log(`Example app listening on port ${port}`);
});