import requests
import psycopg2
from psycopg2 import Error
import re
import urllib.parse
import copy
import json
from datetime import datetime
from dateutil.parser import parse

def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try: 
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False


f = open("db-params.json",) 
params = json.load(f) 
f.close()

f = open("airtable.json",) 
airtable_data = json.load(f) 
f.close()
bases = airtable_data["bases"]
airtable_key = airtable_data["airtable_key"]


print(params)
print(bases)
print(airtable_key)

def create_table(table_name, fields, field_type_general):
    conn = None
    
    table_name = re.sub('[^A-Za-z0-9]+', '', table_name).lower()

    conn = psycopg2.connect(**params)

    cur = conn.cursor()
    
    cur.execute("drop table if exists "+table_name)

    insert_query_list = []
    for field in fields:
        if field_type_general[field] == "number":
            insert_query_list += [field+" float"]
        elif field_type_general[field] == "time":
            insert_query_list += [field+" timestamp"]
        else:
            insert_query_list += [field+" varchar(2000)"]
    
    insert_query_values = ",".join(insert_query_list)

    
    insert_query = 'create table '+table_name+' ('+insert_query_values+')'


    cur.execute(insert_query)


    conn.commit()

    cur.close()

    if conn is not None:
        conn.close()

def insert(table_name, fields, all_values):
    table_name = re.sub('[^A-Za-z0-9]+', '', table_name).lower()
    
    conn = None

    conn = psycopg2.connect(**params)

    cur = conn.cursor()
    
    cur.execute("delete from "+table_name)
    
    records_list_template = "("+','.join(['%s'] * len(fields))+")"

    insert_query_values = '{}'.format(records_list_template)

    insert_query_values = (','.join(cur.mogrify(insert_query_values, x).decode('utf8') for x in all_values))
    insert_query = ('insert into '+table_name+' ('+",".join(fields)+') values {}').format(insert_query_values)

    cur.execute(insert_query)

    conn.commit()
    
    cur.close()

    if conn is not None:
        conn.close()



def fetch_table(base, table):
    offset = ""
    all_data = []
    page = 0

    max_records = ""

    print(table, datetime.now())

    while not (offset==None):
        page +=1 

        endpoint = "https://api.airtable.com/v0/"+base+"/"+table+"?"+offset+max_records

        headers = {"Authorization": "Bearer "+airtable_key}

        data = requests.get(endpoint, headers=headers).json()

        records = data["records"]
        all_data += records
        if "offset" in data:
            offset = "&offset="+data["offset"]
        else:
            offset = None

    print(table, len(all_data), datetime.now())
    blank_record = {}
    final_fields = []
    final_field_mapping = {}
    final_field_mapping_reverse = {}
    field_type = {}
    field_type_general = {}

    record = records[0]
    record_id = record["id"]
    record_fields = record["fields"]
    record_createdTime = record["createdTime"]
    fields = record_fields.keys()

    data_to_enter = []

    for a_record in all_data:
        record = a_record["fields"]
        fields = record.keys()
        new_record = []
        for field in fields:
            new_field = copy.deepcopy(field)

            new_field = re.sub('[^A-Za-z0-9]+', '', new_field).lower()

            if new_field == "desc":
                new_field = "desc_"

            if new_field == "using":
                new_field = "using_"

            if new_field == "asc":
                new_field = "asc_"


            while (new_field in blank_record) and (final_field_mapping_reverse[new_field] != field):
                new_field = new_field + "_"

            if new_field not in blank_record:
                blank_record[new_field] = ""
                final_fields+=[new_field]
                final_field_mapping[field] = new_field
                final_field_mapping_reverse[new_field] = field
                field_type[new_field] = type(record[field])

                if type(record[field])==type(int(1)) or type(record[field])==type(float(1)):
                    field_type_general[new_field] = "number"
                elif type(record[field]) == type("") and is_date(record[field]):
                    field_type_general[new_field] = "time"
                else:    
                    field_type_general[new_field] = "string"

    for a_record in all_data:
        record = a_record["fields"]
        new_record = []
        for field in final_fields:
            if final_field_mapping_reverse[field] in record:
                if field_type_general[field] == "number":
                    if type(record[final_field_mapping_reverse[field]])==type(int(1)) or type(record[final_field_mapping_reverse[field]])==type(float(1)):
                        new_record += [record[final_field_mapping_reverse[field]]]
                    else:
                        new_record += [0]
                elif field_type_general[field] == "time":
                    if type(record[final_field_mapping_reverse[field]]) == type("") and is_date(record[final_field_mapping_reverse[field]]):
                        new_record += [parse(record[final_field_mapping_reverse[field]])]
                    else:
                        new_record += [datetime.fromtimestamp(0)]
                else:
                    new_record += [str(record[final_field_mapping_reverse[field]])[:2000].replace("'",'"').replace(",","")]
            else:
                if field_type_general[field] == "number":
                    new_record += [0]
                elif field_type_general[field] == "time":
                    new_record += [datetime.fromtimestamp(0)]
                else:
                    new_record += [""]
            
        data_to_enter += [new_record]

    create_table(table, final_fields, field_type_general)
    insert(table, final_fields, data_to_enter)

for base in bases:
    tables = bases[base]

    for table in tables:
        try:
            fetch_table(base, table)
        except (Exception) as error:
           print(error)