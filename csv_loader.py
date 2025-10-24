import csv
from record import Record

class CSVLoader:
    @staticmethod
    def load_records(csv_file):
        records = []
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                record = Record(
                    name=row["NAME"].strip(),
                    ssn=row["SSN"].strip(),
                    departmentcode=row["DEPARTMENTCODE"].strip(),
                    address=row["ADDRESS"].strip(),
                    phone=row["PHONE"].strip(),
                    birthdate=row["BIRTHDATE"].strip(),
                    sex=row["SEX"].strip(),
                    jobcode=row["JOBCODE"].strip(),
                    salary=row["SALARY"].strip()
                )
                records.append(record)
        return records
