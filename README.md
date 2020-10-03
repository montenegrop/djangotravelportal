### 
```
#set up myqsl server
sudo docker-compose up
```

### Install a development environment

```
CREATE DATABASE yas CHARACTER SET utf8;
#install system dependencies
apt-get install libgdal-dev
#clone the repo
git clone <this repo URL>/yas
#enter the repo
cd yas/
#create a database and place a custom .env file in the project root
#this should ideally be MySQL but you can also use sqlite locally
#create a virtual environment for python dependencies
virtualenv --python=python3 venv
#activate virtual environment
source venv/bin/activate
#install python dependencies
pip install -r requirements.txt
#install node dependencies
npm install
#run auth migrations
python manage.py migrate auth
#run rest of migrations
python manage.py migrate
#create yourself a superuser
python manage.py createsuperuser
#run development server
python manage.py runserver 0:8000
#open another terminal and run the following
npm run watch
```

Notes for  importing
```
#ALTER TABLE places_currency CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci
sudo apt-get install python-mysqldb
```

How to fix networking in VM

```
sudo nano /etc/network/interfaces
#add only this:
iface eth0 inet dhcp
sudo nano /etc/NetworkManager/NetworkManager.conf
#and change managed=true
sudo service network-manager restart
sudo sshfs -o allow_other  -p 2223 yas@127.0.0.1:/opt/YAS/ /home/juan/Desktop/juan/dev/yas/yas_shared

scp -P 2223 yas@127.0.0.1:/home/yas/yas.sql /home/juan/Desktop/juan/dev/yas/yas_perl.sql
mysql -u phpma -p yas_perl < /home/juan/Desktop/juan/dev/yas/yas_perl.sql
```


Sync yas
```
#remove all migrations for a fresh start
rm -rf ads/migrations/00*
rm -rf places/migrations/00*
rm -rf reviews/migrations/00*
rm -rf lodges/migrations/00*
rm -rf analytics/migrations/00*
rm -rf blog/migrations/00*
rm -rf operators/migrations/00*
rm -rf extras/migrations/00*
rm -rf core/migrations/00*
rm -rf users/migrations/00*
rm -rf photos/migrations/00*
rm -rf ads/migrations/__pycache__
rm -rf places/migrations/__pycache__
rm -rf reviews/migrations/__pycache__
rm -rf lodges/migrations/__pycache__
rm -rf analytics/migrations/__pycache__
rm -rf blog/migrations/__pycache__
rm -rf operators/migrations/__pycache__
rm -rf extras/migrations/__pycache__
rm -rf core/migrations/__pycache__
rm -rf users/migrations/__pycache__
rm -rf photos/migrations/__pycache__

#remove media images
sudo rm -r media/images/*
#set up database
python manage.py makemigrations
python manage.py migrate auth
python manage.py migrate
#import
python -u manage.py import_main  -db_name yas_perl -db_user phpma -db_pass phpma > output
#sync images from test
rsync -avzr  --exclude 'cache' --exclude '*crop*' --bwlimit=2000 yas_staging:/home/juan/yas/media .


```

Sync media folder and database to test server
```
#Add this to your ssh config
cat  ~/.ssh/config
#host yas_staging
#User <user>
#hostname 134.209.196.106
rsync -avzr  --exclude 'cache' --bwlimit=2000 media yas_staging:/home/juan/yas/

#or 

rsync -avzr  --exclude 'cache' --exclude '*crop*' --bwlimit=2000 media/. juan@46.101.176.142:/home/juan/yas/media/.

mysqldump -u phpma -p yas > yas.sql

gzip yas.sql  && scp yas.sql.gz yas_staging:/home/juan/. && ssh yas_staging "rm yas.sql" && ssh yas_staging "gunzip yas.sql.gz"
ssh yas_staging
#mysql -u yas -p yas < yas.sql
ssh yas_staging "mysql -u yas -p yas < yas.sql"
```


Troubleshoot
```
# django.db.utils.OperationalError: (1709, 'Index column size too large. The maximum column size is 767 bytes.')

CREATE DATABASE `yas` COLLATE 'utf8_unicode_ci';
USE yas;
set global innodb_large_prefix = ON;
set global innodb_file_per_table = ON;
set global innodb_file_format = BARRACUDA;

#Cannot create SPATIAL INDEX CREATE SPATIAL INDEX `places_countryindex_location_id` ON `places_countryindex`(`location`). Only MyISAM and (as of MySQL 5.7.5) InnoDB support them.


#problem installing mysqllib in macOS
env LDFLAGS="-I/usr/local/opt/openssl/include -L/usr/local/opt/openssl/lib" pip install mysqlclient

```


### Neil's environment
#### To start the dev env
```
cd /Users/Neil/Documents/GitHub/yas
source venv/bin/activate
python manage.py runserver 0:8000
#open the browser in localhost:80000
```

### Common problems
```
# django.core.exceptions.ImproperlyConfigured: Error loading MySQLdb module.
# Did you install mysqlclient?

cp -r /usr/local/mysql/lib/* /usr/local/lib/



#Another solution

  513  sudo cp -r /usr/local/Cellar/mysql@5.6/5.6.46_2/lib/* /usr/local/lib/
  514  pip freeze
  515  pip freeze | head -n 30
  516  pip freeze | head -n 30
  517  pip freeze | head -30
  518  head
  519  pip freeze
  520  pip freeze | grep mys
  521  pip install mysql-python
  522  which python
  523  python
  524  which pip
  525  python manage.py runserver 0:8000
  526  pip install mysqlclient
  527  which python
  528  export DYLD_LIBRARY_PATH=/usr/local/mysql/lib/
  529  pip install mysql-python
  530  history | grep mys
  531  sudo cp -r /usr/local/Cellar/mysql@5.6/5.6.46_2/lib/* /usr/local/lib/
  532  pip install mysql-python
  533  python manage.py runserver 0:8000
  534  brew install mysql-python
  535  brew install mysql
  536  pip install mysqlclient
  537  brew install mysql-connector-c
  538  pip install mysqlclient
  539  env LDFLAGS="-I/usr/local/opt/openssl/include -L/usr/local/opt/openssl/lib" pip install mysqlclient==1.3.12
  540  pip install mysql-python
  541  pip install mysqlclient
  542  python manage.py runserver 0:8000
  543  env LDFLAGS="-I/usr/local/opt/openssl/include -L/usr/local/opt/openssl/lib" pip install mysqlclient
  544  pip uninstall mysqlclient
  545  pip install mysqlclient
  546  pip install wheel
  547  pip install mysqlclient
  548  pip install -r requirements.txt
  549  pip install -U wheel
  550  export LIBRARY_PATH=$LIBRARY_PATH:/usr/local/opt/openssl/lib/
  551  pip install -U wheel
  552  pip install mysqlclient
  553  python manage.py runserver 0:8000
  554  history
```

### Deploy
```
fab test deploy -u juan
```

### Troubleshooting

``` 
The database backend does not accept 0 as a value for AutoField.
```

To solve this, ensure that the tables have PRIMARY index and AUTO_INCREMENT attribute in its pk column

### Sync local-test
```
#Download dev database
mysqldump -h 134.209.196.106 -u yas -p yas --column-statistics=0 > yas.sql
#Import to local server
mysql -u yas -p yas < yas.sql
#Import images local server
rsync -avzr  --exclude 'cache' --exclude '*crop*' --bwlimit=2000 neil@134.209.196.106:/home/juan/yas/media .
```

### Required to add META to all the templates
```
{% block meta_name %}{% endblock %}
{% block meta_itemprop_description %}{% endblock %}
{% block meta_description %}{% endblock %}
{% block meta_title %}{% endblock %}
{% block meta_keywords %}{% endblock %}
```

### YAS fresco
cd yas-fresco
npm i
npm build 
grunt
cd ..
npm i yas-fresco


### SSL
```
# using apache conf file and:
sudo certbot --apache --cert-name crescente.com.ar -d yastest.crescente.com.ar -w /var/lib/letsencrypt/http_challenges
```




### facebook login

add this to 
Inicio de sesion > Configuracion > URI de redireccionamiento de OAuth válidos

https://yastest.crescente.com.ar/social-auth/complete/facebook




* * * * * (/home/juan/yas/venv/bin/python manage.py send_queued_mail >> send_mail.log 2>&1)




invalid chars  ALTER TABLE operators_itinerarydaydescription CHANGE description description VARCHAR(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;



sudo apt install optipng jpegoptim