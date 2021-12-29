import json
import collections
import pyodbc
import pytz
import datetime
import logging
import logging.handlers

log_file = 'output_process/app.log'
logger = logging.getLogger(log_file)
logger.setLevel(logging.INFO)

log_format_file = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s')
handler_file = logging.handlers.RotatingFileHandler(log_file, maxBytes=1073741824, backupCount=1)
handler_file.setFormatter(log_format_file)
logger.addHandler(handler_file)

log_format_console = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler_console = logging.StreamHandler()
handler_console.setLevel(logging.INFO)
handler_console.setFormatter(log_format_console)
logger.addHandler(handler_console)

log = logging.getLogger('output_process/app.log')

def create_json_from_dict(mydict ,myfilepathname):
    try:
        with open(myfilepathname, "w+") as fileToSave: 
            json.dump(mydict, fileToSave, ensure_ascii=True, indent=4, sort_keys=False)
            return 0
    except:
        return 1

def convert_json_to_dict(myfilepathname):
    """Parse 'workbook_release.config' to retrieve and return runtime params"""  
    try:
        with open(myfilepathname, "r") as read_file:
            my_new_dict =  dict(json.load(read_file))
            log.info(f"'myfilepathname':'{myfilepathname}'")
            
    except:
        my_new_dict = {}
        log.error(f"'myfilepathname':'{myfilepathname}'", exc_info=True)
    
    return my_new_dict

def get_MSSQL_connection(mssql_instance ,mssql_DB):
    """MSSQL connection with retry and timeout management"""
    retry ,wait ,cn_timeout ,qry_timeout = 3 ,30 ,30 ,0
    for _ in range(retry):
        try:
            cn = pyodbc.connect(
                "DRIVER={ODBC Driver 13 for SQL Server};"
                f"SERVER={mssql_instance};"
                f"DATABASE={mssql_DB};"
                "trusted_connection=Yes;"
                "APP=HCHB_Tableau_Sync;"
                ,timeout=cn_timeout)
            cn.timeout = qry_timeout
        except:
            log.warning(f"Failed to connect to [{mssql_instance}].[{mssql_DB}]", exc_info=True)
            time.sleep(wait)
            continue
        else:
            return cn
    else:
        log.warning(f"After {retry} Retry attempts, failed to connect to [{mssql_instance}].[{mssql_DB}]")

def get_MSSQL_test_targets(unittest_configuration):
    test_targets = []

    if 1==0:
        pass

    else:
        if len(unittest_configuration["dbs_query_instance"]["i"]) + len(unittest_configuration["dbs_query_instance"]["db"]) > 1:
            catalog_i ,catalog_db ,get_dbs_query_file = unittest_configuration["dbs_query_instance"]["i"] ,unittest_configuration["dbs_query_instance"]["db"] ,unittest_configuration["dbs_query_instance"]["sql_file"]
        else:
            catalog_i ,catalog_db ,get_dbs_query_file = unittest_configuration["dbs_query_tier"]["i"] ,unittest_configuration["dbs_query_tier"]["db"] ,unittest_configuration["dbs_query_tier"]["sql_file"]

        get_dbs_query_file = "input_user/" + get_dbs_query_file 
        log.info(f"'catalog_i':'{catalog_i}' ,'catalog_db':'{catalog_db}' ,'get_dbs_query_file':'{get_dbs_query_file}' ")

        with open(get_dbs_query_file, encoding="utf8") as f:
            mssql_query = f.read()

        cn = get_MSSQL_connection(catalog_i ,catalog_db)
        cursor = cn.cursor()
        results = cursor.execute(mssql_query)

        for row in results:
            test_targets.append((row.i ,row.db))

        cursor.close()
        cn.close()

    return test_targets

def run_unittest(MSSQL_test_targets ,unit_test_batch_name ,unit_test_sql_file):
    timestamp_b = str(pytz.utc.localize(datetime.datetime.utcnow()).astimezone(pytz.timezone("America/Louisville")))
    test_results = {"unit_test_batch_name": unit_test_batch_name ,"timestamp_begin": timestamp_b}
    detail_results = {}
    results_summary = {"pass":0 ,"fail":0 ,"na":0 ,"null":0}
    unit_test_sql_file = "input_user/" + unit_test_sql_file

    with open(unit_test_sql_file, encoding="utf8") as f:
        unittest_query = f.read()

    for catalog_i ,catalog_db in MSSQL_test_targets:
        log.info(f"'target':'{catalog_i}.{catalog_db}'")

        try:
            cn = get_MSSQL_connection(catalog_i ,catalog_db)
            cursor = cn.cursor()
            
            results = cursor.execute(unittest_query)

            for row in results:
                detail_results[row.i +"."+ row.db] = (row.ud_0 ,row.ud_1 ,row.ud_2 ,row.ud_3 ,row.PassFail)

                if row.PassFail is not None:
                    if row.PassFail.upper() == "PASS":
                        results_summary["pass"] += 1 
                    if row.PassFail.upper() == "FAIL":
                        results_summary["fail"] += 1 
                    if row.PassFail.upper() == "NA":
                        results_summary["na"] += 1 
                else:
                    results_summary["null"] += 1

            cursor.close()
            cn.close()
        
        except:
            log.error(f"'target':'{catalog_i}.{catalog_db}'", exc_info=True)
            results_summary["null"] += 1
            cursor.close()
            cn.close()

    log.info(f"'results_summary':'(pass:{results_summary['pass']} ,fail:{results_summary['fail']} ,na:{results_summary['na']} ,null:{results_summary['null']})'")

    test_results["timestamp_end"] = str(pytz.utc.localize(datetime.datetime.utcnow()).astimezone(pytz.timezone("America/Louisville")))
    test_results["results_summary"] = results_summary
    test_results["results"] = collections.OrderedDict(sorted(detail_results.items()))

    return test_results

def main():
    timestamp_b = pytz.utc.localize(datetime.datetime.utcnow()).astimezone(pytz.timezone("America/Louisville"))
    timestring_file =  timestamp_b.strftime("%Y%m%d%H%M%S")

    unittest_configuration = convert_json_to_dict("input_user/unittest_configuration.json")
    unit_test_batch_name = unittest_configuration['unit_test_batch_name']

    if "" not in unittest_configuration["dbs_list"]:
        for k,v in unittest_configuration["dbs_list"].items():
            print(k,v)

if __name__ == "__main__":
    main()
