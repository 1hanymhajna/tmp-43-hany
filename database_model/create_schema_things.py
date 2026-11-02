"""Create and access a small PostgreSQL ``things`` table."""

import json
import os

import psycopg2


def connect_to_postgres():
	"""Connect using the standard PostgreSQL PG* environment variables."""
	return psycopg2.connect(
		host=os.getenv("PGHOST", "localhost"),
		port=os.getenv("PGPORT", "5432"),
		dbname=os.getenv("PGDATABASE", "postgres"),
		user=os.getenv("PGUSER", "postgres"),
		password=os.getenv("PGPASSWORD", ""),
	)


def initialize_database(connection):
	"""Create the application schema and table if they do not exist."""
	with connection.cursor() as cursor:
		cursor.execute('CREATE SCHEMA IF NOT EXISTS "things"')
		cursor.execute(
			'''CREATE TABLE IF NOT EXISTS "things"."things" (
				id BIGSERIAL PRIMARY KEY,
				name TEXT NOT NULL,
				data JSONB NOT NULL DEFAULT '{}'::jsonb,
				created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
			)'''
		)
	connection.commit()


def write_thing(connection, name, data=None):
	"""Insert a thing and return its generated ID."""
	try:
		with connection.cursor() as cursor:
			cursor.execute(
				'INSERT INTO "things"."things" (name, data) '
				'VALUES (%s, %s::jsonb) RETURNING id',
				(name, json.dumps(data if data is not None else {})),
			)
			thing_id = cursor.fetchone()[0]
		connection.commit()
		return thing_id
	except Exception:
		connection.rollback()
		raise


def read_thing(connection, thing_id):
	"""Return a thing by ID, or None if it does not exist."""
	with connection.cursor() as cursor:
		cursor.execute(
			'SELECT id, name, data, created_at FROM "things"."things" WHERE id = %s',
			(thing_id,),
		)
		row = cursor.fetchone()
	if row is None:
		return None
	return {"id": row[0], "name": row[1], "data": row[2], "created_at": row[3]}


def read_things(connection):
	"""Return all things ordered by ID."""
	with connection.cursor() as cursor:
		cursor.execute(
			'SELECT id, name, data, created_at FROM "things"."things" ORDER BY id'
		)
		rows = cursor.fetchall()
	return [
		{"id": row[0], "name": row[1], "data": row[2], "created_at": row[3]}
		for row in rows
	]
