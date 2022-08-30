from environs import Env

env = Env()
env.read_env()

IP = env.str("DBHOST")
USER = env.str("USER")
PASSWORD = env.str("PASSWORD")
DBNAME = env.str("DBNAME")
DB_PORT = env.str("DB_PORT")
SERVER_PORT = env.str("SERVER_PORT")
CLEAR_DB = True
