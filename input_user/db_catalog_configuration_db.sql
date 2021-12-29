select 
   [i] = di.[DatabaseInstanceName] 
  ,[db] = s.[DatabaseName]
from [Configuration].[dbo].[sqlDatabase] s
join [Configuration].[dbo].[DatabaseInstance] AS di on di.DatabaseInstanceID = s.DatabaseInstanceID
  and exists(select 1 from [Configuration].[dbo].[DatabaseInstanceType] dit where dit.[DatabaseInstanceTypeID] = 'S' and dit.[DatabaseInstanceTypeID] = di.[DatabaseInstanceTypeID])
join [Configuration].[dbo].[DatabaseHandle] AS h on h.DatabaseID = s.DatabaseID
join [Configuration].[dbo].[Application] a on a.ApplicationID = h.ApplicationID
  and a.[ApplicationID] = 17
join [Configuration].[dbo].[Server] AS se ON se.ServerID = di.ServerID
join [Configuration].[dbo].[DataCenter] AS dc on dc.DataCenterID = se.DataCenterID 
join [Configuration].[dbo].[ReleaseTier] AS rt ON rt.ReleaseTierID = h.ReleaseTierID
  and rt.[ReleaseTier] = 'Development'
join [Configuration].[dbo].[Owner] o on h.OwnerID = o.OwnerID
join [Configuration].[dbo].[DataLevel] dl on h.DataLevelID = dl.DataLevelID
order by newid();