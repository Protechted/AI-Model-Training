-- SCHEMA Name public

-- Create Table for storing the metadata

-- Table: public.samples

-- DROP TABLE IF EXISTS public.samples;

CREATE TABLE IF NOT EXISTS public.samples
(
    sample_id integer NOT NULL DEFAULT nextval('samples_sample_id_seq'::regclass),
    subject text COLLATE pg_catalog."default" NOT NULL,
    label text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT samples_pkey PRIMARY KEY (sample_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.samples
    OWNER to postgres;


-- Create Data Table where the actual data is stored
-- Table: public.data

-- DROP TABLE IF EXISTS public.data;

CREATE TABLE IF NOT EXISTS public.data
(
    datapoint_id integer NOT NULL DEFAULT nextval('data_id_seq'::regclass),
    ax real NOT NULL,
    ay real NOT NULL,
    az real NOT NULL,
    gx real NOT NULL,
    gy real NOT NULL,
    gz real NOT NULL,
    qx real NOT NULL,
    qy real NOT NULL,
    qz real NOT NULL,
    qw real NOT NULL,
    p real NOT NULL,
    sample_id integer NOT NULL,
    CONSTRAINT data_pkey PRIMARY KEY (datapoint_id),
    CONSTRAINT sample_id FOREIGN KEY (sample_id)
        REFERENCES public.samples (sample_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.data
    OWNER to postgres;
    
    
