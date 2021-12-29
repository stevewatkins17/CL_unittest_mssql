use master;
if not exists(select * from sys.syslogins where name = 'MyLogin')
begin
    CREATE LOGIN MyLogin WITH PASSWORD = '';
end

if not exists(select 1 from sys.databases where name = 'MyDatabase')
begin
    create database MyDatabase;
end
