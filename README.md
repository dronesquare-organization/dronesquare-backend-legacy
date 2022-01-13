migrations는 commit X  
venv도 commit X  
  
  
* window 에서 사용 시  
  
pip install pipwin  
pipwin refresh  
pipwin install gdal  
pipwin install pycurl  
  
* lib에 있는 파일은 해당 경로로 가서 pip install filename으로 설치해야함  
* 서버에는 설치 되어 있는 상태임, 설치, 파일 옮기지 말것!  
* python 모듈 잘 안깔리는것들은 아래의 url에서 python 버전에 맞는 whl 받아서 설치  
https://www.lfd.uci.edu/~gohlke/pythonlibs/  
  
  
#### pip install 목록 ###  
pip install -r requirements.txt  
  
  
alter table projects drop CONSTRAINT projects_pkey cascade;  
alter table projects add CONSTRAINT projects_pkey PRIMARY KEY(id, email);  
  
  
alter table imgs add CONSTRAINT imgs_projects_fkey FOREIGN KEY("projectId", email) REFERENCES projects(id, email);  
alter table imgs drop CONSTRAINT imgs_pkey;  
alter table imgs add CONSTRAINT imgs_pkey PRIMARY KEY (id, "projectId", name, format);  
  
  
drop table account_emailaddress cascade;  
drop table account_emailconfirmation cascade;  
drop table auth_group cascade;  
drop table auth_group_permissions cascade;  
drop table auth_permission cascade;  
drop table authtoken_token cascade;  
drop table django_admin_log cascade;  
drop table django_content_type cascade;  
drop table django_migrations cascade;  
drop table django_session cascade;  
drop table django_site cascade;  
drop table payment cascade;  
drop table socialaccount_socialaccount cascade;  
drop table socialaccount_socialapp cascade;  
drop table socialaccount_socialapp_sites cascade;  
drop table socialaccount_socialtoken cascade;  
drop table storages cascade;  
drop table users_users cascade;  
drop table users_users_groups cascade;  
drop table users_users_user_permissions cascade;  
drop table projects cascade;  
drop table imgs cascade;  
drop table token_blacklist_blacklistedtoken cascade;  
drop table token_blacklist_outstandingtoken cascade;  
drop table timeseries cascade;  
drop table timeseries_relation cascade;  
drop table "d2Layers" cascade;  
drop table mosaic cascade;  
drop table "d3Layers" cascade;  
drop table d3object cascade;  
drop table mtl cascade;  
drop table texture cascade;  
drop table video cascade;  
drop table "etcFiles" cascade;  