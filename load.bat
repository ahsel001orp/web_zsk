set oracle_home=T:\oracl11clt\product\11.2.0\client_1

T:\oracl11clt\product\11.2.0\client_1\bin\sqlldr.exe userid=%root_db_login%/%root_db_password%@%ip_db%/test control=to_database.ctl log=to_database.log errors=200000

