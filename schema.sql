CREATE DATABASE IF NOT EXISTS load_counter;
USE load_counter;

CREATE TABLE IF NOT EXISTS page_load_counter (
    id TINYINT UNSIGNED NOT NULL PRIMARY KEY,
    total_loads BIGINT UNSIGNED NOT NULL DEFAULT 0
);

INSERT IGNORE INTO page_load_counter (id, total_loads) VALUES (1, 0);
