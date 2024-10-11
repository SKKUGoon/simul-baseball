-- Create the 'teams' table
CREATE TABLE baseball.teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    statiz_id INTEGER UNIQUE
);

-- Create the 'players' table
CREATE TABLE baseball.players (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    statiz_id INTEGER UNIQUE
);

-- Create the 'player_roles' table
CREATE TABLE baseball.player_roles (
    player_id INTEGER NOT NULL,
    role VARCHAR(20) NOT NULL,
    PRIMARY KEY (player_id, role),
    FOREIGN KEY (player_id) REFERENCES baseball.players(id) ON DELETE CASCADE
);

-- Create the 'player_stats' table
CREATE TABLE baseball.player_stats (
    id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL,
    season DATE NOT NULL,
    role VARCHAR(20) NOT NULL,
    games_played INTEGER DEFAULT 0,
    at_bats INTEGER DEFAULT 0,
    hits INTEGER DEFAULT 0,
    doubles INTEGER DEFAULT 0,
    triples INTEGER DEFAULT 0,
    home_runs INTEGER DEFAULT 0,
    runs_batted_in INTEGER DEFAULT 0,
    walks INTEGER DEFAULT 0,
    strikeouts INTEGER DEFAULT 0,
    batting_average DECIMAL(4,3) DEFAULT 0.000,
    whip DECIMAL(4,2) DEFAULT 0.00,
    era DECIMAL(4,2) DEFAULT 0.00,
    FOREIGN KEY (player_id) REFERENCES baseball.players(id) ON DELETE CASCADE
);

-- Create the 'games' table
CREATE TABLE baseball.games (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    home_team_id INTEGER NOT NULL,
    away_team_id INTEGER NOT NULL,
    home_score INTEGER DEFAULT 0,
    away_score INTEGER DEFAULT 0,
    venue VARCHAR(100),
    FOREIGN KEY (home_team_id) REFERENCES baseball.teams(id),
    FOREIGN KEY (away_team_id) REFERENCES baseball.teams(id)
);

-- Create the 'lineups' table
CREATE TABLE baseball.lineups (
    id SERIAL PRIMARY KEY,
    game_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    batting_order INTEGER,
    position VARCHAR(10),
    is_starting BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (game_id) REFERENCES baseball.games(id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES baseball.teams(id),
    FOREIGN KEY (player_id) REFERENCES baseball.players(id)
);

-- Create the 'game_events' table
CREATE TABLE baseball.game_events (
    id SERIAL PRIMARY KEY,
    game_id INTEGER NOT NULL,
    inning INTEGER NOT NULL,
    event_number INTEGER NOT NULL,
    pitcher_id INTEGER NOT NULL,
    batter_id INTEGER NOT NULL,
    pitch_type VARCHAR(20),
    pitch_speed DECIMAL(4,1),
    result VARCHAR(50),
    previous_LEV DECIMAL(5,2),
    REs DECIMAL(5,2),
    REa DECIMAL(5,2),
    WPe DECIMAL(5,2),
    WPa DECIMAL(5,2),
    FOREIGN KEY (game_id) REFERENCES baseball.games(id) ON DELETE CASCADE,
    FOREIGN KEY (pitcher_id) REFERENCES baseball.players(id),
    FOREIGN KEY (batter_id) REFERENCES baseball.players(id)
);

-- Create the 'game_conditions' table
CREATE TABLE baseball.game_conditions (
    game_id INTEGER PRIMARY KEY,
    weather VARCHAR(50),
    temperature DECIMAL(4,1),
    humidity DECIMAL(4,1),
    wind_speed DECIMAL(4,1),
    FOREIGN KEY (game_id) REFERENCES baseball.games(id) ON DELETE CASCADE
);

-- Indexes to optimize query performance
CREATE INDEX idx_player_stats_player_season ON player_stats(player_id, season);
CREATE INDEX idx_lineups_game_team ON lineups(game_id, team_id);
CREATE INDEX idx_game_events_game_inning_event ON game_events(game_id, inning, event_number);

-- Constraints for data integrity
ALTER TABLE baseball.player_stats
ADD CONSTRAINT chk_role CHECK (role IN ('batter', 'pitcher', 'both'));

ALTER TABLE baseball.lineups
ADD CONSTRAINT chk_batting_order CHECK (batting_order BETWEEN 1 AND 9);

ALTER TABLE baseball.game_events
ADD CONSTRAINT chk_inning CHECK (inning >= 1);