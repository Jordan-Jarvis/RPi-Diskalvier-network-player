CREATE TABLE Song (
	id serial,
	title TEXT NOT NULL,
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
    CONSTRAINT songBLOBID PRIMARY KEY (id),
    CONSTRAINT songID FOREIGN KEY (songID)
    REFERENCES Song(id)
);

CREATE TABLE songlist (
    id serial,
    listID int,
    songID int,
    CONSTRAINT songlistID PRIMARY KEY (id),
    CONSTRAINT songID FOREIGN KEY (ID)
    REFERENCES Song(ID)
)

INSERT INTO Song (title, rating, filelocation, BPM, len, numplays)
VALUES ('Bach', 3, 'dev/null', 120, 130.0029, 4),
  ('Bh', 3, 'dev/null', 120, 130.0029, 4),
  ('ach', 3, 'dev/null', 120, 130.0029, 4);

select * from Song;

INSERT INTO songlist (listID, songID)
VALUES (1, 19),(1,20);

select * from song s join songlist sl on s.id=sl.songid;