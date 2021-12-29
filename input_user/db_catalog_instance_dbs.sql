select
	 [i] = @@SERVERNAME
	,[db] = di.Name
from [master].[sys].[databases] di
where /* left(di.[name],5) = 'TEMP_'
and */ di.[state] = 0 
and di.[user_access] = 0
and di.[is_cleanly_shutdown] = 0
and di.[is_in_standby] = 0
and di.[is_read_only] = 0
order by newid();
