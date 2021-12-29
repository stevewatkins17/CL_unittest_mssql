# overview

unittest_mssql is a Python & TSQL unit testing tool.

Python implements the programming framework to execute the test.
TSQL implements the core test itself and returns Pass/Fail results.

# Getting started
The user must have Python installed to implement (although it can be compiled to a Windows or linux .exe to avoid that).

The user is required to provide two file inputs and a probable third. All file inputs are stored in the "/input_user" sub-dir.

## User Input 1 -- TSQL unit test script (single batch)
The script is run on the local DB to be tested against.

It outputs the following schema:

```
"i" string not null - the name of the MSSQL instance of the test target DB
"db" string not null - the name of the MSSQL DB of the test target
"ud_0" string or int isnullable - user definable; this value is returned to the Python caller and is written to the json results, but is not summed and is otherwise ignored.
"ud_1" string or int isnullable - user definable; this value is returned to the Python caller and is written to the json results, but is not summed and is otherwise ignored.
"ud_2" string or int isnullable - user definable; this value is returned to the Python caller and is written to the json results, but is not summed and is otherwise ignored.
"ud_3" string or int isnullable - user definable; this value is returned to the Python caller and is written to the json results, but is not summed and is otherwise ignored.
"PassFail" string isnullable - Result of test. Can be any value but only the following 4 values will be summed in the Results summary: ("Pass", "Fail", "NA", null)
```

## Input 2 -- unittest_configuration.json
At runtime, unittest_mssql.py starts by reading parameters from unittest_configuration.json, a key-value store.

WARNING - must use characters in the key-value that Python, the json parser and the runtime OS will accept. Keep it simple.

```
	{
		 "unit_test_batch_name" : "udf_GetAttachmentsList - XAI"
		,"unit_test_sql_file" : "unit test - udf_GetAttachmentsList.sql"
		,"dbs_list" : {
		  "XBISQL842":"TEMP_SEASONS_DNA"
		 ,"XAISQL841":"TEMP_ACCENTCARE_PHYSICIANS_QA"
		 ,"":"an empty key voids dbs_list"
		 }
		,"dbs_query_instance" : {
			 "i": "XAISQL841" 
			,"db": "master" 
			,"sql_file" : "db_catalog_instance_dbs.sql"
			}
		,"dbs_query_tier" : {
			 "i": "AGENCY-CONFIGURATION-INFO-LOU-HNA" 
			,"db": "Configuration"
			,"sql_file" : "db_catalog_configuration_db.sql"
			}     
	}
```

What each line means:

- "unit_test_batch_name" : the unique name of this test. Its also used to name the results output json file. 

- "unit_test_sql_file" : the SQL read-only batch script filename that performs the test. 
	o WARNING - do not put SSMS specific code/commands in the TSQL batch, like "GO" or ":connect XAISQL841"

- "dbs_list" : an explicit list of DBs to test against. When empty key exists ("":""), then entire list void. Can be empty strings (null).

- "dbs_query_instance" : a single MSSQL instance to test against. Can be empty strings (null). The DBs on the named instance, filtered by the query in file referenced in "sql_file"
	- "sql_file" : the file that stores the query that we run against the instance & DB stored in "dbs_query_instance" KVs. Can be empty strings (null).

- "dbs_query_tier" : a single user-definable MSSQL tier of instances and DBs to test against, filtered by the query in file referenced in "sql_file"
	- "sql_file" : the file that stores the query that we run against the Configuration DB stored in "dbs_query_tier" KVs.

### DB or instance or tier?
What gets used at runtime?

Although this could change, currently the Python logic uses a "narrowest scope wins" logic:
- if "dbs_list" is populated (and does not contain an empty key "":"v") then it is used and the others are ignored. 
- if "dbs_query_instance" is populated and "dbs_list" is not, then it is used and "dbs_query_tier" is ignored. 
- if "dbs_list" and "dbs_query_instance" values are empty, then we default to "dbs_query_tier"


# To run

unittest_mssql is executed at the Windows CMD line:
```
   /unittest_mssql>python unittest_mssql.py
```

# Outputs
unittest_mssql.py outputs 2 files:
- a runtime app log "app.log"
- a results json file as per this example:

```
	{
		"unit_test_batch_name": "udf_GetAttachmentsList - XBI",
		"timestamp_begin": "2021-10-14 21:13:25.517203-04:00",
		"timestamp_end": "2021-10-14 21:24:57.536177-04:00",
		"results_summary": {
			"pass": 62,
			"fail": 0,
			"na": 0,
			"null": 6
		},
		"results": {
			"XBISQL842.TEMP_AAYCT_SPARSETEST_DNA": [
				487,
				487,
				0,
				0,
				"Pass"
			],
			"XBISQL842.TEMP_ABSOLUTE_SPARSETEST_DNA": [
				921,
				921,
				0,
				0,
				"Pass"
			],
			"XBISQL842.TEMP_ADDUS_SPARSETEST_DNA": [
				946,
				946,
				0,
				0,
				"Pass"
			]
		}
	}
```

# best practices & resource warnings
To minimize imapact on the test targets:
- we do not install anything permanent or that requires deleting later -- tables, procedures etc 
- we keep our test narrowly focused, usually on a single logical query
- we ensure our test code is lean & efficient: its runtime against the largest customers should not exceed 60 seconds.
- our test should never stress the test target instance, thereforwe we only run single-threaded tests (one-DB-at-a-time)
- we avoid testing when the target system is active to avoid resource contention or re-testing caused by an inconsistent state.