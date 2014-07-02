#relax editor

A tool intended for translating Mount&Blade warband mod language into Chinese.

##environment and tools

1. windows 7.
2. python 2.7, with wx-python 3.0 and mysql-python 1.25 package.
3. mysql-server 5, coresponding to mysql-python 1.25.
4. notepad++, not required but recommended.

##mysql charset

Open *my.ini* in mysql directory, for example *C:\Program Files (x86)\MySQL\MySQL Server 5.5\my.ini*, and add below lines to *my.ini*.

>[client]  
**default-character-set = utf8**

>[mysql]  
**default-character-set = utf8**

>[mysqld]  
**init__connect='SET collation_connection = utf8_unicode_ci'**  
**character-set-server = utf8**  
**collation-server = utf8_unicode_ci**


