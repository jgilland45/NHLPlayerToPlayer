import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import heroImg from './assets/hero.png'
import './App.css'

import type { Player } from './models/players.ts'

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const [playerName, setPlayerName] = useState('');
  const [players, setPlayers] = useState<Array<Player>>([]);

  const searchPlayers = async (name: string) => {
    setPlayerName(name);
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:3000/api/searchPlayers', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ playerName: name })
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
          type="text"
          value={playerName}
          onChange={(e) => searchPlayers(e.target.value)}
          placeholder="Enter player name"
          aria-disabled={isLoading ? 'true' : 'false'}
        />

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
