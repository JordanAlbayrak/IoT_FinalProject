from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, Float, String, MetaData
from datetime import datetime

engine = create_engine('sqlite:///temp')
temperature_t = "temperature"
humidity_t = "humidity"

def create_tables():
	try:
		meta = MetaData()
		temperature = Table(temperature_t, meta, Column('id', Integer, primary_key=True), Column('taken_at', String(255)), Column('temperature', Float))
		humidity = Table(humidity_t, meta, Column('id', Integer, primary_key=True), Column('taken_at', String(255)), Column('humidity', Float))
		meta.create_all(engine)
		print("Tables created")
	except Exception as e:
		print(e)

def insert_into(table, col, val, taken_at):
	with engine.connect() as con:
		try:
			q = f"INSERT INTO {table}(taken_at, {col}) VALUES('{taken_at}', {val})"
			print(q)
			con.execute(q)
		except Exception as e:
			print(e)


def insert_into_humidity(humidity, taken_at=datetime.now()):
	insert_into(humidity_t, "humidity", humidity, taken_at)


def insert_into_temperature(temperature, taken_at=datetime.now()):
	print(temperature, taken_at)
	insert_into(temperature_t, "temperature", temperature, taken_at)


def get_all_raw_from(table, on_fetch):
	q = f"SELECT * FROM {table}"
	print(q)
	with engine.connect() as con:
		try:
			res = con.execute(q)
		except Exception as e:
			print(e)
		else:
			return on_fetch(res)
	return None


def get_all_humidity():
	return get_all_raw_from(humidity_t, lambda res: [{"taken_at": row[1], "humidity": row[2]} for row in res])


def get_all_temperature():
	return get_all_raw_from(temperature_t, lambda res: [{"taken_at": row[1], "temperature": row[2]} for row in res])


def purge_all():
	ts = [temperature_t, humidity_t]
	with engine.connect() as con:
		try:
			for t in ts:
				q = f"DELETE FROM {t}"
				print(q)
				res = con.execute(q)
		except Exception as e:
			print(e)
		else:
			return res
	return None



