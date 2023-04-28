-- CREATE DATABASE IF NOT EXISTS awb;
-- USE awb;
-- -- CREATE TABLE IF NOT EXISTS submissions (
-- --     id VARCHAR(20) PRIMARY KEY,
-- --     subreddit VARCHAR(20) NOT NULL,
-- --     removed BOOL NOT NULL DEFAULT FALSE,
-- --     deleted BOOL NOT NULL DEFAULT FALSE
-- -- );
-- CREATE TABLE IF NOT EXISTS images (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     submission_id VARCHAR(20) NOT NULL,
--     url VARCHAR(255) NOT NULL,
--     width INT NOT NULL,
--     height INT NOT NULL,
--     sift LONGBLOB NOT NULL,
--     UNIQUE KEY (submission_id, url)
-- );

CREATE DATABASE IF NOT EXISTS celery;
