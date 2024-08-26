import mysql.connector
from uuid import uuid4
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
load_dotenv()

# Now you can access the environment variables using os.getenv
# main_guild_id = int(os.getenv('MAIN_GUILD_ID'))
class SQLChallengeDatabase:
    challenge_ids = []
    HOST = os.getenv('HOST').strip()       # Usually 'localhost' or an IP address
    USER = os.getenv('USER_AWS').strip()
    PASSWORD = os.getenv('PASSWORD').strip()
    DATABASE = os.getenv('DATABASE').strip()

    @staticmethod
    def get_connection():
        return mysql.connector.connect(
            host=SQLChallengeDatabase.HOST,
            user=SQLChallengeDatabase.USER,
            password=SQLChallengeDatabase.PASSWORD,
            database=SQLChallengeDatabase.DATABASE
        )

    @staticmethod
    async def create_challenge(user_id1, user_id2, date, price, wallet, server_id, task_id):
        try:
            # Convert the date from DD-MM-YYYY to YYYY-MM-DD
            date_obj = datetime.strptime(str(date), '%d-%m-%Y')
            formatted_date = date_obj.strftime('%Y-%m-%d')  # Format the date in the correct format for SQL
        except ValueError as e:
            # Log the error and perhaps return or handle it
            print(f"Date format error: {e}")
            return None  # or raise an exception, or handle it as per your application logic

        challenge_id = str(uuid4())
        conn = SQLChallengeDatabase.get_connection()
        cursor = conn.cursor()
        query = """
        INSERT INTO challenges (challenge_id, user_id1, user_id2, date, price, status, channel_created, wallet, server_id, task_id) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        cursor.execute(query, (challenge_id, user_id1, user_id2, formatted_date, price, 0, 0, wallet, server_id, task_id))
        conn.commit()
        cursor.close()
        conn.close()
        return challenge_id

    @staticmethod
    async def get_challenge(challenge_id):
        conn = SQLChallengeDatabase.get_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM challenges WHERE challenge_id = %s;"
        cursor.execute(query, (challenge_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result

    @staticmethod
    def accept_challenge(challenge_id):
        conn = SQLChallengeDatabase.get_connection()
        cursor = conn.cursor()
        query = "UPDATE challenges SET accept = 1 WHERE challenge_id = %s;"
        cursor.execute(query, (challenge_id,))
        affected_rows = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        return affected_rows > 0


    @staticmethod
    async def update_channel_created(challenge_id):
        conn = SQLChallengeDatabase.get_connection()
        cursor = conn.cursor()
        query = "UPDATE challenges SET channel_created = 1 WHERE challenge_id = %s;"
        try:
            cursor.execute(query, (challenge_id,))
            conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return False
        finally:
            cursor.close()
            conn.close()


    @staticmethod
    async def get_leaderboard(period):
        if period not in ['week", "month']:
            raise ValueError("Period must be either 'week' or 'month'.")

        # Calculate the start date based on the given period
        today = datetime.today()
        if period == "week":
            start_date = today - timedelta(days=today.weekday())
        else:  # month
            start_date = today.replace(day=1)

        # Connect to the database
        conn = SQLChallengeDatabase.get_connection()
        cursor = conn.cursor(dictionary=True)

        print("Today: ", today)
        print("Week from today: ", start_date)
        # Fetch challenges and calculate leaderboard within the date range
        query = """
            SELECT
                p.name,
                SUM(c.price) AS points,
                p.user_picture
            FROM
                discord_bot.challenges c
            JOIN
                discord_bot.profiles p ON c.user_id2 = p.user_id
            WHERE
                c.date >= %s
            GROUP BY
                c.user_id2
            ORDER BY
                points DESC
            LIMIT 50;
        """
        cursor.execute(query, (start_date,))
        leaderboard = cursor.fetchall()

        # Close the database connection
        cursor.close()
        conn.close()

        return leaderboard


