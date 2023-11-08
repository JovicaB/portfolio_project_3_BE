import datetime
import json

from datetime import datetime, timedelta
from data.data import PI5_DATA
from data.database import DatabaseManager
from data.json_data_manager import JSONData, DateEncoder


class GymMembershipData:
    def __init__(self, ticket_type: str):
        self.ticket_type = ticket_type
        self.json_filename = MEMBERSHIP_DATA
        
    def get_membership_price(self):
        """
        Gets membership price for the choosen period

        Returns: 
        float: membership price for the choosen membership period

        Usage:
        ```
        membership_price = GymMembershipData().get_membership_price('3_months'))
        print(membership_price)
        ```

        """
        json_data = JSONData(self.json_filename).read_json(self.ticket_type)
        return json_data['price']
    
    def get_membership_duration(self):
        """
        gets membership duration from choosen membership type

        Returns: 
        int: duration of membership type in days

        Usage:
        ```
        membership_duration = GymMembershipData().get_membership_duration('3_months'))
        print(membership_duration)
        ```

        """
        json_data = JSONData(self.json_filename).read_json(self.ticket_type)
        return json_data['duration']
    

class PaymentProcessor:
    def __init__(self):
        self.database = DatabaseManager('mysql')
        self.membership_log = {'payment_date':'', 'membership_type':'', 'sum_payed':0, 'membership_valid_to': ''}
        self.data_log = {}

    def get_member_user_id(self, jmbg: str) -> str: 
        """
        gets user_id from the database based on user JMBG

        Returns: 
        str: user ID

        Usage:
        ```
        user_id = PaymentProcess().get_member_user_id('0505982700700'))
        print(user_id)
        ```

        """
        member_id = self.database.read_data_sql_query(f"SELECT user_id from user WHERE JMBG = '{jmbg}'")
        return member_id[0][0]
       
    def get_membership_log_key(self, user_id: str):
        """
        gets actual membership log key [log for payment]

        Returns: 
        int: membership log key

        Usage:
        ```
        membership_log_key = PaymentProcess().get_membership_log_key('001'))
        print(membership_log_key)
        ```

        """
        data = self.database.read_data_sql_query("SELECT membership_log from P3_user_log WHERE user_id = %s" % user_id)
        if data == ():
            self.data_log = {}
            return 1
        else:
            self.data_log =  json.loads(data[0][0])
            converted_dict = {int(key): value for key, value in self.data_log.items()}
            return max(converted_dict, key=int) + 1

    def set_membership_log(self, membership_type: str, sum: float):
        """
        sets new membership log when user pays for membership

        Returns: 
        dict: new membership log

        Usage:
        ```
        membership_log = PaymentProcess().set_membership_log('3_months', 12000))
        print(membership_log)
        ```

        """
        todays_date = datetime.now().date()
        membership_type_duration = GymMembershipData(membership_type).get_membership_duration()
        membership_valid_to = todays_date + timedelta(days=membership_type_duration)

        self.membership_log['payment_date'] = todays_date
        self.membership_log['membership_type'] = membership_type
        self.membership_log['sum_payed'] = sum
        self.membership_log['membership_valid_to'] = membership_valid_to

        return self.membership_log

    def register_payment(self, user_id: str, membership_type: str, sum: float):
        """
        registers membership payment and stores generated new membership payment log

        Returns: 
        str: A confirmation message indicating that the payment is finished.

        Usage:
        ```
        membership_log = PaymentProcess().set_membership_log('3_months', 12000))
        print(membership_log)
        ```

        """
        membership_key = self.get_membership_log_key(user_id)
        membership_log_data = self.set_membership_log(membership_type, sum)
        self.data_log.update({membership_key: membership_log_data})
        log = json.dumps(self.data_log, cls=DateEncoder)
        
        if membership_key == 1:
            sql_query = f"INSERT INTO P3_user_log (user_id, membership_log) VALUES (%s, %s)"
            data = (user_id, log)
        else:
            sql_query = "UPDATE P3_user_log SET membership_log = %s WHERE user_id = %s"
            data = (log, user_id)

        self.database.save_data(sql_query, data)

        return f'Payment for the member id {user_id} is finished'


class LogExtractor:
    def __init__(self, log_type: str = 'M'):
        """
        Initialize a LogExtractor instance.

        Parameters:
        - log_type (str, optional): The type of logs to extract. Defaults to 'M'.
          
          - 'M': Extracts membership logs.
          - 'A': Extracts access logs.

        Raises:
        - ValueError: If log_type is not 'M' or 'A'.
        """
        if log_type not in ('M', 'A'):
            raise ValueError("log_type must be 'M' or 'A'")
        
        self.database = DatabaseManager('mysql')
        self.log_type = log_type
        
        if log_type == 'M':
            self.user_data = self.database.read_data_sql_query("SELECT user_id, membership_log from P3_user_log")
        else:
            self.user_data = self.database.read_data_sql_query("SELECT user_id, access_log from P3_user_log")
        
        self.last_log_main_key = None

    def get_complete_log(self):
        """
        Extracts complete membership or access log data depending on the class parameters.

        Returns: 
        list: Raw log data.

        Usage:
        ```
        log = LogExtractor('M').get_log()
        print(log)
        ```
        """
        raw_data = self.user_data
        return raw_data

    def get_member_log(self, user_id: str, full_log: bool):
        """
        Extracts membership or access log data for a specific user.

        Parameters:
        - user_id (str): Gym member ID.
        - full_log (bool): If True, return the full log data. If False, return the last membership or access session data.

        Returns: 
        dict: Gym member's log data.

        Usage:
        ```
        member_log = LogExtractor().get_member_log('001', full_log=True)
        print(member_log)
        ```
        """
        raw_data = self.user_data
        
        raw_user_data = [element for element in raw_data if element[0] == user_id][0]
        if raw_user_data[1] == None:
            return f"There is no log for member with ID {user_id}"
        else:
            user_data_json = [json.loads(element[1]) for element in raw_data if element[0] == user_id][0]
            user_data = {int(k): v for k, v in user_data_json.items()}
            if full_log:
                return user_data
            else:
                last_session = user_data.popitem()
                self.last_log_main_key = last_session[0]
                return last_session
        
    def get_last_log_main_key(self, user_id: str):
        """
        Extracts the key of the last log session for a specific member.

        Parameters:
        - user_id (str): Gym member ID.

        Returns: 
        int: The key of the last log session.

        Usage:
        ```
        last_key = LogExtractor('A').get_last_log_key('001')
        print(last_key)
        ```
        """
        last_session = self.get_member_log(user_id, False)
        if self.last_log_main_key == None:
            return 0
        else:
            return self.last_log_main_key
    
    def get_last_log_key_value(self, user_id: str, key):
        """
        Extracts the value from last log session for a specific member based on a key.
        Method checks if value is data JSON string and converts it to date

        Parameters:
        - user_id (str): Gym member ID, key: dictionary value key of the last gym session

        Returns: 
        dictionary value: from the provided dictionary key

        Usage:
        ```
        dict_value = LogExtractor('M').get_last_log_key_value('001', 'membership_valid_to')
        print(dict_value)
        ```
        """
        last_session_data = self.get_member_log(user_id, False)[1]
        value = last_session_data.get(key)

        try:
            date_format = "%Y-%m-%d"
            parsed_date = datetime.strptime(value, date_format)
            return parsed_date
        except (json.JSONDecodeError, ValueError):
            return value


class SetMemberIDCard:
    def __init__(self):
        self.filename = ID_CARD_DATA
    
    def create_gym_id_card_file(self):
        """
        Create a new gym ID card JSON file with default data.

        Returns:
        str: Confirmation message if the file is created successfully.

        Usage:
        ```
        id_card = SetMemberIDCard()
        result = id_card.create_gym_id_card_file()
        print(result)
        ```
        """
        file_path = self.filename
        data = {
            "userID": None,
            "hasAccess": False,
            "lockerNumber": None,
            "access_log": {"entrance_timestamp": None, "exit_timestamp": None}
        }

        try:
            with open(file_path, "w") as json_file:
                json.dump(data, json_file, indent=4)
            return f"File '{file_path}' created successfully."
        except Exception as e:
            return f"Error creating file '{file_path}': {e}"
        
    def set_member_id(self, user_id: str):
        """
        Set the user's membership ID in the gym ID card data.

        Parameters:
        - user_id (str): The user's membership ID.

        Returns:
        str: Confirmation message after updating the data.

        Usage:
        ```
        id_card = SetMemberIDCard()
        result = id_card.set_member_id('001')
        print(result)
        ```
        """
        return JSONData(self.filename).write_json(["userID"], user_id)
    
    def set_access(self, access: bool):
        """
        Set the access status in the gym ID card data.

        Parameters:
        - access (bool): True if the user has access, False otherwise.

        Returns:
        str: Confirmation message after updating the data.

        Usage:
        ```
        id_card = SetMemberIDCard()
        result = id_card.set_access(True)
        print(result)
        ```
        """
        return JSONData(self.filename).write_json(["hasAccess"], access)
    
    def set_locker(self, locker: int):
        """
        Set the locker number in the gym ID card data.

        Parameters:
        - locker (int): The locker number.

        Returns:
        str: Confirmation message after updating the data.

        Usage:
        ```
        id_card = SetMemberIDCard()
        result = id_card.set_locker(123)
        print(result)
        ```
        """
        return JSONData(self.filename).write_json(["lockerNumber"], locker)

    def set_access_log_timestamp(self, key: str):
        """
        Set the entrance or exit timestamp in the gym ID card's access log.

        Parameters:
        - key (str): The type of timestamp, either 'entrance_timestamp' or 'exit_timestamp'.

        Returns:
        str: Confirmation message after updating the data.

        Usage:
        ```
        id_card = SetMemberIDCard()
        result = id_card.set_access_log_timestamp('entrance_timestamp')
        print(result)
        ```
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return JSONData(self.filename).write_json(["access_log", key], now)


class GetMemberIDCardData:
    def __init__(self):
        self.filename = ID_CARD_DATA

    def get_member_id(self):
        """
        Get the user's membership ID from the ID card data.

        Returns:
        str: The user's membership ID.

        Usage:
        ```
        member_id = GetMemberIDCardData().get_member_id()
        print(member_id)
        ```
        """
        return JSONData(self.filename).read_json("userID")
    
    def get_member_access_status(self):
        """
        Get the access status of the user from the ID card data.

        Returns:
        bool: True if the user has access, False otherwise.

        Usage:
        ```
        access_status = GetMemberIDCardData().get_member_access_status()
        print(access_status)
        ```
        """
        return JSONData(self.filename).read_json("hasAccess")
    
    def get_member_locker_number(self):
        """
        Get the locker number assigned to the user from the ID card data.

        Returns:
        str or None: The locker number if assigned, or None if not.

        Usage:
        ```
        locker_number = GetMemberIDCardData().get_member_locker_number()
        if locker_number is not None:
            print(f"Locker Number: {locker_number}")
        else:
            print("No locker assigned.")
        ```
        """
        return JSONData(self.filename).read_json("lockerNumber")

    def get_member_access_log(self):
        """
        On exit after exit timestamp has been set this method returns complete access log to be written to DB.

        Returns:
        dict: access log.

        Usage:
        ```
        member_access_log = GetMemberIDCardData().get_member_access_log()
        print(member_access_log)
        ```
        """
        return JSONData(self.filename).read_json("access_log")
  
