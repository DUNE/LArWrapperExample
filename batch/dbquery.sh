export SQL_QUERY_PATH=${HERE}/sql
sqlite3 mem.db < ${SQL_QUERY_PATH}/peak-summary.sql
sqlite3 mem.db < ${SQL_QUERY_PATH}/max-rss-events.sql
sqlite3 mem.db < ${SQL_QUERY_PATH}/max-vsize-events.sql
sqlite3 mem.db < ${SQL_QUERY_PATH}/max-delta-rss-events.sql
sqlite3 mem.db < ${SQL_QUERY_PATH}/max-delta-vsize-events.sql
sqlite3 mem.db < ${SQL_QUERY_PATH}/max-rss-modules.sql
sqlite3 mem.db < ${SQL_QUERY_PATH}/max-vsize-modules.sql
sqlite3 mem.db < ${SQL_QUERY_PATH}/max-delta-rss-modules.sql
sqlite3 mem.db < ${SQL_QUERY_PATH}/max-delta-vsize-modules.sql
    

#ls ${SQL_TIME_QUERY_PATH}
sqlite3 time.db < ${SQL_QUERY_PATH}/event-summary.sql
sqlite3 time.db < ${SQL_QUERY_PATH}/module-summary.sql
sqlite3 time.db < ${SQL_QUERY_PATH}/max-events.sql
