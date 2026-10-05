import os
import cv2
import numpy as np
from PIL import Image, ImageDraw
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def make_sample_image(path, title, subtitle, bg_color, accent_color, shape_func=None):
    img = Image.new("RGB", (800, 600), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    if shape_func:
        shape_func(draw)
        
    draw.rectangle([60, 420, 740, 540], fill=(15, 23, 42), outline=accent_color, width=2)
    draw.text((80, 440), title, fill=(255, 255, 255))
    draw.text((80, 480), subtitle, fill=(203, 213, 225))
    
    img.save(path, "JPEG", quality=90)
    print(f"Generated image: {path}")

def make_sample_video(path, title, bg_color1, bg_color2, frames=60, fps=24):
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(path, fourcc, fps, (640, 480))
    
    for i in range(frames):
        alpha = i / frames
        color = [
            int(bg_color1[c] * (1 - alpha) + bg_color2[c] * alpha)
            for c in range(3)
        ]
        frame = np.full((480, 640, 3), color, dtype=np.uint8)
        cx = int(100 + (640 - 200) * alpha)
        cy = int(240 + 50 * np.sin(alpha * 6.28))
        cv2.circle(frame, (cx, cy), 35, (255, 255, 255), -1)
        cv2.putText(frame, f"{title} - Frame {i}", (40, 420), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        out.write(frame)
        
    out.release()
    print(f"Generated video: {path}")

def make_sample_pdf(path, title, subtitle, paragraphs):
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    
    # Modern header
    c.setFillColorRGB(0.08, 0.12, 0.22)
    c.rect(0, height - 120, width, 120, fill=True, stroke=False)
    
    c.setFillColorRGB(0.24, 0.58, 0.98) # Accent line
    c.rect(0, height - 124, width, 4, fill=True, stroke=False)
    
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 60, title)
    
    c.setFillColorRGB(0.8, 0.85, 0.95)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 90, subtitle)
    
    c.setFillColorRGB(0.15, 0.18, 0.25)
    c.setFont("Helvetica", 11)
    
    y = height - 160
    for para in paragraphs:
        if para.startswith("###"):
            c.setFont("Helvetica-Bold", 14)
            c.setFillColorRGB(0.08, 0.12, 0.22)
            y -= 10
            c.drawString(50, y, para.replace("###", "").strip())
            y -= 22
            c.setFont("Helvetica", 11)
            c.setFillColorRGB(0.2, 0.25, 0.3)
            continue
            
        words = para.split(" ")
        line = ""
        for word in words:
            if c.stringWidth(line + " " + word, "Helvetica", 11) < (width - 100):
                line += (" " if line else "") + word
            else:
                c.drawString(50, y, line)
                y -= 16
                line = word
        if line:
            c.drawString(50, y, line)
            y -= 22
            
    c.save()
    print(f"Generated PDF: {path}")

def make_blank_scanned_pdf(path):
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    # Just draw a graphic box with no extractable text
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.setFillColorRGB(0.95, 0.95, 0.95)
    c.rect(50, 50, width - 100, height - 100, fill=True, stroke=True)
    c.save()
    print(f"Generated scanned/empty text PDF: {path}")

if __name__ == "__main__":
    os.makedirs("dataset/images", exist_ok=True)
    os.makedirs("dataset/videos", exist_ok=True)
    os.makedirs("dataset/pdfs", exist_ok=True)
    
    # 1. Images
    def draw_cat_woman(draw):
        draw.ellipse([300, 150, 420, 270], fill=(244, 208, 111))
        draw.polygon([(260, 270), (460, 270), (500, 500), (220, 500)], fill=(79, 70, 229))
        draw.ellipse([460, 380, 540, 470], fill=(249, 115, 22))
        draw.polygon([(460, 380), (480, 330), (500, 380)], fill=(249, 115, 22))
        draw.polygon([(500, 380), (520, 330), (540, 380)], fill=(249, 115, 22))

    make_sample_image(
        "dataset/images/woman_with_cat.jpg",
        "A woman standing with a cat in a bright room",
        "Domestic portrait photography with friendly pet companion",
        (241, 245, 249),
        (79, 70, 229),
        draw_cat_woman
    )

    def draw_nature(draw):
        draw.polygon([(50, 450), (280, 150), (500, 450)], fill=(71, 85, 105))
        draw.polygon([(300, 450), (550, 180), (780, 450)], fill=(51, 65, 85))
        draw.rectangle([0, 400, 800, 600], fill=(14, 165, 233))

    make_sample_image(
        "dataset/images/nature_mountains_lake.jpg",
        "Scenic nature landscape with mountains and lake",
        "Vibrant wilderness photography with tranquil lake reflections",
        (186, 230, 253),
        (14, 165, 233),
        draw_nature
    )

    def draw_architecture(draw):
        draw.rectangle([180, 120, 360, 450], fill=(30, 41, 59))
        draw.rectangle([380, 80, 600, 450], fill=(51, 65, 85))
        for y in range(140, 420, 40):
            draw.rectangle([200, y, 260, y+25], fill=(254, 240, 138))
            draw.rectangle([280, y, 340, y+25], fill=(254, 240, 138))
            draw.rectangle([400, y, 480, y+25], fill=(254, 240, 138))
            draw.rectangle([500, y, 580, y+25], fill=(254, 240, 138))

    make_sample_image(
        "dataset/images/modern_residential_architecture.jpg",
        "Modern luxury residential architecture and apartments",
        "High-end contemporary real estate architectural rendering",
        (226, 232, 240),
        (30, 41, 59),
        draw_architecture
    )

    with open("dataset/images/corrupted_sample_image.jpg", "wb") as f:
        f.write(b"NOT_A_VALID_JPEG_HEADER_CORRUPTED_STREAM_DATA_12345")
    print("Generated corrupt image test file: dataset/images/corrupted_sample_image.jpg")

    # 2. Videos
    make_sample_video(
        "dataset/videos/construction_activity_timelapse.mp4",
        "Construction Site Machinery & Builders Activity",
        (40, 40, 40),
        (245, 158, 11),
        frames=48,
        fps=24
    )

    make_sample_video(
        "dataset/videos/city_skyline_traffic.mp4",
        "Metropolitan City Skyline and Evening Traffic",
        (15, 23, 42),
        (99, 102, 241),
        frames=48,
        fps=24
    )

    # 3. PDFs
    make_sample_pdf(
        "dataset/pdfs/residential_luxury_project_brochure.pdf",
        "The Grand Horizons - Luxury Residential Project",
        "Official Architectural & Sales Brochure | Prestige Living",
        [
            "### Project Overview & Vision",
            "The Grand Horizons represents a pinnacle of contemporary architectural elegance. Located in the prestigious central district, this residential development features 120 luxury penthouses and apartments surrounded by landscaped botanical gardens, infinity pools, and eco-friendly infrastructure.",
            "### Architectural Specifications & Floorplans",
            "Every residence offers floor-to-ceiling panoramic glass walls, Italian marble flooring, bespoke German kitchen fittings, and integrated smart home automation systems controlling climate, ambient lighting, and biometric security.",
            "### Community Amenities & Sustainability",
            "Residents enjoy exclusive access to a 24/7 private concierge, state-of-the-art wellness club, heated rooftop pool, private cinema lounge, and electric vehicle charging stations throughout the subterranean parking facility."
        ]
    )

    make_sample_pdf(
        "dataset/pdfs/financial_quarterly_earnings_report.pdf",
        "Vertex Global Financial - Q3 Earnings Report",
        "Corporate Financial Disclosure & Strategic Growth Metrics",
        [
            "### Executive Financial Summary",
            "Vertex Global reported total Q3 revenues of $482 million, a 14.2% year-over-year increase driven by cloud enterprise software subscriptions and digital asset management infrastructure solutions.",
            "### Operational Margins & Outlook",
            "Operating margins expanded to 31.8% reflecting disciplined cost optimization and algorithmic workload acceleration. Net cash flows from operations totaled $124 million for the quarter."
        ]
    )

    make_blank_scanned_pdf("dataset/pdfs/scanned_empty_text_document.pdf")
