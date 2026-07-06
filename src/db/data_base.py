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
                score        NUMBER(3,2)   DEFAULT 0.0 NOT NULL,
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


def init_simulated_calendar_table():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            CREATE TABLE simulated_calendar (
                calendar_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                simulated_day DATE,
                simulated_start_time timestamp,
                simulated_end_time timestamp
            )
        ''')
        print("Table simulated_calendar's created.")
    except oracledb.DatabaseError as e:
        error, = e.args
        if error.code == 955:  # ORA-00955
            print("Table simulated_calendar already exists, continuing...")
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
            INSERT INTO DETECTED_PLATES (plate_number, is_valid, score, detected_at, left_at, plate_image)
            VALUES (:1, :2, :3, :4, :5, :6)
        '''
        rows = [
            (plate, 'Y' if is_valid else 'N', score, start_time, end_time, image)
            for plate, is_valid, score, image in license_plates
        ]
        cursor.executemany(insert_sql, rows)
        conn.commit()
    except oracledb.DatabaseError as e:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def create_simulated_calendar():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        create_simulated_calendar_sql = '''
            INSERT INTO simulated_calendar (
                simulated_day,
                simulated_start_time,
                simulated_end_time
            )
            SELECT
                DATE '2026-06-01' + (LEVEL - 1),
                TO_TIMESTAMP('2026-06-28 12:40:00',
                            'YYYY-MM-DD HH24:MI:SS')
                    + NUMTODSINTERVAL((LEVEL - 1) * 20, 'MINUTE'),
                TO_TIMESTAMP('2026-06-28 12:40:00',
                            'YYYY-MM-DD HH24:MI:SS')
                    + NUMTODSINTERVAL(LEVEL * 20, 'MINUTE')
            FROM dual
            CONNECT BY LEVEL <= 30
        '''
        cursor.execute(create_simulated_calendar_sql)
        conn.commit()
    except oracledb.DatabaseError as e:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()