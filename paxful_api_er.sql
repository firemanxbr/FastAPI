DROP DATABASE IF EXISTS paxful;
CREATE DATABASE IF NOT EXISTS paxful;
USE paxful;

CREATE TABLE IF NOT EXISTS users
    (user_id INT(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) NOT NULL UNIQUE,
    token VARCHAR(255) NOT NULL UNIQUE,
    max_wallet TINYINT(4) DEFAULT(10),
    date_created DATETIME NOT NULL)
    ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS wallets
    (wallet_id INT(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    address VARCHAR(255) NOT NULL UNIQUE,
    balance DECIMAL(10,8) DEFAULT(1),
    user_id INT(11),
    date_created DATETIME NOT NULL,
    CONSTRAINT fk_wallets_users FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE)
    ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS transactions
    (transaction_id INT(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    address_income VARCHAR(255) NOT NULL,
    address_outcome VARCHAR(255) NOT NULL,
    amount DECIMAL(10,8) NOT NULL
    user_id INT(11),
    date_created DATETIME NOT NULL,
    CONSTRAINT fk_transactions_users FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE)
    ENGINE=InnoDB DEFAULT CHARSET=utf8;

/* Test 
INSERT INTO paxful.users(name, email, token) values("Marcelo Barbosa", "mr.marcelo.barbosa@gmail.com", "86f41a39c3a243fd22d96228eaeb23a60df36e76");
INSERT INTO paxful.wallets(address, user_id) values("bc1q84y2quplejutvu0h4gw9hy59fppu3thg0u2xz3", "1");
*/