from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import lightblue, black, white

class Receipt():
    def __init__(self, file_name, session_value, date, slip_num, name, father_name, contact, shift, timing, seat, address, duration, amount, img):
        super().__init__()
        self.session_value = session_value

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

        self.create_receipt()

    def create_receipt(self):
        # Create a canvas for an A4 page in landscape orientation
        c = canvas.Canvas(self.file_name, pagesize=landscape(A4))

        # Get the dimensions of the landscape A4 page
        page_width, page_height = landscape(A4)

        # Calculate the midpoint of the page width (to divide into two A5 sections)
        mid_width = page_width / 2

        # Set the dash pattern (6 units dash, 3 units space) for dividing line
        c.setDash(6, 3)
        c.setLineWidth(1)
        c.line(mid_width, 0, mid_width, page_height)  # Vertical dashed line dividing landscape A4 into two A5 pages
        c.setDash([])  # Reset dash for normal lines

        # Function to draw the receipt section
        def draw_receipt_section(x_start, y_start):
            # Define the margins and dimensions
            margin = 20
            header_height = 50  # Height of the header box
            image_box_height = 150
            image_box_width = 180
            image_box_margin_top = 25
            image_box_margin_bottom = 10
            total_image_box_height = image_box_height + image_box_margin_top + image_box_margin_bottom
            image_box_x = x_start + margin - 20 + (page_width / 2 - image_box_width) / 2
            image_box_y = y_start + page_height - margin - header_height - total_image_box_height - 30  # Increased space below header

            # Rectangle dimensions accounting for margin
            rect_x = x_start + margin
            rect_y = y_start + margin
            rect_width = page_width / 2 - 2 * margin
            rect_height = page_height - 2 * margin

            # Draw the header box with rounded corners
            c.setFillColor(lightblue)  # Background color of the header
            c.roundRect(x_start + margin, y_start + page_height - margin - header_height, rect_width, header_height, 10, fill=1)

            # Draw organization name
            c.setFont("Helvetica-Bold", 20)
            c.setFillColor(black)  # Text color for the organization name
            c.drawCentredString(x_start + margin + rect_width / 2, y_start + page_height - margin - header_height + 27, self.bus_name)

            # Draw organization details (address and contact) below the name
            c.setFont("Helvetica", 12)
            c.drawCentredString(x_start + margin + rect_width / 2, y_start + page_height - margin - header_height + 7, f"Address: {self.bus_address}  |  Contact: {self.bus_contact}")

            # Draw a rectangle with rounded corners (for the receipt content)
            c.setStrokeColor(black)  # Black color for the rectangle border
            c.setLineWidth(1)
            c.roundRect(rect_x, rect_y, rect_width, rect_height, 10)  # x, y, width, height, radius

            # Draw the header text "SLIP: 17", "FEE RECEIPT", and "Date: 17-08-2024"
            c.setFont("Helvetica-Bold", 16)
            c.drawString(x_start + margin + (rect_width / 2) - 50, y_start + page_height - margin - header_height - 25, "FEE RECEIPT")

            c.setFont("Helvetica-Bold", 12)
            c.drawString(x_start + margin + 30, y_start + page_height - margin - header_height - 40, "Slip No:")
            c.setFont("Helvetica-Bold", 14)
            c.drawString(x_start + margin + 80, y_start + page_height - margin - header_height - 40, self.slip_num)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(x_start + margin + rect_width - 110, y_start + page_height - margin - header_height - 40, "Date:")
            c.setFont("Helvetica", 12)
            c.drawString(x_start + margin + rect_width - 75, y_start + page_height - margin - header_height - 40, self.date)

            # Draw Image Box (rounded corners) with margins
            c.setFillColor(white)  # Background color of the image box
            c.setStrokeColor(black)  # Border color for the image box
            c.setLineWidth(1)
            c.roundRect(image_box_x, image_box_y, image_box_width, image_box_height, 0, stroke=1, fill=1)  # Draw image box with rounded corners

            # Draw Customer Image (150x150) within the box
            c.drawImage(self.img, image_box_x + 7.5, image_box_y + 7.5, width=image_box_width - 15, height=image_box_height - 15, mask='auto')

            # Draw a dotted line across the full width of the A5 page with 10 units padding on each side
            c.setDash(1, 2)  # Dot-dash pattern
            c.setLineWidth(0.5)
            dotted_line_y = image_box_y - 20  # Adjusted position of the dotted line
            dotted_line_x_start = x_start + margin + 10  # Start position with padding
            dotted_line_x_end = x_start + rect_width + 5  # End position with padding
            c.line(dotted_line_x_start, dotted_line_y, dotted_line_x_end, dotted_line_y)
            c.setDash([])  # Reset dash for normal lines


            # Customer Details
            c.setFont("Helvetica-Bold", 13)
            c.setFillColor(black)  # Ensure text color is black
            # Name
            c.drawString(x_start + margin + 20, dotted_line_y - 28, "Name:")
            c.setFont("Helvetica", 13)
            c.drawString(x_start + margin + 130, dotted_line_y - 28, self.name)
            # Father's Name
            c.setFont("Helvetica-Bold", 13)
            c.drawString(x_start + margin + 20, dotted_line_y - 55, "Father Name:")
            c.setFont("Helvetica", 13)
            c.drawString(x_start + margin + 130, dotted_line_y - 55, f"Mr. {self.father_name}")
            # Contact and Seat
            c.setFont("Helvetica-Bold", 13)
            c.drawString(x_start + margin + 20, dotted_line_y - 80, "Contact:")
            c.setFont("Helvetica", 13)
            c.drawString(x_start + margin + 130, dotted_line_y - 80, self.contact)
            c.setFont("Helvetica-Bold", 13)
            c.drawString(x_start + margin + 280, dotted_line_y - 80, "Seat:")
            c.setFont("Helvetica", 13)
            c.drawString(x_start + margin + 320, dotted_line_y - 80, self.seat)
            # Timing and Shift
            c.setFont("Helvetica-Bold", 13)
            c.drawString(x_start + margin + 20, dotted_line_y - 105, "Timing:")
            c.setFont("Helvetica", 13)
            c.drawString(x_start + margin + 130, dotted_line_y - 105, self.timing)
            c.setFont("Helvetica-Bold", 13)
            c.drawString(x_start + margin + 280, dotted_line_y - 105, "Shift:")
            c.setFont("Helvetica", 13)
            c.drawString(x_start + margin + 320, dotted_line_y - 105, self.shift)
            # Address
            c.setFont("Helvetica-Bold", 13)
            c.drawString(x_start + margin + 20, dotted_line_y - 130, "Address:")
            c.setFont("Helvetica", 13)
            c.drawString(x_start + margin + 130, dotted_line_y - 130, self.address)
            # Duration
            c.setFont("Helvetica-Bold", 13)
            c.drawString(x_start + margin + 20, dotted_line_y - 155, "Duration:")
            c.setFont("Helvetica-Bold", 13)
            c.drawString(x_start + margin + 130, dotted_line_y - 155, self.duration)
            # Amount in Words
            c.setFont("Helvetica-Bold", 13)
            c.drawString(x_start + margin + 20, dotted_line_y - 180, "Rupees             :")
            c.setFont("Helvetica-Bold", 8)
            c.drawString(x_start + margin + 72, dotted_line_y - 180, "(in words)")
            c.setFont("Helvetica", 13)
            c.drawString(x_start + margin + 130, dotted_line_y - 180, self.rupees)
            # Rupees in Digits (in box)
            c.setFont("Helvetica-Bold", 14)
            c.rect(x_start + margin + 20, dotted_line_y - 255, 80, 20)  # Box for amount in digits
            c.drawString(x_start + margin + 25, dotted_line_y - 250, f"Rs. {self.amount}/-")
            # Authorization Signature
            c.setFont("Helvetica-Bold", 14)
            c.drawString(x_start + margin + 250, dotted_line_y - 260, "Auth. Signature")

        # Draw receipt on both sections of the landscape A4 page
        draw_receipt_section(0, 0)  # Left A5 page
        draw_receipt_section(mid_width, 0)  # Right A5 page

        # Save the PDF file
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
            return f"{integer_words} Rupees and {decimal_words} Paise Only."
        else:
            return f"{integer_words} Rupees Only."

