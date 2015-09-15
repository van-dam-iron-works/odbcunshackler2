import logging
log = logging.getLogger('general')

from django.core.serializers.json import DjangoJSONEncoder
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext

import json
import pypyodbc


from .models import OdbcDatabase


class TableInfo():
    def __init__(self, table_obj):
        self.table_cat = table_obj[0]
        self.table_schema = table_obj[1]
        self.table_name = table_obj[2]
        self.table_type = table_obj[3]
        self.remarks = table_obj[4]


class ColumnInfo():
    def __init__(self, column_obj):
        self.table_cat = column_obj[0]
        self.table_schema = column_obj[1]
        self.table_name = column_obj[2]
        self.column_name = column_obj[3]
        self.data_type = column_obj[4]
        self.type_name = column_obj[5]
        self.column_size = column_obj[6]
        self.buffer_length = column_obj[7]
        self.decimal_digits = column_obj[8]
        self.num_prec_radix = column_obj[9]
        self.nullable = column_obj[10]
        self.remarks = column_obj[11]


def home(request):
    dbs = OdbcDatabase.objects.all()
    return render_to_response("home.html",
                              {'dbs': dbs},
                              context_instance=RequestContext(request))


def info(request, db=None, table=None):

    if db is None:
        dbs = OdbcDatabase.objects.all()
        return render_to_response("home.html",
                              {'dbs': dbs},
                              context_instance=RequestContext(request))

    use_db = get_object_or_404(OdbcDatabase, name=db)
    cur = get_cursor(use_db)
    if not cur:
        log.warning("Could not create cursor for {}".format(db))
        raise Http404
    t_meta = None
    c_meta = None
    if table is None:
        t_meta = get_table_info(cur)
    else:
        c_meta = get_column_info(cur, table)
    return render_to_response("info.html",
                              {'db': use_db,
                               'tables': t_meta,
                               'table': table,
                               'columns': c_meta},
                              context_instance=RequestContext(request))
        

def sql(request, db=None):
    ''' Options:
            q: SQL query string
            c: True = Try to get the column names and return them as a list as
                      the first record with the data
    '''
    use_db = get_object_or_404(OdbcDatabase, name=db)
    query = request.GET.get('q')
    results = {}
    if query is not None:
        cur = get_cursor(use_db)
        if not cur:
            log.warning("Could not create cursor for {}".format(db))
            raise Http404
        log.debug("SQL ({}): {}".format(db, query))
        try:
            res = cur.execute(query).fetchall()
        except:
            log.warning("Could not execute query for {}: {}".format(db, query))
            raise Http404
        results['columns'] = get_select_fields_from_query(use_db, query)
        results['rows'] = res
        return HttpResponse(json.dumps(results, cls=DjangoJSONEncoder),
                            content_type="application/json")
    else:
        return render_to_response("sql.html",
                                  {'db': use_db, },
                                  context_instance=RequestContext(request))


def get_cursor(db):
    conn = pypyodbc.connect(db.dsn,
                            unicode_results=True,
                            readonly=True)
    if conn:
        log.info("Connected to {}".format(db.name))
    else:
        log.warning("Failed to connect to {}".format(db.name))

    cur = conn.cursor()
    if cur:
        log.info("Cursor created successfully")
    else:
        log.error("Cursor failed.")
        conn.close()
    return cur


def get_table_info(cur):
    table_res = cur.tables()
    if table_res:
        tables = table_res.fetchall()
        if tables:
            t_meta = []
            for tbl in tables:
                t_meta.append(TableInfo(tbl))
        else:
            log.warning("Error while fetching tables from cursor.")
            raise Http404
    else:
        log.warning("Cursor error while fetching tables.")
        raise Http404
    return t_meta


def get_column_info(cur, use_table):
    # Get info about all columns in the table
    column_res = cur.columns(use_table)
    if column_res:
        columns = column_res.fetchall()
        if columns:
            c_meta = []
            for col in columns:
                c_meta.append(ColumnInfo(col))
        else:
            log.warning("Error while fetching columns from cursor.")
            raise Http404
    else:
        log.warning("Cursor error while fetching columns.")
        raise Http404
    return c_meta


def get_select_fields_from_query(cur, query):
    """ Tries to find the column names in a SELECT statement
        TODO: If column name = *, query for the list of columns in the table
    """
    from_pos = query.lower().find("from")
    select_columns = query[len("select"):from_pos]
    columns = select_columns.split(",")
    cleaned_columns = []
    for sel in columns:
        stripped = sel.strip(" []")
        cleaned_columns.append(stripped)
    return cleaned_columns
