from app.db.connection import transaction
with transaction(commit=False) as cur:
    cur.execute("select table_name from information_schema.tables where table_schema='public' order by 1")
    tabs = [r['table_name'] for r in cur.fetchall()]
    print('TABLES:', tabs)
    for t in tabs:
        cur.execute('select count(*) c from "%s"' % t)
        print('  %s : %s lignes' % (t, cur.fetchone()['c']))
