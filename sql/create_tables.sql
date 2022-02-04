CREATE TABLE Song (
	id serial,
	title  TEXT NOT NULL UNIQUE,
	rating INT DEFAULT '4',
	filelocation TEXT NOT NULL,
	BPM INT,
	len FLOAT,
	numplays INT,
    CONSTRAINT songID PRIMARY KEY (id)
);

CREATE TABLE songBLOB (
    id serial,
    songID INT,
    songBLOB bytea,
    CONSTRAINT songBLOBID PRIMARY KEY (id),
    CONSTRAINT songID FOREIGN KEY (songID)
    REFERENCES Song(id)
);



CREATE TABLE playlist (
   id serial,
   title TEXT NOT NULL,
   folderLocation TEXT NOT NULL,
   listID int,
   CONSTRAINT playlistID PRIMARY KEY (id)
  );
  
CREATE TABLE songlist (
    id serial,
    listID int,
    songID int,
    CONSTRAINT songlistID PRIMARY KEY (id),
    CONSTRAINT songID FOREIGN KEY (id)
    REFERENCES Song(ID),
    CONSTRAINT songlist FOREIGN KEY (listID)
    REFERENCES playlist(id)
);



-- insert sample data
INSERT INTO Song (title, rating, filelocation, BPM, len, numplays)
VALUES ('Bach', 3, 'dev/null', 120, 130.0029, 4),
  ('Bh', 3, 'dev/null', 120, 130.0029, 4),
  ('ach', 3, 'dev/null', 120, 130.0029, 4);

select * from Song;

-- sample playlist
INSERT INTO playlist (title, folderLocation, listID)
Values ('hello','dev/null',1);

-- sample songlist
INSERT INTO songlist (listID, songID)
VALUES (1, 1),(1,2);

-- uppdate value in DB
update song set len=5 where song.numplays=4;

-- get songs in playlist
select s.title, s.rating from playlist as p join songlist as sl on p.listID=sl.listid join song s on sl.songid=s.id; 

