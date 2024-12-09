import json
from utils import cred
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import portrait, A4
from reportlab.lib.colors import lightblue, black, white

class DReceipt():
    def __init__(self, file_name, session_value, date, slip_num, name, father_name, contact, shift, timing, seat, address, duration, amount, img, designation, identity):
        super().__init__()

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
        self.shift = shift
        self.timing = timing
        self.seat = seat
        self.address = address
        self.img = img
        self.designation = designation
        self.identity = identity

        # Variable to decide whether to generate receipt in top or bottom A5 section
        with open(f'{session_value[1]}.json', 'r') as config_file:
            config = json.load(config_file)

        self.position = config["receipt_position"].capitalize()

        # self.position = "Top"

        self.create_receipt()

    def create_receipt(self):
        # Create a canvas for an A4 page in portrait orientation
        c = canvas.Canvas(self.file_name, pagesize=portrait(A4))

        # Get the dimensions of the portrait A4 page
        page_width, page_height = portrait(A4)

        # Calculate the positions for dividing the page
        mid_height = page_height / 2  # Midpoint for dividing the A4 into two A5 sections
        a5_height = page_height / 2  # A5 height
        mid_a5_width = page_width / 2  # Midpoint to divide A5 into two A6 sections

        # Function to draw the receipt in either top or bottom A5 section (split into two A6 pages)
        def draw_receipt_section(x_start, y_start):
            # Define the margins and dimensions
            margin = 20
            header_height = 50  # Height of the header box
            image_box_height = 100
            image_box_width = 120
            image_box_margin_top = 20
            image_box_margin_bottom = 10
            total_image_box_height = image_box_height + image_box_margin_top + image_box_margin_bottom
            image_box_x = x_start + margin - 20 + (page_width / 2 - image_box_width) / 2
            image_box_y = y_start + a5_height - margin - header_height - total_image_box_height - 20  # Adjusted space below header

            # Rectangle dimensions accounting for margin
            rect_x = x_start + margin
            rect_y = y_start + margin
            rect_width = page_width / 2 - 2 * margin
            rect_height = a5_height - 2 * margin

            # Draw the header box with rounded corners
            c.setFillColor(lightblue)  # Background color of the header
            c.roundRect(x_start + margin, y_start + a5_height - margin - header_height, rect_width, header_height, 10, fill=1)

            # Draw organization name
            c.setFont("Helvetica-Bold", 18)
            c.setFillColor(black)  # Text color for the organization name
            c.drawCentredString(x_start + margin + rect_width / 2, y_start + a5_height - margin - header_height + 27, self.bus_name)

            # Draw organization details (address and contact) below the name
            c.setFont("Helvetica", 12)
            c.drawCentredString(x_start + margin + rect_width / 2, y_start + a5_height - margin - header_height + 7, f"{self.bus_address}  |  {self.bus_contact}")

            # Draw a rectangle with rounded corners (for the receipt content)
            c.setStrokeColor(black)  # Black color for the rectangle border
            c.setLineWidth(1)
            c.roundRect(rect_x, rect_y, rect_width, rect_height, 10)  # x, y, width, height, radius

            # Draw the header text "FEE RECEIPT" and "Date"
            c.setFont("Helvetica-Bold", 13)
            c.drawString(x_start + margin + (rect_width / 2) - 50, y_start + a5_height - margin - header_height - 20, "FEE RECEIPT")

            c.setFont("Helvetica", 12)
            c.drawString(x_start + margin + 15, y_start + a5_height - margin - header_height - 40, "Slip No:")
            c.setFont("Helvetica-Bold", 13)
            c.drawString(x_start + margin + 65, y_start + a5_height - margin - header_height - 40, self.slip_num)
            c.setFont("Helvetica", 12)
            c.drawString(x_start + margin + rect_width - 110, y_start + a5_height - margin - header_height - 40, "Date:")
            c.setFont("Helvetica-Bold", 12)
            c.drawString(x_start + margin + rect_width - 75, y_start + a5_height - margin - header_height - 40, self.date)

            # Draw Image Box (rounded corners) with margins
            c.setFillColor(white)  # Background color of the image box
            c.setStrokeColor(black)  # Border color for the image box
            c.setLineWidth(1)
            c.roundRect(image_box_x, image_box_y, image_box_width, image_box_height, 0, stroke=1, fill=1)  # Draw image box with rounded corners

            # Draw Customer Image (150x150) within the box
            c.drawImage(self.img, image_box_x + 7.5, image_box_y + 7.5, width=image_box_width - 15, height=image_box_height - 15, mask='auto')

            # Customer Details
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(black)  # Ensure text color is black
            # Name
            c.drawString(x_start + margin + 15, image_box_y - 20, "Name:")
            c.setFont("Helvetica", 11)
            c.drawString(x_start + margin + 95, image_box_y - 20, self.name)
            # Father's Name
            c.setFont("Helvetica-Bold", 11)
            c.drawString(x_start + margin + 15, image_box_y - 38, "Father Name:")
            c.setFont("Helvetica", 11)
            c.drawString(x_start + margin + 95, image_box_y - 38, f"Mr. {self.father_name}")
            # Contact and Seat
            c.setFont("Helvetica-Bold", 11)
            c.drawString(x_start + margin + 15, image_box_y - 56, "Contact:")
            c.setFont("Helvetica", 11)
            c.drawString(x_start + margin + 95, image_box_y - 56, self.contact)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(x_start + margin + 175, image_box_y - 56, "Seat:")
            c.setFont("Helvetica", 11)
            c.drawString(x_start + margin + 210, image_box_y - 56, self.seat)
            # Timing
            c.setFont("Helvetica-Bold", 11)
            c.drawString(x_start + margin + 15, image_box_y - 74, "Timing:")
            c.setFont("Helvetica", 11)
            c.drawString(x_start + margin + 95, image_box_y - 74, self.timing)
            # Address
            c.setFont("Helvetica-Bold", 11)
            c.drawString(x_start + margin + 15, image_box_y - 92, "Address:")
            c.setFont("Helvetica", 11)
            c.drawString(x_start + margin + 95, image_box_y - 92, self.address)
            # Duration
            c.setFont("Helvetica-Bold", 11)
            c.drawString(x_start + margin + 15, image_box_y - 110, "Duration:")
            c.setFont("Helvetica-Bold", 11)
            c.drawString(x_start + margin + 95, image_box_y - 110, self.duration)
            # Amount in Words
            c.setFont("Helvetica-Bold", 11)
            c.drawString(x_start + margin + 15, image_box_y - 128, "Rupees:")
            c.setFont("Helvetica", 9)
            c.drawString(x_start + margin + 95, image_box_y - 128, self.rupees)

            # Rupees in Digits (in box)
            c.setFont("Helvetica-Bold", 12)
            c.rect(x_start + margin + 15, image_box_y - 175, 75, 20)  # Box for amount in digits
            c.drawString(x_start + margin + 25, image_box_y - 170, f"Rs. {self.amount}/-")
            # Authorization Signature
            c.setFont("Helvetica-Bold", 11)
            c.drawString(x_start + margin + 135, image_box_y - 160, self.identity)
            c.setFont("Helvetica", 10)
            c.drawString(x_start + margin + 155, image_box_y - 175, self.designation)
            # Draw "This is system generated slip" at the bottom
            c.setFont("Helvetica", 8)
            c.drawString(x_start + margin - 5, rect_y - 9, f"Generated by: {cred.reciept_software_address} | {cred.help_dlg_contact}")
            # c.drawString(x_start + margin - 5, rect_y - 9, f"Generated by: MODAL - Library Management Software, Orai | 9580815767")

        # Decide whether to draw in the top or bottom half based on self.position
        if self.position == "Top":
            # Draw horizontal dashed line for top A5 section
            c.setDash(6, 3)
            c.line(0, mid_height, page_width, mid_height)  # Horizontal dashed line
            c.setDash(1, 0)  # Reset to solid lines

            # Draw vertical dashed line only for top A5 section
            c.setDash(6, 3)
            c.line(mid_a5_width, mid_height, mid_a5_width, page_height)  # Vertical dashed line for top A5 section
            c.setDash(1, 0)  # Reset to solid lines

            draw_receipt_section(0, mid_height)  # Top-left A6
            draw_receipt_section(mid_a5_width, mid_height)  # Top-right A6

        elif self.position == "Bottom":
            # Draw horizontal dashed line for bottom A5 section (above receipt section)
            c.setDash(6, 3)
            c.line(0, mid_height - 1, page_width, mid_height - 1)  # Horizontal dashed line just above the receipt
            c.setDash(1, 0)  # Reset to solid lines

            # Draw vertical dashed line only for bottom A5 section
            c.setDash(6, 3)
            c.line(mid_a5_width, 0, mid_a5_width, mid_height)  # Vertical dashed line for bottom A5 section
            c.setDash(1, 0)  # Reset to solid lines

            draw_receipt_section(0, 0)  # Bottom-left A6
            draw_receipt_section(mid_a5_width, 0)  # Bottom-right A6

        # Save the PDF
        c.save()


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
            return f"{integer_words} Rupees and {decimal_words} Paise."
        else:
            return f"{integer_words} Rupees."


# # Usage example:
# receipt = DReceipt("output.pdf", ['Modal Study Library', '8381990926', 'helloiamin', 'LIFETIME ACCESS', 'Rajendra Nagar, Orai - Jalaun'], "30-11-2024", "12345", "Anurag Tiwari", "Shiv Kant Tiwari", "8381990926",
#                   "Morning", "06:00 AM - 12:00 PM", "Random", "123 Street, City", "23-11-2024  To  23-12-2024", "1500", "1.jpg", "Manager", "Anurag Tiwari")
