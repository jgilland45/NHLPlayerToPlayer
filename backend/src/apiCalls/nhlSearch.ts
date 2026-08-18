import type { PlayerInput, PlayerOutput } from '../models/players.ts';

import { normalizeText } from 'normalize-text';

const searchNHLPlayersByName = async (name: string): Promise<Array<PlayerOutput>> => {
    const trimmedName = name?.trim();

    if (!trimmedName) {
        return [];
    }

    const normalizedName = normalizeText(trimmedName);
    console.log(`Searching for NHL players with name: ${normalizedName}`);

    try {
        const response = await fetch(
            `https://search.d3.nhle.com/api/v1/search/player?culture=en-us&limit=20&q=${encodeURIComponent(normalizedName)}`,
        );

        if (!response.ok) {
            return [];
        }

        const data: Array<PlayerInput> = await response.json();

        console.log('Response from NHL API:', data);

        const players: Array<PlayerOutput> = (data || []).map((player) => ({
            playerId: player.playerId,
            name: player.name,
        }));

        return players;
    } catch {
        return [];
    }
};

export { searchNHLPlayersByName };