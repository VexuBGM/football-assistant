PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS clubs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL COLLATE NOCASE UNIQUE,
  city TEXT NOT NULL,
  founded_year INTEGER
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

CREATE TABLE IF NOT EXISTS matches (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  home_club_id INTEGER NOT NULL,
  away_club_id INTEGER NOT NULL,
  match_date TEXT NOT NULL,
  home_score INTEGER,
  away_score INTEGER,
  FOREIGN KEY (home_club_id) REFERENCES clubs(id),
  FOREIGN KEY (away_club_id) REFERENCES clubs(id)
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
CREATE INDEX IF NOT EXISTS idx_transfers_player_id ON transfers(player_id);
CREATE INDEX IF NOT EXISTS idx_transfers_to_club_id ON transfers(to_club_id);
CREATE INDEX IF NOT EXISTS idx_transfers_date ON transfers(transfer_date);
