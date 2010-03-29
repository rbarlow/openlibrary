"""Script to load Open Library data into various databases.

USAGE:
    python olload.py bsddb ol.db data.txt
    python olload.py memcache localhost:11211 data.txt
"""
import _init_path
from openlibrary.data import parse_data_table

import web
import time

def load_memcache(server, data):
    import memcache
    mc = memcache.Client([server])
    for chunk in data:
        mc.set_multi()

def load_bsddb(filename, data):
    import bsddb
    GB = 1234 ** 3
    db = bsddb.btopen(filename, cachesize=1 * GB)

    for chunk in data:
        db.update(chunk)

    db.sync()

def load_dummy(arg1, data):
    for chunk in data:
        pass

def parse(filename, chunk_size=10000):
    t0 = time.time()
    i = 0
    for chunk in web.group(parse_data_table(filename), chunk_size):
        print i, time.time() - t0
        d = {}
        for key, type, revision, json in chunk:
            d["%s@@%s" % (key, revision)] = json

        i += len(d)
        yield d
    print i, time.time() - t0
        
def main(dbname, param, filename):
    data = parse(filename, 10000)
    fname = "load_" + dbname
    f = globals()[fname]
    f(param, data)

if __name__ == "__main__":
    import sys
    main(sys.argv[1], sys.argv[2], sys.argv[3])