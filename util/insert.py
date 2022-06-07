import psycopg2
import pandas as pd

def insert_data(data_df: pd.DataFrame, label: str, subject: str = "test"):

    CONNECTION = "postgres://postgres:EbHVP7KzkkazeC4WMtUUHAjPFWaYq9nsKk9nzfvj9XdM5ZLLZhW@1aefeea9-b1df-42f2-873a-ed9538cc798e.ma.bw-cloud-instance.org:6744/postgres"

    #df = pd.read_csv("data/test.csv")
    df = data_df

    with psycopg2.connect(CONNECTION) as conn:
        cursor = conn.cursor()

        SQL_SAMPLE = "INSERT INTO samples (subject, label) VALUES (%s, %s) RETURNING sample_id;"

        try:
            cursor.execute(SQL_SAMPLE, (subject, label))
            print("Sample inserted")
            sample_id = cursor.fetchone()[0]

        except (Exception, psycopg2.Error) as error:
                print(error.pgerror)

        for index, row in df.iterrows():
            ax, ay, az, gx, gy, gz, qx, qy, qz, qw, p = row["ax"], row["ay"], row["az"], row["gx"], row["gy"], row["gz"], row["qx"], row["qy"], row["qz"], row["qw"], row["p"]
            SQL_DATA = "INSERT INTO data (ax, ay, az, gx, gy, gz, qx, qy, qz, qw, p, sample_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
            try:
                cursor.execute(SQL_DATA, (ax, ay, az, gx, gy, gz, qx, qy, qz, qw, p, sample_id))
            except (Exception, psycopg2.Error) as error:
                print(error.pgerror)
            conn.commit()

        print("Data inserted")
