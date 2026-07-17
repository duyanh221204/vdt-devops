create table users (
    id serial primary key,
    username varchar(20) not null,
    hashed_password varchar(255) not null,
    role varchar(20) not null
);

create table students (
    id serial primary key,
    name varchar(100) not null,
    year_of_birth integer not null
);

insert into students (name, year_of_birth) values ('Nguyễn Duy Anh', 2004);
insert into students (name, year_of_birth) values ('Nguyễn Trí Dũng', 2004);
insert into students (name, year_of_birth) values ('Đỗ Sơn Tùng', 2004);
insert into students (name, year_of_birth) values ('Nguyễn Thế Thịnh', 2004);
insert into students (name, year_of_birth) values ('Đỗ Đàm Quân', 2004);
insert into students (name, year_of_birth) values ('Nguyễn Tự Kiên', 2005);