use MyDatabase;

if not exists(SELECT 1 FROM sys.database_principals dp where dp.[name] = 'MyUser')
begin
    CREATE USER MyUser FOR LOGIN MyLogin;
end


if exists(SELECT 1 FROM sys.database_principals dp where dp.[name] = 'MyUser')
begin
    ALTER ROLE db_owner ADD MEMBER MyUser;  
end




