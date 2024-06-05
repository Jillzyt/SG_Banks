import re 
from datetime import datetime
from decimal import Decimal
import csv
import PyPDF2

class Bank:
    def __init__(self, year):
        self.year = year
        self.pdf_text_array = []
        return
    def transform(self, row):
        print(f"This is a SG bank.")
    
    def parse(self, input_file):
        return 
    
    @staticmethod
    def create_instance_from_type_string(type_string, year):
        for subclass in Bank.__subclasses__():
            if subclass.get_type() == type_string:
                return subclass(year)  # Initialize the subclass instance
        return None

    def transform(self):
        return 
    
    def extract(self):
        return
    
    def parse_csv_file(self, input_file):
        with open(input_file, 'r', newline='') as infile, \
            open('output.csv', 'w', newline='') as outfile:

            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            
            # Process the file
            for row in reader:
                # Assuming each line is read as a list of strings
                concatenated_line = ','.join(row)
                print(concatenated_line.strip())
                checked,row = self.transform(concatenated_line.strip())
                row_list = row.split(',')
                if (checked):
                    writer.writerow(row_list)

    def parse_pdf_file(self, input_file):
        with open(input_file, 'rb') as file, \
            open('output.csv', 'w', newline='') as outfile:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page.extract_text(visitor_text=self.visitor_body)
            
            # To debug
            self.pdf_text_array = self.filter_encodable_strings(self.pdf_text_array)
            print(self.pdf_text_array)
            self.pdf_text_array = self.extract(self.pdf_text_array)
            writer = csv.writer(outfile)
            print(self.pdf_text_array)
            for concatenated_line in self.pdf_text_array:
                checked,row = self.transform(concatenated_line.strip())
                row_list = row.split(',')
                if (checked):
                    writer.writerow(row_list)

    def visitor_body(self, text, cm, tm, fontDict, fontSize):
        self.pdf_text_array.extend(text.split('\n'))
        
    # To filter out encoded strings in the pdf
    def filter_encodable_strings(self, strings):
        filtered_strings = []

        for s in strings:
            try:
                s.encode('utf-8')
                filtered_strings.append(s)
            except UnicodeEncodeError:
                print("String '{}' cannot be encoded.".format(s))

        return filtered_strings

# STANDARD CHARTER

class SCCsvBankStatement(Bank):
    def __init__(self, year):
        super().__init__(year)
    
    def get_type():
        return "Standard Charter CSV Bank Statement"

    def parse(self, input_file):
        super().parse_csv_file(input_file)
    
    def transform(self, row):
        # Split the line by comma
        elements = row.split(',')
    
        if (len(elements) == 4):
            print(self.year)
            # Check if the timestamp contains the current year or the last year
            amount = elements[4]
        
            if "DB" in amount:
                price = amount.replace(" DB", "")
                month_year = convertDateToMonthUOBCsv(elements[0], self.year)
                category = get_category(elements[1], price)
                message = f"{month_year},{price},{category},{self.name}"
                return (True, message)
    
        return False, ""
        
class SCCreditCardCsv(Bank):
    def __init__(self, year):
        super().__init__(year)

    def get_type():
        return "SC CSV Credit Card Statement"
    
    def parse(self, input_file):
        super().parse_csv_file(input_file)
    
    def sanitizeMoneyStr(self, moneyStr):

        # Regular expression pattern to match decimal numbers
        pattern = r'\d+\.\d+'
        number = ""
        # Search for the pattern in the original string
        match = re.search(pattern, moneyStr)

        if match:
            # Extract the matched decimal number
            number = match.group()
        return number
        
    def transform(self, row):
        print(f"This is sc")
        
         # Split the line by comma
        elements = row.split(',')

        # Check if the timestamp contains the current year or the last year
        timestamp = elements[0]
        year = datetime.now().year
        last_year = year - 1
    
        if str(year) in timestamp or str(last_year) in timestamp:
            # Check if the last element contains 'DR'
            last_element = elements[-1]
            if 'DR' in last_element:
                price = self.sanitizeMoneyStr(elements[3])
                month_year = convertDateToMonth(timestamp)
                category = get_category(elements[1], price)
                message = f"{month_year},{price},{category},SC"
                return (True, message)
                
        return False, ""
    

class SCPdfCreditCardStatement(Bank):
    def __init__(self, year):
        super().__init__(year)
    
    def get_type():
        return "SC PDF Credit Card Statement"
    
    def parse(self, input_file):
        self.parse_pdf_file(input_file)
        
    def parse_pdf_file(self, input_file):
        final_array = []
        with open(input_file, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                matching_lines = []
                first_last_refs = []
                chunk = ""
                lines = ""
                page = reader.pages[page_num]
                text = page.extract_text()
                #print(text)
                text = text.replace("PAYMENT - THANK YOU", "Transaction Ref PAYMENT - THANK YOU ")
                text = text.replace("PAYMENT AT", "Transaction Ref PAYMENT AT")
                text = text.replace("CASHBACK", " Transaction Ref CASHBACK")
                lines = text.split('\n')
                for line in lines:
                    # Match "27 Aug", "28 Aug", and "5.25" in each line
                    pattern = r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec))\s+(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec))\s+([\d,]+\.\d+)'
                    match = re.search(pattern, line)
                    if match:
                        date1 = match.group(1)
                        date2 = match.group(2)
                        amount = match.group(3)
                        matching_lines.append(date1 + ":" +amount)
                        #print(matching_lines)
                # Find the first occurrence of "Transaction Ref" on the page
                first_ref_index = text.find("Transaction Ref")
                # Find the last occurrence of "Transaction Ref" on the page
                last_ref_index = text.rfind("Transaction Ref")
                first_last_refs.append((first_ref_index, last_ref_index))
                chunk = text[first_ref_index:last_ref_index + len("Transaction Ref")]
                chunk = chunk.split("Transaction Ref")
                if (len(chunk) >= 2):
                    lines = [line for line in chunk if line.strip() != '']
                    #print(lines)
                    #print(len(lines))
                    # Check if they matches
                    #print(len(lines) == len(matching_lines))
                    #print("page : " , page_num)
                    for i in range(len(matching_lines)):
                        matching_lines[i] = matching_lines[i] + ":" + lines[len(lines)-i-1]
                    
                    final_array.extend(matching_lines)
        
            try:
                with open('output.csv', 'w', newline='') as outfile:
                    writer = csv.writer(outfile)
                    for concatenated_line in final_array:
                        print(concatenated_line)
                        checked,row = self.transform(concatenated_line.strip())
                        row_list = row.split(',')
                        if (checked):
                            writer.writerow(row_list)
            except Exception as e:
                print(e)
                        
    def transform(self, row):
        #print(f"This is uob pdf")
        
         # Split the line by comma
        elements = row.split(':')
        #print(elements)
        if ("PAYMENT AT" in elements[2] or "CASHBACK" in elements[2] or "PAYMENT - THANK YOU" in elements[2]):
             return (False, "")
        # Check if the timestamp contains the current year or the last year
        date = elements[0]
        price = elements[1]
        if ("," in price):
            price = price.replace(",", "")
        month_year = convertDateToMonthUOBCsv(elements[0], self.year)
        category = get_category(elements[2], price)
        message = f"{month_year},{price},{category},SC SC"
        return (True, message)

# UOB Bank
class UOBCsvBank(Bank):
    def __init__(self, year):
        super().__init__(year)
    
    # Return the type
    def get_type():
        return "UOB CSV Bank statement"
    
    def parse(self, input_file):
        super().parse_csv_file(input_file)
    
    def transform(self, row):        
        # Split the line by comma
        elements = row.split(',')

        # Check if the timestamp contains the current year or the last year
        timestamp = elements[0]
        year = datetime.now().year
        
        last_year = year - 1
    
        if str(year) in timestamp or str(last_year) in timestamp:
            price = elements[2]
            if (len(price)> 1):
                month_year = convertDateToMonthUOBCsv(timestamp)
                category = get_category(elements[1].replace("\n", " "), price)
                message = f"{month_year},{price},{category},{self.name}"
                return (True, message)
        
        return False, ""


class UOBCsv(Bank):
    def __init__(self, year):
        super().__init__(year)

    def get_type():
        return "UOB Csv statement"
    
    
    def transform(self, row):
        print(f"This is uob")
        
         # Split the line by comma
        elements = row.split(',')

        # Check if the timestamp contains the current year or the last year
        timestamp = elements[0]
        year = datetime.now().year
        last_year = year - 1
    
        if str(year) in timestamp or str(last_year) in timestamp:
            # Check if there's withdrawal
            withdrawal = elements[-2]
            if withdrawal != "":
                month_year = convertDateToMonth(timestamp)
                category = get_category(elements[1], withdrawal)
                message = f"{month_year},{withdrawal},{category},{self.name}"
                return (True, message)
                
        
        return False, ""

class UOBPDFBank(Bank):
    def __init__(self, year):
        super().__init__(year)
    
    def get_type():
        return "UOB PDF Credit Card Statement"
    
    def parse(self, input_file):
        self.parse_pdf_file(input_file)    
    
    def extract(self, parts):
        final_array = []
        for i in range(len(parts)):
            line = parts[i].strip()
            pattern = r"\d{2} [A-Za-z]{3}"
            if (i + 2 < len(parts)):
                try:
                    if re.match(pattern, line) and re.match(pattern, parts[i+2].strip()):
                        # Find the CR in the statement
                        j = i + 1
                        amount_checked = False
                        amountPattern = r'\b\d+\.\d+\b'
                        while (not amount_checked):
                            sus = parts[j].strip()
                            if (j > i + 10):
                                break
                            if (re.match(amountPattern, sus)):
                                if (parts[j+2].strip() == "CR"):
                                    amount_checked = False
                                    # print("CR processed")
                                    # We do not process CR
                                    i = j
                                else:
                                    amount_checked = True
                                break
                            else:
                                j = j + 1
                        
                        if (amount_checked):
                            # Append the next few lines until CR
                            next_lines = ','.join([parts[k].strip() for k in range(i, min(j+1, len(parts)))])
                            final_array.append(next_lines)
                            i = j 
                except Exception as e:
                    print(e)
        
        return final_array
                            
    def find_amount(self, array):
        # Define the pattern for matching amounts without the dollar sign
        pattern = r'\b\d+\.\d+\b'
        amount = None

        for item in array:
            matches = re.findall(pattern, item)
            if matches:
                amount = matches[0]
                break  # Stop looping once the amount is found

        return amount
    
    def find_date(self, array):
        # Define the pattern for matching amounts without the dollar sign
        pattern = r"\d{2} [A-Za-z]{3}"
        date = None

        for item in array:
            matches = re.findall(pattern, item)
            if matches:
                date = matches[0]
                break  # Stop looping once the amount is found

        return date
    
    
    def transform(self, row):
        #print(f"This is uob pdf")
        
         # Split the line by comma
        elements = row.split(',')
        #print(elements)

        # Check if the timestamp contains the current year or the last year
        date = self.find_date(elements[0])
        price = self.find_amount(elements)
        month_year = convertDateToMonthUOBCsv(elements[0],self.year)
        category = get_category(elements[4], price)
        message = f"{month_year},{price},{category},UOB Credit Card"
        return (True, message)

# DBS bank
class DBSPDFBank(Bank):
    def __init__(self, year):
        super().__init__(year)
    
    
    def get_type():
        return "DBS PDF bank statement"
    
    def extract(self):
        for i in range(len(self.parts)):
            line = self.parts[i].strip()
            if re.match(pattern,line):
                # Append the next five lines
                next_five_lines = ','.join([self.parts[j].strip() for j in range(i, min(i + 6, len(self.parts)))])
                self.final_array.append(next_five_lines)
    
    def transform(self, row):
        print(f"This is dbs")
        
         # Split the line by comma
        elements = row.split(',')
        # print(elements)

        # Check if the timestamp contains the current year or the last year
        amount = elements[5]
    
        if "DB" in amount:
            price = amount.replace(" DB", "")
            month_year = convertDateToMonthUOBCsv(elements[0], self.year)
            category = get_category(elements[1], price)
            message = f"{month_year},{price},{category},{self.name}"
            return (True, message)
        
        return False, ""

# OCBC
class OcbcCsv(Bank):
    def __init__(self, year):
        super().__init__(year)
    

    def get_type():
        return "OCBC Csv statement"
    
    def transform(self, row):
        print(f"This is ocbc")
        
         # Split the line by comma
        elements = row.split(',')

        # Check if the timestamp contains the current year or the last year
        timestamp = elements[0]
        year = datetime.now().year
        last_year = year - 1
    
        if str(year) in timestamp or str(last_year) in timestamp:
            price = elements[2]
            if (len(price)> 1):
                month_year = convertDateToMonth(timestamp)
                category = get_category(elements[1], price)
                message = f"{month_year},{price},{category},{self.name}"
                return (True, message)
        
        return False, ""



def get_category(description, cost):
    #print(description)
    cost = Decimal(cost)
    description = description.lower()
    if "xnap" in description and cost < 3:
        return "Drink"
    elif "xnap" in description and cost > 3:
        return "Food"
    elif "mcdonalds" in description:
        return "Food"
    elif ("fairprice" in description or "ntuc" in description) and cost > 3:
        return "Food"
    elif ("fairprice" in description or "ntuc" in description) and cost < 3:
        return "Drink"
    elif "bus/mrt" in description:
        return "Transport"
    elif "shopee" in description:
        return "Others"
    elif "watsons" in description and cost < 100 and cost > 20:
        return "Beauty"
    elif "watsons" in description and cost < 30 and cost > 3:
        return "Medical"
    elif "daiso" in description:
        return "Others"
    elif "shopee" in description:
        return "Others"
    elif "ccy" in description or "takashimaya" in description or "cotton on" in description:
        return "Others"
    elif "tada" in description:
        return "Taxi"
    elif "chillipadi" in description and cost > 3:
        return "Food"
    elif "chillipadi" in description and cost < 3:
        return "Drink"
    elif "7-eleven" in description and cost < 3:
        return "Drink"
    elif "7-eleven" in description and cost > 3 or "cheers" in description and cost <= 2:
        return "Drink"
    elif "four leaves" in description or "breadtalk" in description or "gongyuan malatang" in description or "mos burger" in description or "tempura"in description or "hot tomato" in description:
        return "Food"
    elif "ikea" in description:
        return "Furniture"
    elif "mcdonald" in description:
        return "Food"
    elif "watson" in description:
        return "Medical"
    elif "innisfree" in description:
        return "Beauty"
    elif "liho" in description or "gong cha" in description or "sharetea" in description or "old tea hut" in description:
        return "Drink"
    elif "challenger" in description:
        return "Others"
    elif "uniqlo" in description:
        return "Others"
    elif cost > 300:
        return "Others"
    else:
        return description


def convertDateToMonth(date_string):
    date_object = datetime.strptime(date_string, "%d/%m/%Y")
    # Get month name from datetime object
    month_year = date_object.strftime("%m/%Y")
    return month_year

def convertDateToMonthUOBCsv(date_string):
    date_object = datetime.strptime(date_string, "%d %b %Y")
    # Get month name from datetime object
    month_year = date_object.strftime("%m/%Y")
    return month_year



def convertDateToMonthUOBCsv(date_string, year):
    date_object = datetime.strptime(date_string + " " + year, "%d %b %Y")
    # Get month name from datetime object
    month_year = date_object.strftime("%m/%Y")
    return month_year

