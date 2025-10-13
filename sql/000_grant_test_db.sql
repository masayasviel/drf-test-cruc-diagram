-- pytestが作る任意の test_ で始まるDBにフル権限を付与
GRANT ALL PRIVILEGES ON `test\_%`.* TO 'my_user'@'%';

FLUSH PRIVILEGES;
