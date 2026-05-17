import sys
import sqlite3
import hashlib
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QMessageBox, QTableWidgetItem
from PyQt5.uic import loadUi
from database import (
    delete_all_data,
    fetch_adopters,
    fetch_adoptions,
    fetch_animal_ids,
    fetch_animals,
    fetch_available_animal_ids,
    fetch_available_adopter_ids,
    fetch_health_records,
    initialize_database,
    insert_adopter,
    insert_adoption,
    insert_animal,
    insert_health_record,
)

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"

class LoginWindow(QDialog):
    def __init__(self):
        super(LoginWindow, self).__init__()
        loadUi("login.ui", self)
        self.acc_error.hide()
        self.login_button.clicked.connect(self.handle_login)
    def handle_login(self):
        username_input = self.input_username.text()
        password_input = self.input_password.text()
        hashed_input = hashlib.sha256(password_input.encode()).hexdigest()
        #Compare with our authorized credentials
        if username_input == ADMIN_USERNAME and hashed_input == ADMIN_PASSWORD_HASH:
            print("Login Successful!")
            self.accept()
        else:
            print("Login Failed!")
            self.acc_error.show()
            self.input_password.clear()
class ConfirmWindow_animal(QDialog):
    def __init__(self, target, rec_id, rec_name, rec_age, rec_breed, rec_status, rec_species):
        super(ConfirmWindow_animal, self).__init__()
        loadUi("system_confirmation.ui", self)
        self.target_table.setText(f"<b>Target:</b> {target}")
        self.record_id.setText(f"<b>ID:</b> {rec_id}")
        self.record_name.setText(f"<b>Name:</b> {rec_name}")
        self.record_age.setText(f"<b>Age:</b> {rec_age}")
        self.record_breed.setText(f"<b>Breed:</b> {rec_breed}")
        self.record_species.setText(f"<b>Species:</b> {rec_species}")
        self.record_status.setText(f"<b>Status:</b> {rec_status}")
        self.confirm_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

class ConfirmWindow_adopterManagement(QDialog):
    def __init__(self, target, rec_id, rec_name, rec_age, rec_phone, rec_address, rec_status):
        super(ConfirmWindow_adopterManagement, self).__init__()
        loadUi("system_confirmation.ui", self)
        self.target_table.setText(f"<b>Target:</b> {target}")
        self.record_id.setText(f"<b>ID:</b> {rec_id}")
        self.record_name.setText(f"<b>Name:</b> {rec_name}")
        self.record_age.setText(f"<b>Age:</b> {rec_age}")
        self.record_species.setText(f"<b>Phone:</b> {rec_phone}")
        self.record_breed.setText(f"<b>Address:</b> {rec_address}")
        self.record_status.setText(f"<b>Status:</b> {rec_status}")
        self.confirm_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

class ConfirmWindow_adopterRecord(QDialog):
    def __init__(self, target, rec_id, rec_date, rec_fee, rec_animalID, rec_recAdopterID):
        super(ConfirmWindow_adopterRecord, self).__init__()
        loadUi("system_confirmation.ui", self)
        self.target_table.setText(f"<b>Target:</b> {target}")
        self.record_id.setText(f"<b>ID:</b> {rec_id}")
        self.record_name.setText(f"<b>Adoption Date:</b> {rec_date}")
        self.record_age.setText(f"<b>Fee Paid:</b> {rec_fee}")
        self.record_species.setText(f"<b>Animal ID:</b> {rec_animalID}")
        self.record_breed.setText(f"<b>Adopter ID:</b> {rec_recAdopterID}")
        self.record_status.hide()
        self.confirm_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

class ConfirmWindow_healthRecord(QDialog):
    def __init__(self, target, rec_animalID, rec_date, rec_procedure, rec_vet):
        super(ConfirmWindow_healthRecord, self).__init__()
        loadUi("system_confirmation.ui", self)
        self.target_table.setText(f"<b>Target:</b> {target}")
        self.record_id.setText(f"<b>Animal ID:</b> {rec_animalID}")
        self.record_name.setText(f"<b>Date Administered:</b> {rec_date}")
        self.record_age.setText(f"<b>Procedure:</b> {rec_procedure}")
        self.record_species.setText(f"<b>Veterinarian:</b> {rec_vet}")
        self.record_breed.hide()
        self.record_status.hide()
        self.confirm_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

class ConfirmWindow_delete(QDialog):
    def __init__(self):
        super(ConfirmWindow_delete, self).__init__()
        loadUi("delete.ui", self)
        self.confirm_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("main_window.ui", self)
        self.navigation_animal_button.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.navigation_adopter_button.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.navigation_records_button.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))
        self.navigation_health_button.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(3))
        self.Logout_button.clicked.connect(self.handle_logout)
        self.SaveButton.clicked.connect(self.save_animal_record)
        self.ClearButton.clicked.connect(self.clear_animal_form)
        self.save2.clicked.connect(self.save_adopter_management)
        self.clear2.clicked.connect(self.clear_adopter_form)
        self.save3.clicked.connect(self.save_adoption_record)
        self.clear3.clicked.connect(self.clear_adoption_form)
        self.btn_save_health.clicked.connect(self.save_health_record)
        self.btn_clear_health.clicked.connect(self.clear_health_form)
        self.btn_delete_record.clicked.connect(self.delete_database_records)
        self.adopter_status_by_id = {}
        self.setup_adoption_id_comboboxes()
        self.setup_date_widgets()
        self.load_database_records()

    def handle_logout(self):
        self.hide()
        self.login_window = LoginWindow()
        print("Logout Successfully")
        if self.login_window.exec_() == QDialog.Accepted:
            self.stackedWidget.setCurrentIndex(0)
            self.show()
        else:
            self.close()
            
    def check_empty_fields(self, fields_dict):
        for field in fields_dict:
            if fields_dict[field] == "":
                new_field = field.replace("_", " ").title()
                QMessageBox.warning(self, "Input Error", f"The '{new_field}' field cannot be empty!")
                return False
        return True

    def setup_adoption_id_comboboxes(self):
        self.animal_id_combox.clear()
        self.adopter_id_combox.clear()
        self.Health_animalid_combox.clear()
        self.animal_id_combox.addItem("-- Select Animal ID --", "")
        self.adopter_id_combox.addItem("-- Select Adopter ID --", "")
        self.Health_animalid_combox.addItem("-- Select Animal ID --", "")

    def load_database_records(self):
        self.load_tables()
        self.load_combobox_ids()

    def load_tables(self):
        self.load_table(self.table_animals, fetch_animals())
        self.load_table(self.table_adopters, fetch_adopters())
        self.load_table(self.table_adoptions, fetch_adoptions())
        self.load_table(self.table_health, fetch_health_records())

    def load_table(self, table, rows):
        table.setRowCount(0)
        for row_number, row_data in enumerate(rows):
            table.insertRow(row_number)
            for column_number, value in enumerate(row_data):
                table.setItem(row_number, column_number, QTableWidgetItem(str(value)))

    def load_combobox_ids(self):
        self.setup_adoption_id_comboboxes()
        for animal_id in fetch_available_animal_ids():
            self.add_combobox_id(self.animal_id_combox, animal_id)

        for animal_id in fetch_animal_ids():
            self.add_combobox_id(self.Health_animalid_combox, animal_id)

        for adopter_id in fetch_available_adopter_ids():
            self.add_combobox_id(self.adopter_id_combox, adopter_id)

    def setup_date_widgets(self):
        self.Adoption_Date.setDisplayFormat("MM/dd/yyyy")
        self.Health_date_edit.setDisplayFormat("MM/dd/yyyy")
        self.reset_date_widget(self.Adoption_Date)
        self.reset_date_widget(self.Health_date_edit)

    def add_combobox_id(self, combobox, record_id):
        if combobox.findData(record_id) == -1:
            combobox.addItem(record_id, record_id)

    def remove_combobox_id(self, combobox, record_id):
        index = combobox.findData(record_id)
        if index != -1:
            combobox.removeItem(index)

    def get_required_combobox_id(self, combobox, field_name):
        selected_id = combobox.currentData()
        if selected_id in (None, ""):
            QMessageBox.warning(self, "Input Error", f"Please select a valid {field_name}.")
            return None
        return selected_id

    def get_date_value(self, widget):
        return widget.date().toString("MM/dd/yyyy")

    def reset_date_widget(self, widget):
        widget.setDate(QDate.currentDate())

    def get_health_animal_id(self):
        return self.get_required_combobox_id(self.Health_animalid_combox, "Animal ID")

    def reset_health_animal_id(self):
        self.Health_animalid_combox.setCurrentIndex(0)

    def save_animal_record(self):
        animal_data = {
            "animal_id": self.AnimalID_ledit.text().strip(),
            "name": self.AnimalName_ledit.text().strip(),
            "age": self.animal_age_ledit.text().strip(),
            "species": self.AnimalSpecie.currentText(),
            "breed": self.AnimalBreed_ledit.text().strip(),
            "status": self.AnimalStatus.currentText()
        }

        if not self.check_empty_fields(animal_data):
            return

        try:
            clean_age = int(animal_data["age"])
            if clean_age < 0:
                QMessageBox.warning(self, "Input Error", "Age cannot be negative.")
                return
            animal_data["age"] = clean_age
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid whole number for the Age.")
            return

        confirm_dialog = ConfirmWindow_animal(
            target="Animal Table",
            rec_id=animal_data["animal_id"],
            rec_name=animal_data["name"],
            rec_age = animal_data["age"],
            rec_breed = animal_data["breed"],
            rec_status = animal_data["status"],
            rec_species = animal_data["species"]
        )

        if confirm_dialog.exec_() == QDialog.Accepted:
            try:
                insert_animal(animal_data)
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Database Error", "Animal ID already exists.")
                return

            self.load_database_records()
            self.clear_animal_form()
            QMessageBox.information(self, "Success", "Record saved successfully!")
        else:
            print("User canceled the save operation.")

    def clear_animal_form(self):
        self.AnimalID_ledit.clear()
        self.AnimalName_ledit.clear()
        self.animal_age_ledit.clear()
        self.AnimalBreed_ledit.clear()
        self.AnimalSpecie.setCurrentIndex(0)
        self.AnimalStatus.setCurrentIndex(0)

    def save_adopter_management(self):
        adopter_data = {
            "adopter_id": self.adopter_id_ledit.text().strip(),
            "first_name": self.adopter_firstname_ledit.text().strip(),
            "last_name": self.adopter_lastname_leditt.text().strip(),
            "age": self.adopter_age_edit.text().strip(),
            "phone": self.adopter_phone_ledit.text().strip(),
            "address": self.adopter_address_ledit.text().strip(),
            "status": self.adopter_status.currentText()
        }

        if not self.check_empty_fields(adopter_data):
            return

        try:
            clean_age = int(adopter_data["age"])
            if clean_age < 0:
                QMessageBox.warning(self, "Input Error", "Age cannot be negative.")
                return
            elif clean_age < 18:
                QMessageBox.warning(self, "Input Error", "Age must be greater than 18 to adopt.")
                return
            adopter_data["age"] = clean_age
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid whole number for the Age.")
            return

        try:
            clean_phone = adopter_data["phone"]
            if len(clean_phone) != 11:
                QMessageBox.warning(self, "Input Error", "Please enter a 11 digit phone number.")
                return
            adopter_data["phone"] = clean_phone
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid phone number.")
            return

        full_name = f"{adopter_data['first_name']} {adopter_data['last_name']}"
        confirm_dialog = ConfirmWindow_adopterManagement(
            target="Adopter Table",
            rec_id=adopter_data["adopter_id"],
            rec_name=full_name,
            rec_age=adopter_data["age"],
            rec_phone=adopter_data["phone"],
            rec_address=adopter_data["address"],
            rec_status=adopter_data["status"]
        )

        if confirm_dialog.exec_() == QDialog.Accepted:
            try:
                insert_adopter(adopter_data)
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Database Error", "Adopter ID already exists.")
                return

            self.load_database_records()
            self.clear_adopter_form()
            QMessageBox.information(self, "Success", "Adopter record saved successfully!")
        else:
            print("User canceled the save operation.")

    def clear_adopter_form(self):
        self.adopter_id_ledit.clear()
        self.adopter_firstname_ledit.clear()
        self.adopter_lastname_leditt.clear()
        self.adopter_age_edit.clear()
        self.adopter_phone_ledit.clear()
        self.adopter_address_ledit.clear()
        self.adopter_status.setCurrentIndex(0)

    def save_adoption_record(self):
        animal_id = self.get_required_combobox_id(self.animal_id_combox, "Animal ID")
        if animal_id is None:
            return

        adopter_id = self.get_required_combobox_id(self.adopter_id_combox, "Adopter ID")
        if adopter_id is None:
            return

        adoption_record_data = {
            "adoption_id": self.adopt_id_ledit.text().strip(),
            "adoption_date": self.get_date_value(self.Adoption_Date),
            "fee_paid": self.adopt_fee_ledit.text().strip(),
            "animal_id": animal_id,
            "adopter_id": adopter_id
        }

        if not self.check_empty_fields(adoption_record_data):
            return

        try:
            clean_fee = float(adoption_record_data["fee_paid"])
            if clean_fee < 0:
                QMessageBox.warning(self, "Input Error", "Fee paid cannot be negative.")
                return
            adoption_record_data["fee_paid"] = clean_fee
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid number for the Fee Paid.")
            return

        confirm_dialog = ConfirmWindow_adopterRecord(
            target="Adoption Records Table",
            rec_id=adoption_record_data["adoption_id"],
            rec_date=adoption_record_data["adoption_date"],
            rec_fee=adoption_record_data["fee_paid"],
            rec_animalID=adoption_record_data["animal_id"],
            rec_recAdopterID=adoption_record_data["adopter_id"]
        )

        if confirm_dialog.exec_() == QDialog.Accepted:
            try:
                insert_adoption(adoption_record_data)
            except sqlite3.IntegrityError as error:
                QMessageBox.warning(self, "Database Error", f"Could not save adoption record: {error}")
                return

            self.load_database_records()
            self.clear_adoption_form()
            QMessageBox.information(self, "Success", "Adoption record saved successfully!")
        else:
            print("User canceled the save operation.")

    def clear_adoption_form(self):
        self.adopt_id_ledit.clear()
        self.reset_date_widget(self.Adoption_Date)
        self.adopt_fee_ledit.clear()
        self.animal_id_combox.setCurrentIndex(0)
        self.adopter_id_combox.setCurrentIndex(0)

    def save_health_record(self):
        animal_id = self.get_health_animal_id()
        if animal_id is None:
            return

        health_data = {
            "animal_id": animal_id,
            "date_administered": self.get_date_value(self.Health_date_edit),
            "procedure": self.health_procedure_ledit.text().strip(),
            "veterinarian": self.health_vet_ledit.text().strip()
        }

        if not self.check_empty_fields(health_data):
            return

        confirm_dialog = ConfirmWindow_healthRecord(
            target="Health & Medical Logs",
            rec_animalID=health_data["animal_id"],
            rec_date=health_data["date_administered"],
            rec_procedure=health_data["procedure"],
            rec_vet=health_data["veterinarian"]
        )

        if confirm_dialog.exec_() == QDialog.Accepted:
            try:
                insert_health_record(health_data)
            except sqlite3.IntegrityError as error:
                QMessageBox.warning(self, "Database Error", f"Could not save health record: {error}")
                return

            self.load_database_records()
            self.clear_health_form()
            QMessageBox.information(self, "Success", "Health record saved successfully!")
        else:
            print("User canceled the save operation.")

    def clear_health_form(self):
        self.reset_health_animal_id()
        self.reset_date_widget(self.Health_date_edit)
        self.health_procedure_ledit.clear()
        self.health_vet_ledit.clear()

    def delete_database_records(self):
        confirm_dialog = ConfirmWindow_delete()

        if confirm_dialog.exec_() == QDialog.Accepted:
            try:
                delete_all_data()
            except sqlite3.Error as error:
                QMessageBox.warning(self, "Database Error", f"Could not delete database records: {error}")
                return

            self.load_database_records()
            self.clear_animal_form()
            self.clear_adopter_form()
            self.clear_adoption_form()
            self.clear_health_form()
            QMessageBox.information(self, "Success", "All database records were deleted successfully!")
        else:
            print("User canceled the delete operation.")

if __name__ == "__main__":
    initialize_database()
    app = QApplication(sys.argv)
    login = LoginWindow()
    if login.exec_() == QDialog.Accepted:
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    else:
        sys.exit()
