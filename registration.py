import calendar
import datetime
import json
import random

from datetime import datetime, timedelta
from data.data import PI5_DATA
from data.database import DatabaseManager
from data.json_data_manager import JSONData, DateEncoder


MEMBERSHIP_DATA = 'data/memebrship_data.json'
ID_CARD_DATA = 'data/gym_id_card.json'
LOCKERS_DATA = 'data/lockers.json'


class RegistrationDataGenerator:
    def __init__(self) -> None:
        self.names = PI5_DATA['names']
        self.surname = PI5_DATA['surnames']
        self.gender = ''
        self.address = PI5_DATA['addresses']
        self.database = DatabaseManager('mysql')
        self.user_data = self.database.read_data("P3_user")

    def generate_new_member_id(self):
        """
        Generates a unique new gym member ID.

        Returns:
        str: The generated member ID.

        Usage:
        ```
        new_member_id = GymRegistration().generate_new_member_id()
        print(new_member_id)
        ```

        """
        data = [int(x[0]) for x in self.user_data]
        max_id = max(data) + 1 if data else 1
        new_user_id = f"{max_id:03d}"
        return new_user_id

    def generate_name(self):
        random_number = random.randint(0, len(self.names)-1)
        name = self.names[random_number][0]
        self.gender = self.names[random_number][1]
        return name

    def generate_surname(self):
        random_number = random.randint(0, len(self.surname)-1)
        surname = self.surname[random_number]
        return surname

    def generate_address(self):
        random_number = random.randint(0, len(self.address)-1)
        address = self.address[random_number]
        return address

    def generate_document_id(self):
        random_number = random.randint(0, 999999999)
        random_string = str(random_number).zfill(9)
        return random_string

    def generate_jmbg(self):
        year = random.randint(1970, 2003)
        month = random.randint(1, 12)
        max_days = calendar.monthrange(year, month)[1]
        day = random.randint(1, max_days)
        last_three_digits_of_year = year % 1000
        formatted_date = f"{day:02d}{month:02d}{last_three_digits_of_year:03d}"

        last_random_number = random.randint(0, 999999)
        last_random_string = str(last_random_number).zfill(6)

        return formatted_date + last_random_string

    def generate_member_data(self):
        gym_registration_data = []
        gym_registration_data = [
            self.generate_new_member_id(),
            self.generate_name(),
            self.generate_surname(),
            self.gender,
            self.generate_address(),
            'Novi Sad',
            self.generate_document_id(),
            self.generate_jmbg()
        ]
        return gym_registration_data


class RegisteredUsers:
    def __init__(self) -> None:
        self.database = DatabaseManager('mysql')
        self.user_data = self.database.read_data("P3_user")
        self.membership_data = self.database.read_data("P3_user_log")

    def users_ids(self):
        return [id[0] for id in self.user_data]
    
    def is_user_active(self, member_id):
        try:
            user_log_data = [log_data for log_data in self.membership_data if log_data[0] == member_id]
            json_data = user_log_data[0][1]
            parsed_data = json.loads(json_data)
            max_key = max(parsed_data, key=lambda key: parsed_data[key].get("membership_valid_to"))

            highest_membership_valid_to = parsed_data[max_key]["membership_valid_to"]
            date_to_compare = datetime.strptime(highest_membership_valid_to, "%Y-%m-%d")
            current_date = datetime.now()

            if date_to_compare > current_date:
                return True
            else:
                return False

        except (IndexError, ValueError, KeyError):
            return False
        
    def display_table_data(self):
        member_data = self.user_data
        member_ids = self.users_ids()

        table_data = []
        for idx, member_id in enumerate(member_ids):
            if member_id == member_data[idx][0]:
                name = (member_data[idx][1] + ' ' + member_data[idx][2])
                table_data.append([member_id, name, self.is_user_active(member_id)])

        return table_data


class GymRegistration:
    def __init__(self):
       self.database = DatabaseManager('mysql')

    def register_member(self, user_id: str, name: str, surname: str, gender: str, address: str, city: str, document_id: str, jmbg: str):
        """
        Method for gym member registration

        Returns: 
        str: A confirmation message indicating that the user is registered.

        Usage:
        ```
        gym_member_registration = GymRegistration().register_member('Sanja',  'Petrovic', 'F', 'adresa', 'grad', '123456789', '0505995100100', )
        print(gym_member_registration)
        ```

        """

        sql_query = f"INSERT INTO P3_user (user_id, name, surname, gender, address, city, document_id, JMBG) " \
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        data = (user_id, name, surname, gender, address, city, document_id, jmbg)
        self.database.save_data(sql_query, data)

        return f"{name} {surname} is registered"

