import logging
log = logging.getLogger('general')

from django.http import Http404
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext

import pypyodbc

from models import OdbcDatabase


def home(request):
    dbs = OdbcDatabase.objects.all()
    return render_to_response("home.html",
                              {'dbs': dbs},
                              context_instance=RequestContext(request))


def info(request, db=None):
    class TableInfo():
        def __init__(self, table_obj):
            self.table_cat = table_obj[0]
            self.table_scehma = table_obj[1]
            self.table_name = table_obj[2]
            self.table_type = table_obj[3]
            self.remarks = table_obj[4]

    use_db = get_object_or_404(OdbcDatabase, name=db)
    cur = get_cursor(use_db)
    if not cur:
        log.warning("Could not create cursor for {}".format(db))
        raise Http404
    # Get info about all tables in the DB
    t_meta = None
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
    return render_to_response("info.html",
                              {'db': use_db,
                               'tables': t_meta},
                              context_instance=RequestContext(request))


def sql(request, db=None):
    use_db = get_object_or_404(OdbcDatabase, name=db)
    query = request.GET.get('q')
    if query:
        cur = get_cursor(use_db)
        if not cur:
            log.warning("Could not create cursor for {}".format(db))
            raise Http404
        log.debug("SQL ({}): {}".format(db, query))
        res = cur.execute(query).fetchall()
        return render_to_response("sql_results.html",
                                  {'db': use_db,
                                   'sql': query,
                                   'results': res},
                                  context_instance=RequestContext(request))
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
