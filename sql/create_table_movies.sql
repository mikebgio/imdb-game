create table movies
(
    id       integer      not null
        constraint id primary key,
    title    varchar(128) not null,
    year     integer,
    director varchar(88),
    constraint title_year
        unique (title, year)
);

alter table movies
    owner to mgiordano;

