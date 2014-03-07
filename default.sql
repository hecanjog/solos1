-- Enables better support for concurrency.
-- See: https://www.sqlite.org/wal.html
PRAGMA journal_mode=WAL;

-- Config values loaded from pippi.json
create table config (
    name text primary key,
    value text
);

-- Currently running voices
create table voices (
    id integer primary key,
    loop bool,
    regenerate bool,
    target_volume real,
    post_volume real,
    once bool,
    uno bool,
    quantize bool,
    plays integer default 0,
    sections integer default 0,
    movements integer default 0,
    generator text
);

-- Params passed to voices
create table params (
    id integer primary key,
    name text,
    shortname text,
    input_type text,
    output_type text,
    value text,
    cooked text,
    voice_id integer,
    accepts text,
    instance_id integer
);

-- Valid param types for this session
-- Synced from types.json on init
create table types (
    id integer primary key,
    name text,
    shortname text,
    output_type text,
    accepts text
);

-- Available generators 
create table generators (
    id integer primary key,
    name text,
    shortname text
);

