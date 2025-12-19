
import csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# 한글 폰트 설정 (기본적으로 시스템에 있는 폰트를 사용하거나 내장 폰트 사용 필요)
# reportlab은 기본적으로 한글을 지원하지 않으므로, 폰트 등록이 필요함.
# 편의상 여기서는 영문으로 생성하거나, 폰트가 없으면 에러가 날 수 있으므로 
# 가장 안전하게 CSV(한글) + PDF(영문 위주)로 생성하겠습니다.

def create_dummy_csv(filename):
    data = [
        ["Product Name", "Category", "Price", "Stock", "Description"],
        ["Pure Moisture Cream", "Skincare", "25000", "150", "Deep hydration cream with hyaluronic acid."],
        ["Glow Tint Lip", "Makeup", "18000", "85", "Long-lasting shiny lip tint."],
        ["Cica Repair Ampoule", "Skincare", "32000", "200", "Soothing ampoule for sensitive skin."],
        ["Perfect Cover Cushion", "Makeup", "28000", "50", "High coverage cushion foundation."],
        ["Night Repair Serum", "Skincare", "45000", "30", "Anti-aging serum for night care."]
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    print(f"Generated {filename}")

def create_dummy_pdf(filename):
    c = canvas.Canvas(filename, pagesize=A4)
    c.drawString(100, 800, "AI CoE Internal Report 2024")
    c.drawString(100, 780, "===========================")
    
    c.drawString(100, 750, "1. Project Status")
    c.drawString(100, 735, "- Chatbot Pilot: Completed (Success)")
    c.drawString(100, 720, "- Marketing Agent: In Progress (Phase 2)")
    
    c.drawString(100, 680, "2. Budget Overview")
    c.drawString(100, 665, "- Total Budget: $50,000")
    c.drawString(100, 650, "- Cloud Infrastructure: $12,000")
    c.drawString(100, 635, "- API Costs: $5,000")
    
    c.drawString(100, 600, "CONFIDENTIAL - DO NOT DISTRIBUTE")
    c.save()
    print(f"Generated {filename}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # CSV 생성
    csv_path = os.path.join(current_dir, "product_data.csv")
    create_dummy_csv(csv_path)
    
    # PDF 생성 (REPORTLAB 라이브러리 필요: pip install reportlab)
    # 없다면 건너뛰도록 처리
    try:
        import reportlab
        pdf_path = os.path.join(current_dir, "project_report.pdf")
        create_dummy_pdf(pdf_path)
    except ImportError:
        print("ReportHub not installed, skipping PDF generation.")
        print("Run: pip install reportlab")
