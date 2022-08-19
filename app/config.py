from environs import Env

env = Env()
env.read_env()

IP = env.str('DBHOST')
PORT = env.str('PORT')
USER = env.str('USER')
PASSWORD = env.str('PASSWORD')
DBNAME = env.str('DBNAME')
CLEAR_DB = True






