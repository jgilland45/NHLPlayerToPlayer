-- Run with psql as a PostgreSQL administrator, for example:
-- psql -U postgres -f database/postgres/001_create_schema.sql

SELECT format('CREATE DATABASE %I OWNER %I', 'nhlptphockeydata', 'postgres')
WHERE NOT EXISTS (
    SELECT FROM pg_database WHERE datname = 'nhlptphockeydata'
)\gexec

\connect nhlptphockeydata

CREATE TABLE IF NOT EXISTS teams (
    team_id integer PRIMARY KEY,
    abbreviation text,
    name text,
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS players (
    player_id integer PRIMARY KEY,
    name text NOT NULL,
    position_code text,
    active boolean NOT NULL DEFAULT false,
    height text,
    height_in_inches smallint,
    height_in_centimeters smallint,
    weight_in_pounds smallint,
    weight_in_kilograms smallint,
    birth_city text,
    birth_state_province text,
    birth_country text,
    current_team_id integer REFERENCES teams(team_id),
    current_team_abbreviation text,
    last_team_id integer REFERENCES teams(team_id),
    last_team_abbreviation text,
    last_season_id integer,
    sweater_number smallint,
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS games (
    game_id bigint PRIMARY KEY,
    season integer NOT NULL,
    game_type smallint NOT NULL,
    eastern_start_time timestamptz,
    game_date date,
    game_number integer,
    game_schedule_state_id integer,
    game_state_id integer,
    home_score smallint,
    home_team_id integer REFERENCES teams(team_id),
    visiting_score smallint,
    visiting_team_id integer REFERENCES teams(team_id),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT games_game_type_valid CHECK (game_type > 0)
);

-- One row records that a player appeared for a team in a game. This is the
-- relational source for building teammate relationships later.
CREATE TABLE IF NOT EXISTS game_players (
    game_id bigint NOT NULL REFERENCES games(game_id) ON DELETE CASCADE,
    player_id integer NOT NULL REFERENCES players(player_id) ON DELETE CASCADE,
    season integer NOT NULL,
    game_type smallint NOT NULL,
    team_id integer REFERENCES teams(team_id),
    PRIMARY KEY (game_id, player_id)
);

CREATE INDEX IF NOT EXISTS game_players_player_id_idx
    ON game_players (player_id);

CREATE INDEX IF NOT EXISTS game_players_team_game_idx
    ON game_players (team_id, game_id);

CREATE INDEX IF NOT EXISTS games_season_game_type_idx
    ON games (season, game_type);