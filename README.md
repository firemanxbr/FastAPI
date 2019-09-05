# paxful
Python developer Test Assignment


# Local environment


## MYSQL
```bash
$ docker pull mysql

$ docker run -p 3306:3306 -h localhost -e MYSQL_ROOT_PASSWORD=password -d mysql:latest
```

## FASTAPI

```bash
$ docker build -t fastapi . 

$ docker run -d -p 80:80 fastapi:latest
```

```sql
CREATE DATABASE IF NOT EXISTS paxful;
CREATE TABLE IF NOT EXISTS users (user_id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), email VARCHAR(255) NOT NULL UNIQUE, token VARCHAR(255) NOT NULL UNIQUE, max_wallet TINYINT DEFAULT(10) );  
CREATE TABLE IF NOT EXISTS wallets (wallet_id INT AUTO_INCREMENT PRIMARY KEY, address VARCHAR(255) NOT NULL UNIQUE, balance DECIMAL(10,8), user_id INT, FOREIGN KEY (user_id) REFERENCES users(user_id) );


INSERT INTO paxful.users(name, email, token) values("Marcelo Barbosa", "mr.marcelo.barbosa@gmail.com", "86f41a39c3a243fd22d96228eaeb23a60df36e76");
INSERT INTO paxful.wallets(address, balance, user_id) values("bc1q84y2quplejutvu0h4gw9hy59fppu3thg0u2xz3", "1", "1");


# show databases; 
# use paxful;
# select * from paxful.users;
select * from paxful.wallets
```
