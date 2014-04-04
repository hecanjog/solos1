PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE config (
    name text primary key,
    value text
);
INSERT INTO "config" VALUES('name','solo1');
INSERT INTO "config" VALUES('root','b');
INSERT INTO "config" VALUES('bpm','80.0');
INSERT INTO "config" VALUES('snapshots','snapshots/');
INSERT INTO "config" VALUES('a0','27.5');
INSERT INTO "config" VALUES('session','pippi.session');
INSERT INTO "config" VALUES('device','T6_pair1');
INSERT INTO "config" VALUES('shortname','rot');
INSERT INTO "config" VALUES('sounds','sounds/');
INSERT INTO "config" VALUES('quality','major');
INSERT INTO "config" VALUES('orc','orc/');
INSERT INTO "config" VALUES('tune','terry');
CREATE TABLE shared (
    name text primary key,
    value text
);
CREATE TABLE voices (
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
CREATE TABLE params (
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
CREATE TABLE types (
    id integer primary key,
    name text,
    shortname text,
    output_type text,
    accepts text
);
INSERT INTO "types" VALUES(1,'bend','be',NULL,NULL);
INSERT INTO "types" VALUES(2,'bpm','bpm','float','["float", "integer"]');
INSERT INTO "types" VALUES(3,'generator','generator','string','["alphanumeric"]');
INSERT INTO "types" VALUES(4,'tweet','tw',NULL,NULL);
INSERT INTO "types" VALUES(5,'trigger_id','tt','integer','["integer"]');
INSERT INTO "types" VALUES(6,'sample_index','si','integer','["integer"]');
INSERT INTO "types" VALUES(7,'regenerate','re',NULL,NULL);
INSERT INTO "types" VALUES(8,'hertz','hz','hz-list','["hz-list"]');
INSERT INTO "types" VALUES(9,'waveform','wf','string','["alphanumeric"]');
INSERT INTO "types" VALUES(10,'buffer_index','bi','integer','["integer"]');
INSERT INTO "types" VALUES(11,'buffer_length','bt','frame','["beat", "second", "millisecond", "integer"]');
INSERT INTO "types" VALUES(12,'device','device','string','["alphanumeric"]');
INSERT INTO "types" VALUES(13,'quantize','qu',NULL,NULL);
INSERT INTO "types" VALUES(14,'alias','a',NULL,NULL);
INSERT INTO "types" VALUES(15,'envelope','e','string','["alphanumeric"]');
INSERT INTO "types" VALUES(16,'drum','d','string-list','["string-list"]');
INSERT INTO "types" VALUES(17,'instrument','i','string','["alphanumeric"]');
INSERT INTO "types" VALUES(18,'harmonic','h','integer-list','["integer-list"]');
INSERT INTO "types" VALUES(19,'speed','sp','float','["float", "integer"]');
INSERT INTO "types" VALUES(20,'multiple','m','integer','["integer"]');
INSERT INTO "types" VALUES(21,'octave','o','integer','["integer", "float"]');
INSERT INTO "types" VALUES(22,'note','n','note-list','["note-list"]');
INSERT INTO "types" VALUES(23,'padding','p','frame','["beat", "second", "millisecond", "integer"]');
INSERT INTO "types" VALUES(24,'scale','s','integer-list','["integer-list"]');
INSERT INTO "types" VALUES(25,'repeats','r','integer','["integer"]');
INSERT INTO "types" VALUES(26,'length','t','frame','["beat", "second", "millisecond", "integer"]');
INSERT INTO "types" VALUES(27,'width','w','frame','["integer", "beat", "millisecond", "second"]');
INSERT INTO "types" VALUES(28,'volume','v','float','["integer", "float"]');
CREATE TABLE generators (
    id integer primary key,
    name text,
    shortname text
);
COMMIT;
