import oracledb

from decouple import config


def get_connection():
    return oracledb.connect(
        user=config('USER'),
        password=config('ORACLE_PWD'),
        host=config('ORACLE_HOSTNAME'),
        port=config('PORT'),
        service_name=config('SERVICE_NAME')
    )