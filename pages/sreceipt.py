from utils import cred
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import portrait, A4
from reportlab.lib.colors import lightblue, black, white


class SReceipt:
    def __init__(self, file_name, session_value, date, slip_num, name, father_name, contact, aadhar, shift, timing, seat, address, duration, amount, img, designation, identity):
        self.file_name = file_name
        self.bus_name = session_value[0]
        self.bus_contact = session_value[1]
        self.bus_address = session_value[4]

        self.date = date
        self.slip_num = slip_num
        self.amount = amount
        self.duration = duration
        self.rupees = self.amount_in_indian_words(int(self.amount))

        self.name = name
        self.father_name = father_name
        self.contact = contact
        self.aadhar = aadhar
        self.shift = shift
        self.timing = timing
        self.seat = seat
        self.address = address
        self.img = img
        self.designation = designation
        self.identity = identity


        self.create_receipt()

    def create_receipt(self):
        c = canvas.Canvas(self.file_name, pagesize=portrait(A4))
        page_width, page_height = portrait(A4)

        # Draw receipt in single A4 section
        self.draw_receipt_section(c, 0, 0, page_width, page_height)
        self.add_designation_section(c, page_width / 2, 0, page_width / 2, page_height)
        c.save()

    def draw_receipt_section(self, c, x_start, y_start, page_width, page_height):
        margin = 20
        header_height = 80

        image_box_height = 200
        image_box_width = 200
        image_box_x = x_start + margin + (page_width - image_box_width - margin) / 2
        image_box_y = y_start + page_height - margin - header_height - image_box_height - 80

        rect_x = x_start + margin
        rect_y = y_start + margin
        rect_width = page_width - 2 * margin
        rect_height = page_height - 2 * margin

        # Draw Header
        c.setFillColor(lightblue)
        c.roundRect(x_start + margin, y_start + page_height - margin - header_height, rect_width, header_height, 10, fill=1)

        c.setFont("Helvetica-Bold", 30)
        c.setFillColor(black)
        c.drawCentredString(x_start + margin + rect_width / 2, y_start + page_height - margin - header_height + 45, self.bus_name)

        c.setFont("Helvetica", 20)
        c.drawCentredString(x_start + margin + rect_width / 2, y_start + page_height - margin - header_height + 11,
                            f"{self.bus_address}  |  {self.bus_contact}")

        # Outer Border
        c.setStrokeColor(black)
        c.roundRect(rect_x, rect_y, rect_width, rect_height, 10)

        # Receipt Details
        c.setFont("Helvetica-Bold", 18)
        c.drawString(x_start + margin + rect_width / 2 - 50, y_start + page_height - margin - header_height - 30, "FEE RECEIPT")

        c.setFont("Helvetica", 18)
        c.drawString(x_start + margin + 15, y_start + page_height - margin - header_height - 55, "Slip No:")
        c.setFont("Helvetica-Bold", 18)
        c.drawString(x_start + margin + 85, y_start + page_height - margin - header_height - 55, self.slip_num)
        c.setFont("Helvetica", 18)
        c.drawString(x_start + margin + rect_width - 155, y_start + page_height - margin - header_height - 55, "Date:")
        c.setFont("Helvetica-Bold", 18)
        c.drawString(x_start + margin + rect_width - 105, y_start + page_height - margin - header_height - 55, self.date)

        # Image Box
        c.setFillColor(white)
        c.roundRect(image_box_x, image_box_y, image_box_width, image_box_height, 0, stroke=1, fill=1)
        c.drawImage(self.img, image_box_x + 7.5, image_box_y + 7.5, width=image_box_width - 15, height=image_box_height - 15, mask='auto')

        # Customer Details
        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(black)  # Ensure text color is black
        # Name
        c.drawString(x_start + margin + 20, image_box_y - 60, "Name:")
        c.setFont("Helvetica", 20)
        c.drawString(x_start + margin + 170, image_box_y - 60, self.name)
        # Father's Name
        c.setFont("Helvetica-Bold", 20)
        c.drawString(x_start + margin + 20, image_box_y - 95, "Father Name:")
        c.setFont("Helvetica", 20)
        c.drawString(x_start + margin + 170, image_box_y - 95, f"Mr. {self.father_name}")
        # Contact
        c.setFont("Helvetica-Bold", 20)
        c.drawString(x_start + margin + 20, image_box_y - 130, "Contact:")
        c.setFont("Helvetica", 20)
        c.drawString(x_start + margin + 170, image_box_y - 130, self.contact)
        # Addhar
        c.setFont("Helvetica-Bold", 20)
        c.drawString(x_start + margin + 20, image_box_y - 165, "Aadhar:")
        c.setFont("Helvetica", 20)
        c.drawString(x_start + margin + 170, image_box_y - 165, self.aadhar)
        # Seat
        c.setFont("Helvetica-Bold", 20)
        c.drawString(x_start + margin + 20, image_box_y - 200, "Seat:")
        c.setFont("Helvetica", 20)
        c.drawString(x_start + margin + 170, image_box_y - 200, self.seat)
        # Timing
        c.setFont("Helvetica-Bold", 20)
        c.drawString(x_start + margin + 20, image_box_y - 235, "Timing:")
        c.setFont("Helvetica", 20)
        c.drawString(x_start + margin + 170, image_box_y - 235, self.timing)
        # Address
        c.setFont("Helvetica-Bold", 20)
        c.drawString(x_start + margin + 20, image_box_y - 270, "Address:")
        c.setFont("Helvetica", 20)
        c.drawString(x_start + margin + 170, image_box_y - 270, self.address)
        # Duration
        c.setFont("Helvetica-Bold", 20)
        c.drawString(x_start + margin + 20, image_box_y - 305, "Duration:")
        c.setFont("Helvetica-Bold", 20)
        c.drawString(x_start + margin + 170, image_box_y - 305, self.duration)
        # Amount in Words
        c.setFont("Helvetica-Bold", 20)
        c.drawString(x_start + margin + 20, image_box_y - 340, "Rupees:")
        c.setFont("Helvetica", 18)
        c.drawString(x_start + margin + 170, image_box_y - 340, self.rupees)
        # Rupees in Digits (in box)
        c.setFont("Helvetica-Bold", 20)
        c.rect(x_start + margin + 30, y_start + 35, 105, 30)  # Box for amount in digits
        c.drawString(x_start + margin + 35, y_start + 42, f"Rs. {self.amount}/-")
        # Draw "This is system generated slip" at the bottom
        c.setFont("Helvetica", 12)
        c.drawString(x_start + margin + 60, y_start + 5, f"Generated by :  {cred.reciept_software_address}  |  {cred.help_dlg_contact}")
        # c.drawString(x_start + margin + 60, y_start + 5, f"Generated by :  MODAL - Library Management Software, Orai  |  8381990926")

    def add_designation_section(self, c, x_start, y_start, section_width, section_height):
        # Center Position in the Right Section
        center_x = x_start + section_width / 2
        center_y = y_start + section_height / 2

        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(center_x, center_y - 370, self.identity)
        c.setFont("Helvetica", 14)
        c.drawCentredString(center_x, center_y - 390, self.designation)

    def convert_to_indian_words(self, num):
        ones = (
            'Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven',
            'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen'
        )
        tens = (
            '', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety'
        )
        thousands = (
            '', 'Thousand', 'Lakh', 'Crore'
        )

        def _convert_less_than_thousand(n):
            if n == 0:
                return ''
            elif n < 20:
                return ones[n]
            elif n < 100:
                return tens[n // 10] + ('' if n % 10 == 0 else ' ' + ones[n % 10])
            else:
                return ones[n // 100] + ' Hundred' + ('' if n % 100 == 0 else ' and ' + _convert_less_than_thousand(n % 100))

        def _convert_less_than_lakh(n):
            if n < 1000:
                return _convert_less_than_thousand(n)
            else:
                return _convert_less_than_thousand(n // 1000) + ' Thousand' + ('' if n % 1000 == 0 else ' ' + _convert_less_than_thousand(n % 1000))

        def _convert_less_than_crore(n):
            if n < 100000:
                return _convert_less_than_lakh(n)
            else:
                return _convert_less_than_lakh(n // 100000) + ' Lakh' + ('' if n % 100000 == 0 else ' ' + _convert_less_than_lakh(n % 100000))

        if num == 0:
            return 'Zero'

        result = ''
        crore_part = num // 10000000
        lakh_part = (num % 10000000) // 100000
        thousand_part = (num % 100000) // 1000
        hundred_part = num % 1000

        if crore_part:
            result += _convert_less_than_crore(crore_part) + ' Crore'
        if lakh_part:
            result += ' ' + _convert_less_than_lakh(lakh_part) + ' Lakh'
        if thousand_part:
            result += ' ' + _convert_less_than_lakh(thousand_part) + ' Thousand'
        if hundred_part:
            result += ' ' + _convert_less_than_thousand(hundred_part)

        return result.strip()

    def amount_in_indian_words(self, amount):
        # Convert integer part
        integer_part = int(amount)
        integer_words = self.convert_to_indian_words(integer_part)
        
        # Convert decimal part
        decimal_part = round((amount - integer_part) * 100)
        if decimal_part:
            decimal_words = self.convert_to_indian_words(decimal_part)
            return f"{integer_words} Rupees and {decimal_words} Paise Only."
        else:
            return f"{integer_words} Rupees Only."


# # Usage example:
# receipt = SReceipt("output.pdf", ['Modal Study Library', '8381990926', 'helloiamin', 'LIFETIME ACCESS', 'Rajendra Nagar, Orai - Jalaun'], "30-11-2024", "12345", "Anurag Tiwari", "Shiv Kant Tiwari", "8381990926", "1234-1234-1234",
#                   "Morning", "06:00 AM - 12:00 PM", "Random", "123 Street, City", "23-11-2024  To  23-12-2024", "1500", "img4.jpg", "Manager", "Rajesh Kumar")
