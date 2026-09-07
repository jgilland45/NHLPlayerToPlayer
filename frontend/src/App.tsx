import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import heroImg from './assets/hero.png'
import './App.css'

import type { Player } from './models/players.ts'

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const [playerId, setPlayerId] = useState('');
  const [players, setPlayers] = useState<Array<Player>>([]);

  const searchTeammates = async (id: string) => {
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:3000/api/getTeammatesOfPlayer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ playerId: id })
      });

      if (!response.ok) {
        throw new Error('The backend could not process the player search.');
      }

      const data: Array<Player> = await response.json();
      console.log('Players found:', data);
      setPlayers(data);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Something went wrong.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <section id="center">
        <div className="hero">
          <img src={heroImg} className="base" width="170" height="179" alt="" />
          <img src={reactLogo} className="framework" alt="React logo" />
          <img src={viteLogo} className="vite" alt="Vite logo" />
        </div>
        <div>
          <h1>Get started</h1>
          <p>
            Edit <code>src/App.tsx</code> and save to test <code>HMR</code>
          </p>
        </div>
        <input
          type="number"
          value={playerId}
          onChange={(e) => setPlayerId(e.target.value)}
          placeholder="Enter player id"
          aria-disabled={isLoading ? 'true' : 'false'}
        />
        <button onClick={() => searchTeammates(playerId)} disabled={isLoading}>
          {isLoading ? 'Searching...' : 'Search Teammates'}
        </button>
        <h2>Teammates of Player ID: {playerId}</h2>
        <p>Results:</p>
        <p>{players.length} players found.</p>

        <ul>
          {players.map((player) => (
            <li key={player.playerId}>{player.playerId}: {player.name}</li>
          ))}
        </ul>
        {error && <p role="alert">{error}</p>}
      </section>
    </>
  )
}

export default App
