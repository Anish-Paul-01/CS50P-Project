import csv
import re
import random
from tabulate import tabulate
import string
from datetime import datetime
import pytz
from fpdf import FPDF
import inflect

p = inflect.engine()


class Details:
    def __init__(self, name, number, email, id, Dr_Name):
        self.name_ = name
        self.number_ = number
        self.email_ = email
        self.id_ = id
        self.Dr_Name_ = Dr_Name

    def __str__(self):
        return f"\nCustomer Name: {self.name_}\nCustomer Id: {self.id_}\nMobile Number: {self.number_}\nE-Mail id: {self.email_}\nDr. :{self.Dr_Name_}\n"

    @classmethod
    def get(cls):
        name = input("Customer Name: ")
        number = input("Mobile Number: ")
        email = input("Email id: ")
        Dr_Name = input("Dr. Name: ")
        id = None
        return cls(name, number, email, id, Dr_Name)

    @property
    def name_(self):
        return self._name

    @name_.setter
    def name_(self, name):
        if not any(char.isdigit() for char in name):
            self._name = name
        else:
            raise ValueError

    @property
    def Dr_Name_(self):
        return self._Dr_Name

    @Dr_Name_.setter
    def Dr_Name_(self, Dr_Name):
        if not any(char.isdigit() for char in Dr_Name):
            self._Dr_Name = Dr_Name
        else:
            raise ValueError

    @property
    def number_(self):
        return self._number

    @number_.setter
    def number_(self, number):
        if re.search(r"^(\+?\d{1,3}[-.\s]?)?\d{10}$", number):
            self._number = number
        else:
            raise ValueError

    @property
    def email_(self):
        return self._email

    @email_.setter
    def email_(self, email):
        if re.search(
            r"^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$",
            email,
        ):
            self._email = email
        else:
            raise ValueError

    @property
    def id_(self):
        return self._id

    @id_.setter
    def id_(self, id):
        id = random.randint(100000, 999999)
        self._id = id

    def customer_data(self):
        with open("my_customer_data.csv", "a") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "Cust. Name",
                    "Cust. id",
                    "Mobile Number",
                    "Email id",
                    "Dr. Name",
                ],
            )
            writer.writerow(
                {
                    "Cust. id": self.id_,
                    "Cust. Name": self.name_,
                    "Mobile Number": self.number_,
                    "Email id": self.email_,
                    "Dr. Name": self.Dr_Name_,
                }
            )


def Add_product_details():
    name = input("Prod. Name: ").upper()
    batch = input("Batch No.: ").upper()
    available_quantity = input("Quantity: ")
    rate = float(input("M.R.P: "))

    x = input("\nAre you Sure?(Y/N)\n").lower()
    if(x == "y"):
        with open("my_inventory_data.csv", "a") as file:
            writer = csv.DictWriter(
                file, fieldnames=["Batch No.", "Product Name", "Quantity", "M.R.P"]
            )
            writer.writerow(
                {
                    "Batch No.": batch,
                    "Product Name": name,
                    "Quantity": available_quantity,
                    "M.R.P": rate,
                }
            )


def order(details):
    list = []
    while True:
        batch = input("\nBatch No.: ").strip().upper()
        if batch == "END":
            x = input("\nAre you Sure?(Y/N)\n").lower()
            if(x == "y"):
                bill(list, details)
                return False
        elif batch == "CANCEL":
            return False
        x = search_product(batch)
        if x == "found":
            try:
                Qty = int(input("Qty: "))
            except ValueError:
                print("Qty should be an intger")
                continue
            y = Update_inventory(batch, Qty)
            if y >= 0:
                print(f"{batch} : {item_name(batch)} X {Qty}")
                list.append(f"{batch}#{Qty}")
            else:
                print(f"{batch} : {item_name(batch)} Count :: 0")
                continue


def search_product(batch):
    with open(f"my_inventory_data.csv") as data:
        reader = csv.DictReader(data)
        for row in reader:
            if batch in row["Batch No."]:
                return f"found"


def search(batch):
    with open(f"my_inventory_data.csv") as data:
        reader = csv.DictReader(data)
        for row in reader:
            if batch in row["Batch No."]:
                return f"{row["Batch No."]} : {row["Quantity"]} Qty left"


def date_time():
    timezone = pytz.timezone("Asia/Kolkata")
    current_time = datetime.now(timezone)
    formated_time = current_time.strftime("%d-%m-%Y %H:%M:%S %p")
    return formated_time


def bill(list, details):
    Total = 0
    Bill = "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(8)
    )

    print()
    print(f"Bill No.:{Bill}")
    print("XYZ Medical Store")
    print("Address Line 1")
    print("Address Line 2")
    print("License No.: XYZ ")
    print("GST IN : XYZ")
    print("Phone : xxxxxxxxxx/xxxxxxxxxx")
    print("Email : xxxxxxxxx@xxxx.xxx")

    customer_details(details)

    print("This is your bill!", end="\n\n")
    table = []
    headers = ["QTY", "PRODUCT NAME", "BATCH NO.", "M.R.P(Rs.)"]
    for element in list:
        batch, Qty = element.split("#")
        recent_total = int(Qty) * float(price(batch))
        Total = Total + recent_total
        table.append([Qty, item_name(batch), batch, price(batch)])

    pdf_table = tabulate(table, headers, tablefmt="presto")
    print()
    print(pdf_table)
    print()
    print(f"DISCOUNT: MIN -> 10% :: Amt > 500 = 15% :: Amt > 1000 = 25% :")
    print(f"   : Amt > 1500 = 30% :: Amt > 2000 = 35% :: Amt > 2500 = 40%:")
    print()
    print(f"GROSS TOTAL: {Total:.2f}")
    print()
    if 0 <= Total < 500:
        payble_total = Total - Total * 0.1
        Discount = Total * 0.1
    elif 500 <= Total < 1000:
        payble_total = Total - Total * 0.15
        Discount = Total * 0.15
    elif 1000 <= Total < 1500:
        payble_total = Total - Total * 0.25
        Discount = Total * 0.25
    elif 1500 <= Total < 2000:
        payble_total = Total - Total * 0.3
        Discount = Total * 0.3
    elif 2000 <= Total < 2500:
        payble_total = Total - Total * 0.35
        Discount = Total * 0.35
    else:
        payble_total = Total - Total * 0.4
        Discount = Total * 0.4

    print(f"DISCOUNTED AMOUNT: {Discount:.2f}")
    print()
    print(f"TOTAL PAYBLE AMT: {payble_total:.2f}")
    print()
    print(date_time())
    print()
    x = input("\nAre want bill?(Y/N)\n").lower()
    if(x == "y"):
        pdf_bill(list, details, Bill, Discount, payble_total, Total)


def item_name(batch):
    with open(f"my_inventory_data.csv", "r") as data:
        reader = csv.DictReader(data)
        for row in reader:
            if batch in row["Batch No."]:
                return f"{row["Product Name"]}"


def price(batch):
    with open(f"my_inventory_data.csv") as data:
        reader = csv.DictReader(data)
        for row in reader:
            if batch in row["Batch No."]:
                return f"{row["M.R.P"]}"


def customer_details(details):
    print(details)


def Update_inventory(batch, Qty):
    with open(f"my_inventory_data.csv") as data:
        reader = csv.DictReader(data)
        rows = list(reader)

    for row in rows:
        if row["Batch No."] == batch:
            old_qty = int(row["Quantity"])
            new_qty = old_qty - Qty
            if new_qty >= 0:
                row["Quantity"] = new_qty

    with open("my_inventory_data.csv", "w") as file:
        writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return new_qty


def main():
    print("Type 'end' to end process")
    print("Press 1 : Add Product Details")
    print("Press 2 : Searching")
    print("Press 3 : For Billing")
    while True:
        cond = input("==>").lower()
        match cond:
            case "1":
                Add_product_details()
            case "2":
                batch = input("Batch No.: ").strip().upper()
                print(search(batch))
            case "end":
                break
            case "3":
                try:
                    details = Details.get()
                    details.customer_data()
                    order(details)
                    break
                except ValueError:
                    print("Try Again !")
            case _:
                print("Invalid Input")


def pdf_bill(list, details, Bill, Discount, payble_total, Total):
    pdf = FPDF("L", "mm", format=(200, 230))

    w = 230
    h = 200

    pdf.add_page()

    pdf.set_xy(10, 0)
    pdf.set_font("Helvetica", size=11)
    pdf.cell(70, 5, f"Bill No.: {Bill}", align="L")
    pdf.cell(70, 5, "GST INVOICE", align="C")
    pdf.cell(70, 5, f"Date: {date_time()}", align="R")
    pdf.dashed_line(10, 5, 220, 5)

    pdf.set_xy(10, 6)
    pdf.set_font("Courier", style="B", size=15)
    pdf.cell(0, 5, "XYZ MEDICAL STORES", align="C")

    pdf.set_xy(10, 11)
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 5, "Address Line 1", align="C")

    pdf.set_xy(10, 15)
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 5, "Address Line 2", align="C")

    pdf.set_xy(10, 20)
    pdf.set_font("Helvetica", size=11)
    pdf.cell(70, 5, "GST IN : XYZ", align="L")
    pdf.cell(70, 5, "License No.: XYZ", align="C")
    pdf.cell(70, 5, "Phone: xxxxxxxxxx", align="R")

    pdf.set_xy(10, 24)
    pdf.set_font("Helvetica", size=11)
    pdf.cell(70, 5, "Email : xxxxxxxxx@xxxx.xxx", align="L")
    pdf.cell(70, 5)
    pdf.cell(70, 5, "Phone: xxxxxxxxxx", align="R")
    pdf.dashed_line(10, 30, 220, 30)

    pdf.set_xy(10, 31)
    pdf.set_font("Helvetica", size=11)
    pdf.cell(105, 5, f"Name: {details.name_}", align="L")
    pdf.cell(105, 5, f"Customer Id.: {details.id_}", align="L")

    pdf.set_xy(10, 35)
    pdf.set_font("Helvetica", size=11)
    pdf.cell(105, 5, f"Phone: {details.number_}", align="L")
    pdf.cell(105, 5, f"Email : {details.email_}", align="L")

    pdf.set_xy(10, 39)
    pdf.set_font("Helvetica", size=11)
    pdf.cell(105, 5, f"Doctor Name: {details.Dr_Name_ }", align="L")
    pdf.dashed_line(10, 44.5, 220, 44.5)
    pdf.dashed_line(10, 45, 220, 45)

    pdf.set_xy(10, 45)
    pdf.set_font("Helvetica", style="B", size=11)
    pdf.cell(20, 5, "QTY", align="C")
    pdf.cell(130, 5, "PRODUCT NAME", align="C")
    pdf.cell(30, 5, "BATCH NO.", align="C")
    pdf.cell(30, 5, "M.R.P(RS.)", align="C")
    pdf.dashed_line(10, 50, 220, 50)

    i = 50
    for element in list:
        while i < 130:
            pdf.set_xy(10, i)
            batch, Qty = element.split("#")
            pdf.set_font("Helvetica", size=11)
            pdf.cell(20, 5, f"{Qty}", align="C")
            pdf.cell(130, 5, f"{item_name(batch)}", align="C")
            pdf.cell(30, 5, f"{batch}", align="C")
            pdf.cell(30, 5, f"{price(batch)}", align="C")
            i = i + 5
            break

    pdf.dashed_line(31, 45, 31, 135)
    pdf.dashed_line(161, 45, 161, 135)
    pdf.dashed_line(191, 45, 191, 135)

    pdf.set_xy(10, 135)
    pdf.dashed_line(10, 135, 220, 135)
    pdf.dashed_line(10, 135.5, 220, 135.5)

    pdf.set_xy(10, 136)
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(
        210,
        4,
        "DISCOUNT: MIN -> 10% :: Amt > 500 = 15% :: Amt > 1000 = 25% :\n: Amt > 1500 = 30% :: Amt > 2000 = 35% :: Amt > 2500 = 40% :",
        align="L",
    )

    pdf.set_xy(10, 145)
    pdf.dashed_line(10, 145, 220, 145)
    pdf.dashed_line(10, 145.5, 220, 145.5)

    pdf.set_xy(10, 147)
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(
        105, 5, f"GROSS TOTAL: Rs.{Total:.2f}\nDISCOUNT: Rs.{Discount:.2f}", align="L"
    )

    pdf.set_xy(115, 146)
    pdf.set_font("Arial", style="B", size=15)
    pdf.cell(105, 5, f"NET TOTAL: Rs.{round(payble_total)}", align="L")

    pdf.dashed_line(114, 146, 114, 160)
    pdf.dashed_line(115, 146, 115, 160)

    pdf.dashed_line(115, 153, 220, 153)
    pdf.set_xy(115, 154)
    pdf.set_font("Helvetica", size=10)
    pdf.cell(
        105,
        5,
        f"Rs. {p.number_to_words(round(payble_total), andword="")} only ",
        align="L",
    )

    pdf.set_xy(10, 160)
    pdf.dashed_line(10, 160, 220, 160)
    pdf.dashed_line(10, 160.5, 220, 160.5)

    pdf.set_xy(10, 161)
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(
        210,
        5,
        "**Goods once sold will not be taken back or exchanged after 7 days.**\n**PLEASE CONSULT DOCTOR BEFORE USING THE MEDICINE**\n**CUTTING PRODUCT WILL NOT BE ACCEPTABLE**",
        align="L",
    )

    pdf.set_xy(140, 166)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(40, 5, f"SCAN TO PAY --->", align="L")

    pdf.set_xy(180, 161)
    pdf.image("Qr_code.jpeg", w=15, h=15)

    pdf.output(f"{Bill}.pdf")


if __name__ == "__main__":
    main()


