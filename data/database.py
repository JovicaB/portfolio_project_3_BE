import MySQLdb
import os
import psycopg2

from abc import ABC, abstractmethod


class SingletonDatabase(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):

        """
        Implement a singleton pattern for database connections.

        Parameters:
        - cls: The class being instantiated.
        - args: Positional arguments.
        - kwargs: Keyword arguments.

        Returns:
        The existing instance of the class if it exists, or a new instance if it doesn't.
        """

        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonDatabase, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DatabaseConnection(ABC):
    @abstractmethod
    def connect(self):

        """
        Abstract method to establish a database connection.
        """

        pass

    @abstractmethod
    def close(self):

        """
        Abstract method to close a database connection.
        """

        pass

class Database(ABC):
    def __init__(self, connection):
        self.connection = connection

    @abstractmethod
    def read_data(self, table_name):

        """
        Abstract method to read data from a database table.

        Parameters:
        - table_name (str): The name of the database table.

        Returns:
        The retrieved data.
        """

        pass

    @abstractmethod
    def save_data(self, sql_query, data):

        """
        Abstract method to save data to the database.

        Parameters:
        - sql_query (str): The SQL query for saving data.
        - data (tuple): The data to be saved.

        Returns:
        None if successful, or an error message if an exception occurs.
        """

        pass


class MySqlConnection(DatabaseConnection):

    def connect(self):

        """
        Establish a MySQL database connection.

        Returns:
        The MySQL database connection.
        """

        connection = MySQLdb.connect(
            host = os.environ.get('MYSQL_DB_HOST'),
            user="admin",
            password = os.environ.get('MYSQL_DB_PASSWORD'),
            database="portfolio",
            port=10093,
            charset='utf8mb4'
        )
        return connection

    def close(self, connection):
        if connection:
            connection.close()


class PostgresqlConnection(DatabaseConnection):

    def connect(self):

        """
        Establish a PostgreSQL database connection.

        Parameters:
        - dbname (str): The name of the database.
        - user (str): The database user.
        - password (str): The user's password.
        - host (str): The database host.
        - port (int): The database port.

        Returns:
        The PostgreSQL database connection.
        """

        connection = psycopg2.connect(
            host = os.environ.get('POSTGRESS_DB_HOST'),
            user="admin",
            password = os.environ.get('POSTGRESS_DB_PASSWORD'),
            database="portfolio",
            port=5432,
            charset='utf8mb4'
        )

        return connection

    def close(self, connection):
        if connection:
            connection.close()


class DatabaseManager(metaclass=SingletonDatabase):

    def __init__(self, connection_type):

        """
        Initialize a DatabaseManager with a specified connection type.

        Parameters:
        - connection_type (str): The type of database connection ('mysql' or 'postgresql').
        """

        self.connection = self.create_connection(connection_type)

    def create_connection(self, connection_type):

        """
        Create a database connection based on the specified connection type.

        Parameters:
        - connection_type (str): The type of database connection ('mysql' or 'postgresql').

        Returns:
        An instance of the appropriate DatabaseConnection subclass based on the connection type.
        
        Raises:
        ValueError: If an unsupported database connection type is provided.
        """
        
        if connection_type == 'mysql':
            return MySqlConnection()
        elif connection_type == 'postgresql':
            return PostgresqlConnection()
        else:
            raise ValueError("Unsupported database connection type")

    def read_data(self, table_name):

        """
        Read data from a specified database table.

        Parameters:
        - table_name (str): The name of the database table to read from.

        Returns:
        The retrieved data from the specified table.
        """

        connection = self.connection.connect()
        cursor = connection.cursor()
        sql = f"SELECT * FROM {table_name}"
        cursor.execute(sql)
        data = cursor.fetchall()
        connection.close()
        return data

      def read_data_sql_query(self, sql_query):
        """
        Read data from the database using a custom SQL query.

        This method establishes a database connection, executes the provided SQL query, and retrieves the data from the database.

        Parameters:
        - sql_query (str): The SQL query to retrieve data from the database.

        Returns:
        A list of tuples containing the retrieved data from the database.

        Example:
        >>> sql_query = "SELECT * FROM my_table WHERE category = 'A'"
        >>> data = database_manager.read_data_sql_query(sql_query)
        >>> print(data)
        [(1, 'Item A', 'A'), (2, 'Item B', 'A'), ...]

        Note:
        - The method is intended for reading data from the database using custom SQL queries.
        - The SQL query should be a valid query that is appropriate for the specific database system (MySQL, PostgreSQL, etc.).
        - Make sure to handle exceptions appropriately when using this method.

        """
        connection = self.connection.connect()
        cursor = connection.cursor()
        cursor.execute(sql_query)
        data = cursor.fetchall()
        connection.close()
        return data
        
    def save_data(self, sql_query, data):

        """
        Save data to the database using a provided SQL query and data.

        Parameters:
        - sql_query (str): The SQL query for saving data.
        - data (tuple): The data to be saved.

        Returns:
        None if successful, or an error message if an exception occurs.
        """

        try:
            connection = self.connection.connect()
            cursor = connection.cursor()
            cursor.execute(sql_query, data)
            connection.commit()
            connection.close()
        except Exception as e:
            print(f"An error occurred while saving the data to the database: {e}")
            return None

        return None
