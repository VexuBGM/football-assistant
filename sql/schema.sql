CREATE TABLE IF NOT EXISTS Clubs (
  club_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  city TEXT NOT NULL,
  founded_year INTEGER
);

CREATE TABLE IF NOT EXISTS Players (
  player_id INTEGER PRIMARY KEY AUTOINCREMENT,
  full_name TEXT NOT NULL,
  birth_date TEXT NOT NULL,
  nationality TEXT NOT NULL,
  position TEXT NOT NULL CHECK(position IN ('GK','DF','MF','FW')),
  number INTEGER NOT NULL CHECK(number BETWEEN 1 AND 99),
  status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active','injured','suspended','retired')),
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
