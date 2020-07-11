DROP TABLE IF EXISTS Photo_tags;
DROP TABLE IF EXISTS Photos;
DROP TABLE IF EXISTS Memoir_tags;
DROP TABLE IF EXISTS Memoirs;
DROP TABLE IF EXISTS Marriages;
DROP TABLE IF EXISTS People;

CREATE TABLE People (
person_id INT PRIMARY KEY AUTO_INCREMENT,
first_name VARCHAR(32) NOT NULL,
middle_name VARCHAR(32),
last_name VARCHAR(32) NOT NULL,
maiden_name VARCHAR(32),
preferred_name VARCHAR(32),
gender VARCHAR(32),
birth_year INT,
birth_month INT,
birth_day INT,
death_year INT,
death_month INT,
death_day INT,
city VARCHAR(32),
state VARCHAR(32),
mother_id INT,
father_id INT,
blurb_file VARCHAR(155),
FOREIGN KEY (mother_id) REFERENCES People (person_id),
FOREIGN KEY (father_id) REFERENCES People (person_id)
);

CREATE TABLE Marriages (
spouse1 INT NOT NULL,
spouse2 INT NOT NULL,
start_year INT,
start_month INT,
start_day INT,
end_year INT,
end_month INT,
end_day INT,
PRIMARY KEY (spouse1,spouse2)
);

CREATE TABLE Memoirs (
memoir_id INT PRIMARY KEY AUTO_INCREMENT,
title VARCHAR(32) NOT NULL,
author_id INT NOT NULL,
year_written INT,
subject VARCHAR(32),
filename VARCHAR(155),
FOREIGN KEY (author_id) REFERENCES People (person_id)
);

CREATE TABLE Memoir_tags (
memoir_id INT NOT NULL,
person_id INT NOT NULL,
PRIMARY KEY (memoir_id, person_id),
FOREIGN KEY (memoir_id) REFERENCES Memoirs (memoir_id),
FOREIGN KEY (person_id) REFERENCES People (person_id)
);

CREATE TABLE Photos (
photo_id INT PRIMARY KEY AUTO_INCREMENT,
filename VARCHAR(155) NOT NULL,
description VARCHAR(155)
);

CREATE TABLE Photo_tags (
photo_id INT NOT NULL,
person_id INT NOT NULL,
PRIMARY KEY (photo_id, person_id),
FOREIGN KEY (photo_id) REFERENCES Photos (photo_id),
FOREIGN KEY (person_id) REFERENCES People (person_id)
);