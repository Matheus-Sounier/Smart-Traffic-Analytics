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
    try:
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
    except oracledb.DatabaseError as e:
        error, = e.args
        if error.code == 955:  # ORA-00955
            print("Table DETECTED_PLATES already exists, continuing...")
        else:
            raise
    finally:
        cursor.close()
        conn.close()

def save_to_database(license_plates, start_time, end_time):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        insert_sql = '''
            INSERT INTO DETECTED_PLATES (plate_number, is_valid, detected_at, left_at, plate_image)
            VALUES (:1, :2, :3, :4, :5)
        '''
        rows = [
            (plate, 'Y' if is_valid else 'N', start_time, end_time, image)
            for plate, is_valid, image in license_plates
        ]
        cursor.executemany(insert_sql, rows)
        conn.commit()
    except oracledb.DatabaseError as e:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()