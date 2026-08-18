import express, { type Express, type Request, type Response } from 'express';
import cors from 'cors';

const app: Express = express();
const port = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

app.get('/', (req: Request, res: Response) => {
    res.send('Hello World!');
});

app.post('/api/data', (req: Request, res: Response) => {
    const { count } = req.body;

    if (typeof count !== 'number' || !Number.isFinite(count)) {
        res.status(400).json({ error: 'count must be a finite number' });
        return;
    }

    const randNumChanger = Math.random() * 10;
    const randOpertor = Math.random() < 0.5 ? -1 : 1;
    const newCount = count + randNumChanger * randOpertor;
    res.json({ newCount });
});

app.listen(port, () => {
    console.log(`Example app listening on port ${port}`);
});