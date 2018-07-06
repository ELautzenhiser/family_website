DROP TABLE IF EXISTS People;
CREATE TABLE People (
person_id INTEGER PRIMARY KEY AUTOINCREMENT,
first_name TEXT NOT NULL,
middle_name TEXT,
last_name TEXT NOT NULL,
maiden_name TEXT,
gender TEXT,
birth_year INTEGER,
birth_month INTEGER,
birth_day INTEGER,
city TEXT,
state TEXT,
mother_id INTEGER,
father_id INTEGER,
FOREIGN KEY (mother_id) REFERENCES People (person_id),
FOREIGN KEY (father_id) REFERENCES People (person_id)
);

DROP TABLE IF EXISTS Marriages;
CREATE TABLE Marriages (
spouse1 INTEGER NOT NULL,
spouse2 INTEGER NOT NULL,
start_year INTEGER,
start_month INTEGER,
start_day INTEGER,
end_year INTEGER,
end_month INTEGER,
end_day INTEGER,
PRIMARY KEY (spouse1,spouse2)
);

DROP TABLE IF EXISTS Memoirs;
CREATE TABLE Memoirs (
memoir_id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT NOT NULL,
author_id INTEGER NOT NULL,
year_written INTEGER,
subject TEXT,
filename TEXT,
FOREIGN KEY (author_id) REFERENCES People (person_id)
);

DROP TABLE IF EXISTS Memoir_tags;
CREATE TABLE Memoir_tags (
memoir_id INTEGER NOT NULL,
person_id INTEGER NOT NULL,
PRIMARY KEY (memoir_id, person_id),
FOREIGN KEY (memoir_id) REFERENCES Memoirs (memoir_id),
FOREIGN KEY (person_id) REFERENCES People (person_id)
);