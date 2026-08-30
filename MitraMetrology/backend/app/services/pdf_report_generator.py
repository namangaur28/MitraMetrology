"""
PDF report generation service using ReportLab
Generates professional compliance inspection reports
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from io import BytesIO
import os

logger = logging.getLogger(__name__)

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image as RLImage
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("ReportLab not installed. PDF generation unavailable.")


class PDFReportGenerator:
    """Generate professional compliance inspection reports"""
    
    def __init__(self):
        self.page_size = A4
        self.available = REPORTLAB_AVAILABLE
    
    def generate_report(self, inspection_data: Dict[str, Any], 
                       output_path: Optional[str] = None) -> Optional[bytes]:
        """
        Generate PDF report from inspection data
        
        inspection_data should contain:
        {
            "inspection_id": "...",
            "scan_id": "...",
            "product_name": "...",
            "manufacturer": "...",
            "images": [...],
            "extracted_fields": {...},
            "findings": [...],
            "compliance_score": {...},
            "overall_status": "...",
            "timestamp": "..."
        }
        """
        if not self.available:
            logger.error("ReportLab not available. Cannot generate PDF.")
            return None
        
        try:
            # Create PDF document
            if output_path:
                doc = SimpleDocTemplate(
                    output_path,
                    pagesize=self.page_size,
                    rightMargin=0.5*inch,
                    leftMargin=0.5*inch,
                    topMargin=0.75*inch,
                    bottomMargin=0.75*inch,
                    title="Compliance Inspection Report"
                )
            else:
                buffer = BytesIO()
                doc = SimpleDocTemplate(
                    buffer,
                    pagesize=self.page_size,
                    rightMargin=0.5*inch,
                    leftMargin=0.5*inch,
                    topMargin=0.75*inch,
                    bottomMargin=0.75*inch,
                    title="Compliance Inspection Report"
                )
            
            # Build document
            story = []
            styles = getSampleStyleSheet()
            
            # Header
            story.extend(self._build_header(inspection_data, styles))
            story.append(Spacer(1, 0.2*inch))
            
            # Product Information
            story.extend(self._build_product_info(inspection_data, styles))
            story.append(Spacer(1, 0.2*inch))
            
            # Extracted Declarations
            story.extend(self._build_extracted_fields(inspection_data, styles))
            story.append(Spacer(1, 0.2*inch))
            
            # Compliance Findings
            story.extend(self._build_findings_section(inspection_data, styles))
            story.append(Spacer(1, 0.2*inch))
            
            # Compliance Score
            story.extend(self._build_score_section(inspection_data, styles))
            story.append(Spacer(1, 0.2*inch))
            
            # Recommendations
            story.extend(self._build_recommendations(inspection_data, styles))
            story.append(PageBreak())
            
            # Inspector Verification Section
            story.extend(self._build_verification_section(styles))
            
            # Disclaimer
            story.extend(self._build_disclaimer(styles))
            
            # Build PDF
            doc.build(story)
            
            if output_path:
                logger.info(f"PDF report generated: {output_path}")
                return True
            else:
                buffer.seek(0)
                return buffer.getvalue()
        
        except Exception as e:
            logger.error(f"Error generating PDF report: {str(e)}")
            return None
    
    def _build_header(self, data: Dict, styles) -> List:
        """Build report header"""
        elements = []
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=6,
            alignment=TA_CENTER
        )
        
        elements.append(Paragraph(
            "LEGAL METROLOGY COMPLIANCE INSPECTION REPORT",
            title_style
        ))
        
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        
        elements.append(Paragraph(
            f"AI-Assisted Preliminary Assessment",
            subtitle_style
        ))
        
        # Inspection Details Table
        header_data = [
            ["Inspection ID:", data.get("inspection_id", "N/A")],
            ["Scan ID:", data.get("scan_id", "N/A")],
            ["Date/Time:", data.get("timestamp", datetime.now().isoformat())],
            ["Status:", data.get("overall_status", "N/A").upper()]
        ]
        
        table = Table(header_data, colWidths=[1.5*inch, 3.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F0F8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        elements.append(table)
        
        return elements
    
    def _build_product_info(self, data: Dict, styles) -> List:
        """Build product information section"""
        elements = []
        
        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=10,
            borderPadding=5
        )
        
        elements.append(Paragraph("1. PRODUCT INFORMATION", heading_style))
        
        product_data = [
            ["Product Name:", data.get("product_name", "N/A")],
            ["Manufacturer:", data.get("manufacturer", "N/A")],
            ["Net Quantity:", data.get("net_quantity", "N/A")],
            ["MRP:", data.get("mrp", "N/A")]
        ]
        
        table = Table(product_data, colWidths=[1.5*inch, 3.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F0F0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        elements.append(table)
        
        return elements
    
    def _build_extracted_fields(self, data: Dict, styles) -> List:
        """Build extracted declarations section"""
        elements = []
        
        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=10
        )
        
        elements.append(Paragraph("2. EXTRACTED DECLARATIONS", heading_style))
        
        fields = data.get("extracted_fields", {})
        
        field_data = [["Field", "Value", "Confidence", "Status"]]
        
        for field_name, field_info in fields.items():
            value = field_info.get("normalized_value") or field_info.get("value")
            confidence = f"{int(field_info.get('confidence', 0) * 100)}%"
            status = "✓ Detected" if value else "✗ Missing"
            
            field_data.append([
                field_name.replace("_", " ").title(),
                value or "N/A",
                confidence,
                status
            ])
        
        table = Table(field_data, colWidths=[1.2*inch, 1.8*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')])
        ]))
        
        elements.append(table)
        
        return elements
    
    def _build_findings_section(self, data: Dict, styles) -> List:
        """Build findings section"""
        elements = []
        
        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=10
        )
        
        elements.append(Paragraph("3. COMPLIANCE FINDINGS", heading_style))
        
        findings = data.get("findings", [])
        
        if not findings:
            elements.append(Paragraph("No findings to report.", styles['Normal']))
        else:
            for i, finding in enumerate(findings[:5], 1):  # Top 5 findings
                finding_text = (
                    f"<b>Finding {i}:</b> {finding.get('what_detected', 'N/A')}<br/>"
                    f"<b>Reason:</b> {finding.get('why_flagged', 'N/A')}<br/>"
                    f"<b>Rule:</b> {finding.get('rule_id', 'N/A')} - {finding.get('rule_reference', '')}<br/>"
                    f"<b>Confidence:</b> {finding.get('confidence_score', 0)}%<br/>"
                    f"<b>Status:</b> {finding.get('status', 'N/A').upper()}"
                )
                
                elements.append(Paragraph(finding_text, styles['Normal']))
                elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def _build_score_section(self, data: Dict, styles) -> List:
        """Build compliance score section"""
        elements = []
        
        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=10
        )
        
        elements.append(Paragraph("4. PRELIMINARY COMPLIANCE SCORE", heading_style))
        
        score_data = data.get("compliance_score", {})
        overall = score_data.get("overall_score", 0)
        
        # Overall score
        score_text = f"Overall Preliminary Score: <b>{overall}/100</b>"
        elements.append(Paragraph(score_text, styles['Normal']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Category breakdown
        categories = score_data.get("categories", {})
        category_data = [["Category", "Score", "Max"]]
        
        for category, score in categories.items():
            max_score = {
                "mandatory_declarations": 40,
                "text_readability": 20,
                "information_extraction": 25,
                "data_consistency": 15
            }.get(category, 100)
            
            category_data.append([
                category.replace("_", " ").title(),
                f"{score:.1f}",
                str(max_score)
            ])
        
        table = Table(category_data, colWidths=[2*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.1*inch))
        
        # Interpretation
        interpretation = score_data.get("interpretation", "")
        elements.append(Paragraph(f"<i>{interpretation}</i>", styles['Normal']))
        
        return elements
    
    def _build_recommendations(self, data: Dict, styles) -> List:
        """Build recommendations section"""
        elements = []
        
        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=10
        )
        
        elements.append(Paragraph("5. RECOMMENDATIONS", heading_style))
        
        recommendations = data.get("compliance_score", {}).get("next_steps", [])
        
        for rec in recommendations:
            elements.append(Paragraph(f"• {rec}", styles['Normal']))
        
        return elements
    
    def _build_verification_section(self, styles) -> List:
        """Build inspector verification section"""
        elements = []
        
        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=10
        )
        
        elements.append(Paragraph("6. INSPECTOR VERIFICATION", heading_style))
        
        verification_data = [
            ["Inspector Name:", "_" * 40],
            ["Verification Date:", "_" * 40],
            ["Decision (Approve/Reject):", "_" * 40],
            ["Comments:", "_" * 40],
            ["", "_" * 40]
        ]
        
        table = Table(verification_data, colWidths=[1.5*inch, 3.5*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LINEABOVE', (1, 0), (1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        
        return elements
    
    def _build_disclaimer(self, styles) -> List:
        """Build disclaimer section"""
        elements = []
        
        disclaimer_text = (
            "<b>⚠️ IMPORTANT DISCLAIMER:</b><br/>"
            "This is an AI-assisted PRELIMINARY ASSESSMENT ONLY.<br/>"
            "• Cannot replace human expert verification by legal metrology officers<br/>"
            "• All preliminary findings must be verified by authorized personnel<br/>"
            "• Based on OCR extraction which may have limitations<br/>"
            "• Legal compliance determination must be made by qualified personnel<br/>"
            "• This report does NOT constitute an official legal compliance certification"
        )
        
        elements.append(Paragraph(disclaimer_text, styles['Normal']))
        
        return elements


# Singleton instance
pdf_report_generator = PDFReportGenerator()
