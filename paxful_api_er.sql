DROP DATABASE IF EXISTS paxful;
CREATE DATABASE IF NOT EXISTS paxful;
USE paxful;

CREATE TABLE IF NOT EXISTS users
    (user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) NOT NULL UNIQUE,
    token BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) NOT NULL UNIQUE,
    max_wallet TINYINT UNSIGNED DEFAULT(10),
    date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)
    ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS wallets
    (wallet_id INT AUTO_INCREMENT PRIMARY KEY,
    address VARCHAR(255) NOT NULL UNIQUE,
    balance DECIMAL(10,8) UNSIGNED NOT NULL DEFAULT(1),
    user_id INT,
    date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_wallets_users FOREIGN KEY (user_id) REFERENCES users(user_id))
    ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS transactions
    (transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    address_income VARCHAR(255) NOT NULL,
    address_outcome VARCHAR(255) NOT NULL,
    amount DECIMAL(10,8) UNSIGNED NOT NULL,
    user_id INT,
    date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_transactions_users FOREIGN KEY (user_id) REFERENCES users(user_id))
    ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS statics
	(statics_id INT AUTO_INCREMENT PRIMARY KEY,
    profit DECIMAL(10,8) NOT NULL,
    transaction_id INT,
    date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_statics_transactions FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id))
	ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TRIGGER update_user_wallet_balance BEFORE INSERT ON transactions FOR EACH ROW
	UPDATE wallets SET balance = balance - NEW.amount WHERE address = NEW.address_outcome;

CREATE TRIGGER update_user_wallet_limit BEFORE INSERT ON wallets FOR EACH ROW
	UPDATE users SET max_wallet = max_wallet - 1 WHERE user_id = NEW.user_id;
    
CREATE TRIGGER update_user_wallet_income BEFORE INSERT ON transactions FOR EACH ROW
	UPDATE wallets SET balance = (balance + (NEW.amount - (NEW.amount * 1.5)/100)) WHERE address = NEW.address_income;

CREATE TRIGGER update_statics_profit AFTER INSERT ON transactions FOR EACH ROW
	INSERT INTO statics(transaction_id, profit) VALUES(NEW.transaction_id, (NEW.amount * 1.5)/100);

/* Registers to Test Proposal */
INSERT INTO users(name, email) VALUES("User 1", "user_1@gmail.com");
INSERT INTO users(name, email) VALUES("User 2", "user_2@gmail.com");

INSERT INTO wallets(address, user_id) VALUES("bc1q84y2quplejutvu0h4gw9hy59fppu3thg0u2xz3", "1");
INSERT INTO wallets(address, user_id) VALUES("ab2m73q1mzojdbytvu0h4gw9hy59fppu3thg0u1ny2", "2");

INSERT INTO transactions(address_income, address_outcome, amount, user_id) VALUES("ab2m73q1mzojdbytvu0h4gw9hy59fppu3thg0u1ny2", "bc1q84y2quplejutvu0h4gw9hy59fppu3thg0u2xz3", "0.5", "1");
INSERT INTO transactions(address_income, address_outcome, amount, user_id) VALUES("bc1q84y2quplejutvu0h4gw9hy59fppu3thg0u2xz3", "ab2m73q1mzojdbytvu0h4gw9hy59fppu3thg0u1ny2", "0.5", "2");

/* Getting the Token
SELECT BIN_TO_UUID(token) FROM users;
*/

/* Getting total of transactions and total of profit of the platform
SELECT SUM(profit), (SELECT count(*) FROM statics) FROM statics
*/
