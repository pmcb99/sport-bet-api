# 888 Technical Test

Download Image:
https://hub.docker.com/repository/docker/paulmcbrien99/888techtest/general

Run using docker run.
Or run using python3 server/app.py in app dir.

# NOTES:
Instructions required use of raw SQL instead of ORM operations. SQLAlchemy has ORM functionality,
but also allows direct interaction with the database using raw SQL - "for applications that are built around direct usage of textual SQL statements and/or SQL expression constructs without involvement by the ORM’s higher level management services".


An alternative to this would be using another SQL module, but these have almost identical methods like all() or fetchone().
So to avoid adding another module, SQLAlchemy is preferred.