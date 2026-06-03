# Example Dialog — Stage 3 (Clubs + Players)

```
> add club Levski Sofia 1914
Added club: Levski (Sofia)

> add club CSKA Sofia 1948
Added club: CSKA (Sofia)

> list clubs
Clubs:
- [1] Levski — Sofia, founded 1914
- [2] CSKA — Sofia, founded 1948

> add player Georgi Petkov in Levski position GK number 1 born 1975-05-10 nat Bulgarian
Added player: Georgi Petkov - GK (#1) in Levski, born 1975-05-10, Bulgarian

> add player Stefan Velev in Levski position DF number 4 born 1998-03-22 nat Bulgarian
Added player: Stefan Velev - DF (#4) in Levski, born 1998-03-22, Bulgarian

> add player Gustavo Busatto in CSKA position FW number 9 born 1996-01-30 nat Brazilian
Added player: Gustavo Busatto - FW (#9) in CSKA, born 1996-01-30, Brazilian

> list players of Levski
Players of Levski:
  #1 Georgi Petkov - GK, Bulgarian, born 1975-05-10 (Levski)
  #4 Stefan Velev - DF, Bulgarian, born 1998-03-22 (Levski)

> list players of CSKA
Players of CSKA:
  #9 Gustavo Busatto - FW, Brazilian, born 1996-01-30 (CSKA)

> change number of Georgi Petkov to 13
Updated Georgi Petkov: number -> #13

> change status of Stefan Velev to injured
Updated Stefan Velev: status -> injured

> change position of Gustavo Busatto to MF
Updated Gustavo Busatto: position -> MF

> list players
All players:
  #9 Gustavo Busatto - MF, Brazilian, born 1996-01-30 (CSKA)
  #13 Georgi Petkov - GK, Bulgarian, born 1975-05-10 (Levski)
  #4 Stefan Velev - DF, Bulgarian, born 1998-03-22 [injured] (Levski)

> delete player Gustavo Busatto
Deleted player: Gustavo Busatto.

> list players of CSKA
No players in CSKA.

> help
Commands:
=== Clubs ===
- add club <name> <city> [year]
- list clubs
- delete club <name|id>
=== Players ===
- add player <name> in <club> position <GK|DF|MF|FW> number <1-99> born <date> nat <nationality>
- list players of <club>  /  list all players
- change number of <player> to <number>
- change position of <player> to <position>
- change status of <player> to <status>
- delete player <name|id>
- seed players
=== Other ===
- help
- exit

> exit
Goodbye!
```
