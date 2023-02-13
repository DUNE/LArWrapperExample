export SQL_QUERY_DIR=${ART_DIR}/tools/sqlite/memoryTracker
sqlite3 mem.db < ${SQL_QUERY_DIR}/peak-summary.sql
#sqlite3 mem.db < ${SQL_QUERY_DIR}/max-rss-events.sql
#sqlite3 mem.db < ${SQL_QUERY_DIR}/max-vsize-events.sql
#sqlite3 mem.db < ${SQL_QUERY_DIR}/max-delta-rss-events.sql
#sqlite3 mem.db < ${SQL_QUERY_DIR}/max-delta-vsize-events.sql
#sqlite3 mem.db < ${SQL_QUERY_DIR}/max-rss-modules.sql
#sqlite3 mem.db < ${SQL_QUERY_DIR}/max-vsize-modules.sql
#sqlite3 mem.db < ${SQL_QUERY_DIR}/max-delta-rss-modules.sql
#sqlite3 mem.db < ${SQL_QUERY_DIR}/max-delta-vsize-modules.sql
    
export SQL_TIME_QUERY_DIR=${ART_DIR}/tools/sqlite/timeTracker/
#ls ${SQL_TIME_QUERY_DIR}
sqlite3 time.db < ${SQL_TIME_QUERY_DIR}/event-summary.sql
#sqlite3 time.db < ${SQL_TIME_QUERY_DIR}/module-summary.sql
#sqlite3 time.db < ${SQL_TIME_QUERY_DIR}/max-events.sql
