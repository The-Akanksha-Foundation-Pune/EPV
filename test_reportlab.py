import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def test_reportlab():
    """Test if ReportLab is working correctly"""
    try:
        # Create a PDF file
        pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_reportlab.pdf')
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.drawString(100, 750, "Hello, World! This is a test PDF generated with ReportLab.")
        c.save()
        
        # Check if the file was created
        if os.path.exists(pdf_path):
            print(f"SUCCESS: ReportLab test PDF created at {pdf_path}")
            return True
        else:
            print(f"ERROR: Failed to create test PDF at {pdf_path}")
            return False
    except Exception as e:
        print(f"ERROR: ReportLab test failed with exception: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing ReportLab...")
    test_reportlab()
