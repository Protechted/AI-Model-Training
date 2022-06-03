import psycopg2

CONNECTION = "postgres://postgres:EbHVP7KzkkazeC4WMtUUHAjPFWaYq9nsKk9nzfvj9XdM5ZLLZhW@1aefeea9-b1df-42f2-873a-ed9538cc798e.ma.bw-cloud-instance.org:6744/postgres"

def main():
    with psycopg2.connect(CONNECTION) as conn:
        cursor = conn.cursor()
        # use the cursor to interact with your database
        # cursor.execute("SELECT * FROM table")

        ax, ay, az, gx, gy, gz, qx, qy, qz, qw, p = 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1
        subject = "test"
        label = 0

        SQL = f"INSERT INTO data (subject, ax, ay, az, gx, gy, gz, qx, qy, qz, qw, p, label) VALUES ('{subject}', {ax}, {ay}, {az}, {gx}, {gy}, {gz}, {qx}, {qy}, {qz}, {qw}, {p}, {label});"

        try:
            cursor.execute(SQL)
        except (Exception, psycopg2.Error) as error:
            print(error.pgerror)
        conn.commit()

if __name__ == "__main__":
    main()