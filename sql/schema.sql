CREATE TABLE IF NOT EXISTS Clubs (
  club_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  city TEXT NOT NULL,
  founded_year INTEGER
);

CREATE TABLE IF NOT EXISTS Players (
  player_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  age INTEGER NOT NULL,
  position TEXT NOT NULL,
  club_id INTEGER NOT NULL,
  FOREIGN KEY (club_id) REFERENCES Clubs(club_id)
);

CREATE TABLE IF NOT EXISTS Matches (
  match_id INTEGER PRIMARY KEY AUTOINCREMENT,
  home_club_id INTEGER NOT NULL,
  away_club_id INTEGER NOT NULL,
  match_date DATE NOT NULL,
  home_score INTEGER,
  away_score INTEGER,
  FOREIGN KEY (home_club_id) REFERENCES Clubs(club_id),
  FOREIGN KEY (away_club_id) REFERENCES Clubs(club_id)
);
