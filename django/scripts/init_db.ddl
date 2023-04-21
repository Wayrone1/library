CREATE SCHEMA IF NOT EXISTS library;

CREATE EXTENSION "uuid-ossp";

CREATE TABLE IF NOT EXISTS library.book (id uuid primary key default uuid_generate_v4(), title TEXT NOT NULL, description TEXT, volume integer, age_limit integer, year INT, type TEXT NOT NULL, created timestamp with time zone default CURRENT_TIMESTAMP, modified timestamp with time zone default CURRENT_TIMESTAMP);

SET search_path TO public,library;

INSERT INTO library.book (title, type, year) SELECT 'some book name', case when RANDOM() < 0.3 THEN 'journal' ELSE 'book' END, generate_series(0, 2023);

CREATE INDEX book_creation_date_idx ON library.book(year);

CREATE TABLE IF NOT EXISTS library.author (id uuid primary key default uuid_generate_v4(), full_name text not null, created timestamp with time zone default CURRENT_TIMESTAMP, modified timestamp with time zone default CURRENT_TIMESTAMP);

CREATE INDEX author_full_name_idx ON library.author(full_name);

CREATE TABLE IF NOT EXISTS library.book_author (id uuid primary key default uuid_generate_v4(), book_id uuid not null references library.book, author_id uuid not null references library.author, created timestamp with time zone default CURRENT_TIMESTAMP);

CREATE UNIQUE INDEX book_author_idx ON library.book_author (book_id, author_id);

CREATE TABLE IF NOT EXISTS library.genre (id uuid primary key default uuid_generate_v4(), name text not null, description text, created timestamp with time zone default CURRENT_TIMESTAMP, modified timestamp with time zone default CURRENT_TIMESTAMP);

CREATE TABLE IF NOT EXISTS library.book_genre (id uuid primary key default uuid_generate_v4(), book_id uuid not null references library.book, genre_id uuid not null references library.genre, created timestamp with time zone default CURRENT_TIMESTAMP);

CREATE UNIQUE INDEX book_genre_idx ON library.book_genre (book_id, genre_id);