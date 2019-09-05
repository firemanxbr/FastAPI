DROP DATABASE IF EXISTS paxful;
CREATE DATABASE IF NOT EXISTS paxful;
USE paxful;

CREATE TABLE IF NOT EXISTS users
    (user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) NOT NULL UNIQUE,
    token VARCHAR(255) NOT NULL UNIQUE,
    max_wallet TINYINT UNSIGNED DEFAULT(10),
    date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)
    ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS wallets
    (wallet_id INT AUTO_INCREMENT PRIMARY KEY,
    address VARCHAR(255) NOT NULL UNIQUE,
    balance DECIMAL(10,8) UNSIGNED DEFAULT(1),
    user_id INT,
    date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_wallets_users FOREIGN KEY (user_id) REFERENCES users(user_id))
    ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS transactions
    (transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    address_income VARCHAR(255) NOT NULL,
    address_outcome VARCHAR(255) NOT NULL,
    amount DECIMAL(10,8) NOT NULL,
    user_id INT,
    date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_transactions_users FOREIGN KEY (user_id) REFERENCES users(user_id))
    ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TRIGGER update_user_wallet_balance BEFORE INSERT ON transactions FOR EACH ROW
	UPDATE wallets SET balance = balance - NEW.amount WHERE address = NEW.address_outcome;
    
CREATE TRIGGER update_user_wallet_limit BEFORE INSERT ON wallets FOR EACH ROW
	UPDATE users SET max_wallet = max_wallet - 1 WHERE user_id = NEW.user_id;

INSERT INTO users(name, email, token) VALUES("User 1", "user_1@gmail.com", "86f41a39c3a243fd22d96228eaeb23a60df36e76");
INSERT INTO users(name, email, token) VALUES("User 2", "user_2@gmail.com", "75z32b48c3a243fd22d96228eaeb23a60df36e75");
INSERT INTO wallets(address, user_id) VALUES("bc1q84y2quplejutvu0h4gw9hy59fppu3thg0u2xz3", "1");
INSERT INTO wallets(address, user_id) VALUES("ab2m73q1mzojdbytvu0h4gw9hy59fppu3thg0u1ny2", "2");
INSERT INTO transactions(address_income, address_outcome, amount, user_id) VALUES("ab2m73q1mzojdbytvu0h4gw9hy59fppu3thg0u1ny2", "bc1q84y2quplejutvu0h4gw9hy59fppu3thg0u2xz3", "0.5", "1");
