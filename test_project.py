import pytest
import unittest
from unittest.mock import patch, mock_open, MagicMock
from project import Details,Add_product_details,search_product,search,date_time,item_name,price,Update_inventory,order,bill,customer_details,pdf_bill
import os
import string
from pypdf import PdfReader


def test_details_initialization():
    details = Details("Anish Paul", "+917438433292", "anishpaul555@gmail.com", None, "Dr. Indranil Chaudhuri")
    assert details.name_ == "Anish Paul"
    assert details.number_ == "+917438433292"
    assert details.email_ == "anishpaul555@gmail.com"
    assert details.Dr_Name_ == "Dr. Indranil Chaudhuri"

# Test for Details __str__ method
def test_details_str():
    details = Details(
        name="Anish Paul",
        number="+917438433292",
        email="anishpaul555@gmail.com",
        id=None,
        Dr_Name="Dr. Indranil Chaudhuri",
    )
    expected_str = (
        "\nCustomer Name: Anish Paul\n"
        f"Customer Id: {details.id_}\n"
        "Mobile Number: +917438433292\n"
        "E-Mail id: anishpaul555@gmail.com\n"
        "Dr. :Dr. Indranil Chaudhuri\n"
    )
    assert str(details) == expected_str

# Tests for validation errors
def test_name_valid():
    with pytest.raises(ValueError):
        Details("Anish123", "9452253563", "dasmanik555@gmail.com", None, "Dr. Somnath Pal")

def test_number_valid():
    with pytest.raises(ValueError):
        Details("Manik Das", "+9194523563", "dasmanik555@gmail.com", None, "Dr. Somnath Pal")

def test_email_valid():
    with pytest.raises(ValueError):
        Details("Deepak Dhara", "+9194523563", "dasmanik-555@gmail.com", None, "Dr. Somnath Pal")

# Test for Details.get() method with input mock
@patch("builtins.input", side_effect=["Anish Paul", "+917438433292", "anishpaul555@gmail.com", "Dr. Indranil Chaudhuri"])
def test_details_get(mock_input):
    details = Details.get()
    assert details.name_ == "Anish Paul"
    assert details.number_ == "+917438433292"
    assert details.email_ == "anishpaul555@gmail.com"
    assert details.Dr_Name_ == "Dr. Indranil Chaudhuri"

# Test for writing customer data to a file
@patch("builtins.open", new_callable=mock_open)
def test_customer_data(mock_file):
    details = Details("Anish Paul", "+917438433292", "anishpaul555@gmail.com", None, "Dr. Indranil Chaudhuri")
    details.customer_data()
    mock_file.assert_called_with("my_customer_data.csv", "a")
    handle = mock_file()
    handle.write.assert_called_once()

# Test for adding product details
@patch("builtins.input", side_effect=["PANTODAC 40 TAB", "1402448", "100", "196.72", "y"])
@patch("builtins.open", new_callable=mock_open)
def test_add_product_details(mock_file, mock_input):
    Add_product_details()
    mock_file.assert_called_with("my_inventory_data.csv", "a")

# Test for searching product
def test_search_product():
    assert search_product("K2401340") == "found"
    assert search_product("1402448") == "found"
    assert search_product("234G6A3") == None
    assert search_product("A24236TM") == "found"

# Test for generic search
def test_search():
    assert search("A24236TM") == "A24236TM : 100 Qty left"
    assert search("32GA782") == None
    assert search("SXF030/A") == "SXF030/A : 100 Qty left"

# Test for updating inventory
@patch("builtins.open", new_callable=mock_open, read_data="Batch No.,Product Name,Quantity,M.R.P\n1333453,ProductA,100,50.0\n")
def test_update_inventory(mock_file):
    result = Update_inventory("1333453", 5)
    assert result == 95

# Test for getting item name
def test_item_name():
    assert item_name("HHA08/6") == "MAXMALA 50 TAB"
    assert item_name("H4FK757") == None
    assert item_name("TDSR-167") == "DROTIN DS TAB"

# Test for getting price
def test_price():
    assert price("1402101") == "211.0"
    assert price("Z40009") == "176.75"
    assert price("AD323F") == None

# Test for getting date and time
def test_date_time():
    result = date_time()
    assert isinstance(result, str)

# Test for customer details function output
def test_customer_details(capfd):
    details = Details(
        name="Anish Paul",
        number="+917438433292",
        email="anishpaul555@gmail.com",
        id=None,
        Dr_Name="Dr. Indranil Chaudhuri",
    )
    customer_details(details)
    captured = capfd.readouterr()

    expected_output = (
        f"\nCustomer Name: Anish Paul\nCustomer Id: {details.id_}\nMobile Number: +917438433292\nE-Mail id: anishpaul555@gmail.com\nDr. :Dr. Indranil Chaudhuri\n"
    )
    assert captured.out.strip() == expected_output.strip()


def test_pdf_bill():
    class CustomerDetails:
        def __init__(self):
            self.name_ = "John Doe"
            self.id_ = "C123"
            self.number_ = "1234567890"
            self.email_ = "john.doe@example.com"
            self.Dr_Name_ = "Dr. Smith"

    def mock_item_name(batch):
        return "Medicine XYZ"

    def mock_price(batch):
        return 100.00

    def mock_date_time():
        return "2024-11-23 10:00:00"

    class TestPDFBill(unittest.TestCase):

        @patch("pdf_generator.item_name", side_effect=mock_item_name)
        @patch("pdf_generator.price", side_effect=mock_price)
        @patch("pdf_generator.date_time", side_effect=mock_date_time)
        def test_pdf_bill(self, mock_date, mock_price_func, mock_item):
            """Test that pdf_bill generates the correct PDF file"""

            details = CustomerDetails()
            Bill = "ABC12345"
            Discount = 50.00
            payble_total = 450.00
            Total = 500.00
            product_list = ["BATCH001#2", "BATCH002#1"]

            pdf_bill(product_list, details, Bill, Discount, payble_total, Total)

            filename = f"{Bill}.pdf"
            self.assertTrue(os.path.exists(filename), "PDF file should be created.")


            with open(filename, "rb") as f:
                reader = PdfReader(f)
                first_page = reader.pages[0]
                text = first_page.extract_text()


                self.assertIn("Bill No.: ABC12345", text, "Bill number should be in the PDF.")
                self.assertIn("GST INVOICE", text, "GST INVOICE should be in the PDF.")
                self.assertIn("Name: John Doe", text, "Customer name should be in the PDF.")
                self.assertIn("Customer Id.: C123", text, "Customer ID should be in the PDF.")
                self.assertIn("PRODUCT NAME", text, "Product name header should be in the PDF.")
                self.assertIn("Medicine XYZ", text, "Product name should be listed in the PDF.")
                self.assertIn("Rs. 500.00", text, "Gross total should be in the PDF.")
                self.assertIn("DISCOUNT: Rs. 50.00", text, "Discount should be in the PDF.")
                self.assertIn(f"NET TOTAL: Rs.{round(payble_total)}", text, "Net total should be in the PDF.")
                self.assertIn("SCAN TO PAY --->", text, "Scan to pay text should be in the PDF.")

            if os.path.exists(filename):
                os.remove(filename)

    if __name__ == "__main__":
        unittest.main()

def test_order(capfd):
    @patch("builtins.input", side_effect=["1402448", "2", "END", "y"])
    @patch("project.search_product", side_effect=lambda batch: "found" if batch == "1402448" else None)
    @patch("project.item_name", side_effect=lambda batch: "PANTODAC 40 TAB" if batch == "1402448" else "Unknown")
    @patch("project.Update_inventory", side_effect=lambda batch, qty: 100 - qty if batch == "1402448" else -1)
    @patch("project.bill", MagicMock())
    def test_order(mock_input, mock_search_product, mock_item_name, mock_update_inventory, mock_bill):
        details = Details(
            name="Anish Paul",
            number="+917438433292",
            email="anishpaul555@gmail.com",
            id=None,
            Dr_Name="Dr. Indranil Chaudhuri",
        )

        order(details)
        mock_search_product.assert_called_with("1402448")
        mock_update_inventory.assert_called_with("1402448", 2)
        mock_item_name.assert_called_with("1402448")
        mock_bill.assert_called_once_with(["1402448#2"], details)
        assert mock_update_inventory("1402448", 2) == 98
        captured = capfd.readouterr()
        assert "PANTODAC 40 TAB X 2" in captured.out


def test_bill():
    @patch("builtins.input", side_effect=["y"])
    @patch("project.random.choice", side_effect=lambda x: "A1B2C3D4")
    @patch("project.price", side_effect=lambda batch: "100.00" if batch == "1402448" else "50.00")
    @patch("project.item_name", side_effect=lambda batch: "PANTODAC 40 TAB" if batch == "1402448" else "Unknown")
    @patch("project.customer_details", MagicMock())
    @patch("project.date_time", side_effect=lambda: "2024-11-23 10:00:00")
    @patch("project.pdf_bill", MagicMock())
    def test_bill(mock_input, mock_random_choice, mock_price, mock_item_name, mock_customer_details, mock_date_time, mock_pdf_bill, capfd):
        details = Details(
            name="Anish Paul",
            number="+917438433292",
            email="anishpaul555@gmail.com",
            id=None,
            Dr_Name="Dr. Indranil Chaudhuri",
        )

        order_list = ["1402448#2", "1402450#3"]
        bill(order_list, details)
        captured = capfd.readouterr()

        assert "Bill No.: A1B2C3D4" in captured.out
        assert "XYZ Medical Store" in captured.out
        assert "PANTODAC 40 TAB" in captured.out
        assert "BATCH NO." in captured.out
        assert "QTY" in captured.out
        assert "GROSS TOTAL" in captured.out
        assert "DISCOUNTED AMOUNT" in captured.out
        assert "TOTAL PAYBLE AMT" in captured.out


        mock_random_choice.assert_called_once_with(string.ascii_uppercase + string.digits)
        mock_price.assert_any_call("1402448")
        mock_item_name.assert_any_call("1402448")
        mock_customer_details.assert_called_once()
        mock_date_time.assert_called_once()

        mock_pdf_bill.assert_called_once_with(order_list, details, "A1B2C3D4", 0.0, 100.0, 200.0)
