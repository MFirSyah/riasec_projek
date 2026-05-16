"""
pdf_export.py — PDF Export Functions for RIASEC Career App
==========================================================
Generate PDF report for career recommendations.
"""

import io
import os
from datetime import datetime
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


def generate_pdf(
    user_name: str,
    riasec_scores: dict,
    academic_scores: dict,
    recommendations: list[dict],
    program_details: list[dict],
    output_path: Optional[str] = None
) -> bytes:
    """Generate PDF report for career recommendations.

    Args:
        user_name: Name of the student
        riasec_scores: {'r': float, 'i': float, 'a': float, 's': float, 'e': float, 'c': float}
        academic_scores: {'bahasa_indonesia': float, ..., 'gpa': float}
        recommendations: List of 5 recommendation dicts from predict_top5()
        program_details: List of 5 program detail dicts from get_program_details()
        output_path: Optional path to save PDF. If None, returns bytes.

    Returns:
        PDF as bytes if output_path is None, else None
    """
    buffer = io.BytesIO()

    # Create document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    # Styles
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        spaceAfter=6,
        textColor=colors.HexColor('#1a5276'),
        alignment=TA_CENTER
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=20,
        textColor=colors.HexColor('#5d6d7e'),
        alignment=TA_CENTER
    )

    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=16,
        spaceBefore=15,
        spaceAfter=10,
        textColor=colors.HexColor('#1a5276'),
        borderColor=colors.HexColor('#1a5276'),
        borderWidth=0,
        borderPadding=0
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        leading=14
    )

    small_style = ParagraphStyle(
        'SmallText',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#5d6d7e'),
        spaceAfter=4
    )

    # Build content
    story = []

    # === HEADER ===
    story.append(Paragraph("LAPORAN REKOMENDASI PROGRAM STUDI", title_style))
    story.append(Paragraph(
        f"Hasil Tes RIASEC dan Akademik — {datetime.now().strftime('%d %B %Y')}",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a5276')))
    story.append(Spacer(1, 10))

    # Student info
    story.append(Paragraph(f"<b>Nama:</b> {user_name}", body_style))
    story.append(Spacer(1, 15))

    # === RIASEC SCORES SECTION ===
    story.append(Paragraph("PROFIL RIASEC", section_header_style))
    story.append(Paragraph(
        "Profil kepribadian berdasarkan teori Holland yang mengukur 6 dimensi:",
        small_style
    ))

    riasec_data = [
        ['Dimensi', 'Skor', 'Kategori'],
        ['Realistic (R)', f"{riasec_scores.get('r', 0):.1f}", _get_riasec_category(riasec_scores.get('r', 0))],
        ['Investigative (I)', f"{riasec_scores.get('i', 0):.1f}", _get_riasec_category(riasec_scores.get('i', 0))],
        ['Artistic (A)', f"{riasec_scores.get('a', 0):.1f}", _get_riasec_category(riasec_scores.get('a', 0))],
        ['Social (S)', f"{riasec_scores.get('s', 0):.1f}", _get_riasec_category(riasec_scores.get('s', 0))],
        ['Enterprising (E)', f"{riasec_scores.get('e', 0):.1f}", _get_riasec_category(riasec_scores.get('e', 0))],
        ['Conventional (C)', f"{riasec_scores.get('c', 0):.1f}", _get_riasec_category(riasec_scores.get('c', 0))],
    ]

    riasec_table = Table(riasec_data, colWidths=[5*cm, 3*cm, 4*cm])
    riasec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5276')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    story.append(riasec_table)
    story.append(Spacer(1, 20))

    # === ACADEMIC SCORES SUMMARY ===
    story.append(Paragraph("RINGKASAN NILAI AKADEMIK", section_header_style))

    academic_data = [
        ['Mata Pelajaran', 'Nilai'],
        ['Bahasa Indonesia', f"{academic_scores.get('bahasa_indonesia', 0):.1f}"],
        ['Bahasa Inggris', f"{academic_scores.get('bahasa_inggris', 0):.1f}"],
        ['Matematika', f"{academic_scores.get('matematika', 0):.1f}"],
        ['Informatika', f"{academic_scores.get('informatika', 0):.1f}"],
        ['IPA', f"{academic_scores.get('ipa', 0):.1f}"],
        ['IPS', f"{academic_scores.get('ips', 0):.1f}"],
        ['PPKn', f"{academic_scores.get('ppkn', 0):.1f}"],
        ['Penjas', f"{academic_scores.get('penjas', 0):.1f}"],
        ['Seni', f"{academic_scores.get('seni', 0):.1f}"],
        ['GPA', f"{academic_scores.get('gpa', 0):.1f}"],
    ]

    academic_table = Table(academic_data, colWidths=[7*cm, 3*cm])
    academic_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5276')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    story.append(academic_table)
    story.append(Spacer(1, 20))

    # === RECOMMENDATIONS SECTION ===
    story.append(PageBreak())
    story.append(Paragraph("REKOMENDASI PROGRAM STUDI", title_style))
    story.append(Paragraph(
        "Berdasarkan profil RIASEC dan nilai akademik kamu, berikut adalah 5 program studi yang direkomendasikan:",
        body_style
    ))
    story.append(Spacer(1, 15))

    for i, (rec, details) in enumerate(zip(recommendations, program_details), 1):
        # Card-like section
        confidence_pct = rec['confidence'] * 100

        # Title with rank
        story.append(Paragraph(
            f"<b>{i}. {rec['program_name']}</b>",
            ParagraphStyle(
                'RecTitle',
                parent=styles['Heading3'],
                fontSize=14,
                textColor=colors.HexColor('#1a5276'),
                spaceBefore=10,
                spaceAfter=5
            )
        ))

        # Confidence bar
        story.append(Paragraph(
            f"Tingkat kecocokan: {confidence_pct:.1f}%",
            body_style
        ))

        # Top features explanation
        if rec.get('top_features'):
            story.append(Paragraph("<b>Mengapa cocok:</b>", small_style))
            for feat in rec['top_features']:
                story.append(Paragraph(f"• {feat}", small_style))

        story.append(Spacer(1, 10))

        # Program details
        if details:
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#dee2e6')))
            story.append(Spacer(1, 5))

            story.append(Paragraph("<b>Deskripsi:</b>", small_style))
            story.append(Paragraph(details.get('deskripsi', '-'), body_style))

            if details.get('prospek_kerja'):
                story.append(Paragraph("<b>Prospek Kerja:</b>", small_style))
                story.append(Paragraph(details.get('prospek_kerja', '-'), body_style))

            info_data = [
                ['Jenjang', details.get('jenjang', '-'), 'Akreditasi', details.get('akreditasi_umum', '-')],
                ['Durasi', details.get('durasi_studi', '-'), 'Estimasi Biaya', details.get('est_biaya', '-')],
            ]
            info_table = Table(info_data, colWidths=[3*cm, 4*cm, 3*cm, 4*cm])
            info_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
            ]))
            story.append(info_table)

            if details.get('top_kampus_prodi'):
                story.append(Spacer(1, 5))
                story.append(Paragraph("<b>Top Kampus:</b>", small_style))
                story.append(Paragraph(details.get('top_kampus_prodi', '-'), small_style))

        story.append(Spacer(1, 15))

    # === FOOTER ===
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a5276')))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        f"Dokumen generated pada {datetime.now().strftime('%d/%m/%Y %H:%M')} | RIASEC Career App",
        ParagraphStyle('Footer', parent=small_style, alignment=TA_CENTER)
    ))
    story.append(Paragraph(
        "Hasil ini hanya sebagai panduan dan bukan jaminan masuk ke program studi yang direkomendasikan.",
        ParagraphStyle('Disclaimer', parent=small_style, alignment=TA_CENTER, fontSize=8)
    ))

    # Build PDF
    doc.build(story)

    # Get PDF bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()

    # Save or return
    if output_path:
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        return None
    else:
        return pdf_bytes


def _get_riasec_category(score: float) -> str:
    """Get RIASEC category based on score."""
    if score >= 80:
        return "Sangat Dominan"
    elif score >= 60:
        return "Dominan"
    elif score >= 40:
        return "Sedang"
    elif score >= 20:
        return "Rendah"
    else:
        return "Sangat Rendah"


def save_pdf_to_file(pdf_bytes: bytes, filename: str) -> str:
    """Save PDF bytes to file in downloads folder.

    Args:
        pdf_bytes: PDF content as bytes
        filename: Desired filename (with .pdf extension)

    Returns:
        Full path to saved file
    """
    # Use downloads folder
    downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
    os.makedirs(downloads_dir, exist_ok=True)

    filepath = os.path.join(downloads_dir, filename)
    with open(filepath, 'wb') as f:
        f.write(pdf_bytes)

    return filepath