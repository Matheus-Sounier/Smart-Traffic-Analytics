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


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE DETECTED_PLATES (
            id           NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            plate_number VARCHAR2(10)  NOT NULL,
            is_valid     CHAR(1)       DEFAULT 'N' NOT NULL,
            detected_at  TIMESTAMP     NOT NULL,
            left_at      TIMESTAMP,
            plate_image  BLOB
        )
    ''')
    print("table DETECTED_PLATES's created.")