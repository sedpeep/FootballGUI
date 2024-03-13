-- Create database if not exists
CREATE DATABASE IF NOT EXISTS football_app;

USE football_app;

-- Create users table with auto-incrementing user_id
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password CHAR(64) NOT NULL,
    department_id CHAR(36) NOT NULL
);

-- Create players table with auto-incrementing player_id
CREATE TABLE IF NOT EXISTS players (
    player_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT,
    grade VARCHAR(255),
    position VARCHAR(255),
    minutes_played INT DEFAULT 0
);

-- Create original_team table

CREATE TABLE IF NOT EXISTS original_team (
    original_team_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    week INT NOT NULL,
    player_name VARCHAR(100) NOT NULL,
    position VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Create substitute_team table
CREATE TABLE IF NOT EXISTS substitute_team (
    substitute_team_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    week INT NOT NULL,
    player_name VARCHAR(100) NOT NULL,
    position VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);


-- Create player_stats table
CREATE TABLE IF NOT EXISTS player_stats (
    stats_id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT,
    goals_scored INT DEFAULT 0,
    fouls_committed INT DEFAULT 0,
    assists_made INT DEFAULT 0,
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);

-- Drop matches table as it is not useful or relevant
DROP TABLE IF EXISTS matches;

ALTER TABLE players
ADD COLUMN user_id INT,
ADD CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES users(user_id);

CREATE TABLE IF NOT EXISTS player_game_week_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT,
    game_week INT,
    minutes_played INT,
    team_type ENUM('original', 'substitute'),
    team_id INT,
    FOREIGN KEY (player_id) REFERENCES players(player_id),
    CONSTRAINT fk_team_type_original FOREIGN KEY (team_id)
        REFERENCES original_team(original_team_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_team_type_substitute FOREIGN KEY (team_id)
        REFERENCES substitute_team(substitute_team_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

INSERT INTO player_game_week_stats (player_id, game_week, minutes_played, team_type, team_id) VALUES
((SELECT player_id FROM players WHERE name = 'Player One'), 1, 90, 'original',
    (SELECT original_team_id FROM original_team WHERE week = 1 AND player_name = 'Player One'));

-- Insert dummy data for Player One
INSERT INTO player_game_week_stats (player_id, game_week, minutes_played, team_type, team_id)
VALUES
((SELECT player_id FROM players WHERE name = 'Player One'), 1, 90, 'original',
    (SELECT original_team_id FROM original_team WHERE week = 1 AND player_name = 'Player One')),
((SELECT player_id FROM players WHERE name = 'Player One'), 2, 120, 'original',
    (SELECT original_team_id FROM original_team WHERE week = 2 AND player_name = 'Player One')),
((SELECT player_id FROM players WHERE name = 'Player One'), 3, 110, 'original',
    (SELECT original_team_id FROM original_team WHERE week = 3 AND player_name = 'Player One'));

-- Insert dummy data for Player Two
INSERT INTO player_game_week_stats (player_id, game_week, minutes_played, team_type, team_id)
VALUES
((SELECT player_id FROM players WHERE name = 'Player Two'), 1, 100, 'original',
    (SELECT original_team_id FROM original_team WHERE week = 1 AND player_name = 'Player Two')),
((SELECT player_id FROM players WHERE name = 'Player Two'), 2, 130, 'original',
    (SELECT original_team_id FROM original_team WHERE week = 2 AND player_name = 'Player Two')),
((SELECT player_id FROM players WHERE name = 'Player Two'), 3, 90, 'original',
    (SELECT original_team_id FROM original_team WHERE week = 3 AND player_name = 'Player Two'));
