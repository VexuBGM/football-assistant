PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS clubs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL COLLATE NOCASE UNIQUE,
  city TEXT NOT NULL,
  founded_year INTEGER
);

CREATE TABLE IF NOT EXISTS leagues (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL COLLATE NOCASE,
  season TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (name, season)
);

CREATE TABLE IF NOT EXISTS players (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  full_name TEXT NOT NULL COLLATE NOCASE,
  birth_date TEXT NOT NULL,
  nationality TEXT NOT NULL,
  position TEXT NOT NULL CHECK (position IN ('GK', 'DF', 'MF', 'FW')),
  number INTEGER NOT NULL CHECK (number BETWEEN 1 AND 99),
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'injured', 'suspended', 'retired')),
  club_id INTEGER,
  FOREIGN KEY (club_id) REFERENCES clubs(id) ON DELETE SET NULL,
  UNIQUE (club_id, number)
);

CREATE TABLE IF NOT EXISTS league_teams (
  league_id INTEGER NOT NULL,
  club_id INTEGER NOT NULL,
  joined_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (league_id, club_id),
  FOREIGN KEY (league_id) REFERENCES leagues(id) ON DELETE CASCADE,
  FOREIGN KEY (club_id) REFERENCES clubs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS matches (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  league_id INTEGER NOT NULL,
  round_no INTEGER NOT NULL CHECK (round_no > 0),
  home_club_id INTEGER NOT NULL,
  away_club_id INTEGER NOT NULL,
  match_date TEXT,
  home_goals INTEGER,
  away_goals INTEGER,
  status TEXT NOT NULL DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'played')),
  FOREIGN KEY (league_id) REFERENCES leagues(id) ON DELETE CASCADE,
  FOREIGN KEY (home_club_id) REFERENCES clubs(id),
  FOREIGN KEY (away_club_id) REFERENCES clubs(id),
  CHECK (home_club_id != away_club_id),
  UNIQUE (league_id, round_no, home_club_id, away_club_id)
);

CREATE TABLE IF NOT EXISTS goals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  match_id INTEGER NOT NULL,
  player_id INTEGER NOT NULL,
  club_id INTEGER NOT NULL,
  minute INTEGER NOT NULL CHECK (minute BETWEEN 1 AND 120),
  is_own_goal INTEGER NOT NULL DEFAULT 0 CHECK (is_own_goal IN (0, 1)),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE,
  FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE,
  FOREIGN KEY (club_id) REFERENCES clubs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cards (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  match_id INTEGER NOT NULL,
  player_id INTEGER NOT NULL,
  club_id INTEGER NOT NULL,
  minute INTEGER NOT NULL CHECK (minute BETWEEN 1 AND 120),
  card_type TEXT NOT NULL CHECK (card_type IN ('Y', 'R')),
  FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE,
  FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE,
  FOREIGN KEY (club_id) REFERENCES clubs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS transfers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  player_id INTEGER NOT NULL,
  from_club_id INTEGER,
  to_club_id INTEGER NOT NULL,
  transfer_date TEXT NOT NULL CHECK (
    length(transfer_date) = 10
    AND substr(transfer_date, 5, 1) = '-'
    AND substr(transfer_date, 8, 1) = '-'
  ),
  fee REAL CHECK (fee IS NULL OR fee >= 0),
  note TEXT,
  FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE,
  FOREIGN KEY (from_club_id) REFERENCES clubs(id) ON DELETE SET NULL,
  FOREIGN KEY (to_club_id) REFERENCES clubs(id) ON DELETE CASCADE,
  CHECK (from_club_id IS NULL OR from_club_id != to_club_id)
);

CREATE INDEX IF NOT EXISTS idx_players_club_id ON players(club_id);
CREATE INDEX IF NOT EXISTS idx_players_full_name ON players(full_name);
CREATE INDEX IF NOT EXISTS idx_leagues_name_season ON leagues(name, season);
CREATE INDEX IF NOT EXISTS idx_league_teams_club_id ON league_teams(club_id);
CREATE INDEX IF NOT EXISTS idx_matches_league_round ON matches(league_id, round_no);
CREATE INDEX IF NOT EXISTS idx_matches_home_club_id ON matches(home_club_id);
CREATE INDEX IF NOT EXISTS idx_matches_away_club_id ON matches(away_club_id);
CREATE INDEX IF NOT EXISTS idx_matches_status ON matches(status);
CREATE INDEX IF NOT EXISTS idx_goals_match_id ON goals(match_id);
CREATE INDEX IF NOT EXISTS idx_goals_player_id ON goals(player_id);
CREATE INDEX IF NOT EXISTS idx_cards_match_id ON cards(match_id);
CREATE INDEX IF NOT EXISTS idx_cards_player_id ON cards(player_id);
CREATE INDEX IF NOT EXISTS idx_transfers_player_id ON transfers(player_id);
CREATE INDEX IF NOT EXISTS idx_transfers_to_club_id ON transfers(to_club_id);
CREATE INDEX IF NOT EXISTS idx_transfers_date ON transfers(transfer_date);
