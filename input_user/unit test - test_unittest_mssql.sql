/* 
docker run -e "ACCEPT_EULA=Y" -e "SA_PASSWORD=MyP@ssword1" -p 1433:1433 -d mcr.microsoft.com/mssql/server:2019-latest 
*/

set nocount on;
set transaction isolation level read uncommitted;

declare @ocount int = (select count(*) from sys.databases d where d.[name] in('msdb' ,'tempdb'));
declare @test_limit int = 1000;

if @ocount = 2
begin  
	begin /* Step 0 -- test 0 -- we run the legacy code */ */

		drop table if exists #ca_0;

		select [mycount] = convert(int ,count(*)) into #ca_0 from sys.databases d;

	end

	begin /* Step 1 -- test 1 -- we run the new code that will replace the legacy code  */
		declare @mycount int = (select count(*) from sys.databases d);

		drop table if exists #ca_1;

		create table #ca_1([mycount] int);

		insert into #ca_1([mycount]) values(@mycount);

	end

	begin /* Step 2 -- Pass-Fail Results -- we compare output results from the old code to the new & vice versa; returning delta counts */

		declare @countdelta int ,@delta0 int ,@delta1 int ,@IA0count int ,@IA1count int; 

		with cte as(
			select 
			 [IA0 count] = (select count(*) from #ca_0)
			,[IA1 count] = (select count(*) from #ca_1)
		)
		select 
			 @IA0count = c.[IA0 count]
			,@IA1count = c.[IA1 count]
			,@countdelta = (c.[IA0 count] - c.[IA1 count])
		from cte c; 

		with cte as(
			select * from #ca_0
			except
			select * from #ca_1
		)
		select @delta0 = count(*) from cte c;


		with cte as(
			select * from #ca_1
			except
			select * from #ca_0
		)
		select @delta1 = count(*) from cte c;

		/* return test results to caller */

       select 
             [i] = @@servername
            ,[db] = db_name() 
            ,[ud_0] = @IA0count
            ,[ud_1] = @IA1count
            ,[ud_2] = @delta0
            ,[ud_3] = @delta1
			,[PassFail] = case 
				when @IA0count = 0 and @IA1count = 0 then 'NA' 
				when (@IA0count - @IA1count = 0) and (@delta0 + @delta1 = 0) then 'Pass' 
				else 'Fail' end;


	end
end
else
    begin
        select 
             [i] = @@servername
            ,[db] = db_name() 
            ,[ud_0] = null
            ,[ud_1] = null
            ,[ud_2] = null
            ,[ud_3] = null
			,[PassFail] = null
    end    


