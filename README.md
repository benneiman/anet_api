# Athletic.net API Wrapper
This repo wraps select Athletic.net endpoints to make it easier to query their data. 

### Start up
Assuming you have postgres installed locally, first create the db:
```
> createdb anet_results
```
Then migrate the schema from inside the pipenv shell:
```
> pipenv shell
> cd db/
> alembic upgrade head
```
Finally start the app:
```
> cd ..
> uvicorn main:app --reload
```
and try it out!