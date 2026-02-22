from fpdf import FPDF
import json
import os

class AgriReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'AI Crop Advisor - Farm Report', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf(data, output_path):
    pdf = AgriReport()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Farmer Profile
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "1. Farmer Profile", 0, 1)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Crop: {data.get('crop', 'N/A')}", 0, 1)
    pdf.cell(0, 10, f"Location: {data.get('location', 'N/A')}", 0, 1)
    pdf.cell(0, 10, f"Field Size: {data.get('field_size', 'N/A')} Acres", 0, 1)
    pdf.ln(5)

    # Soil Analysis
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "2. Soil Intelligence", 0, 1)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"pH: {data.get('ph', 'N/A')}, EC: {data.get('ec', 'N/A')}, OC: {data.get('oc', 'N/A')}%", 0, 1)
    pdf.cell(0, 10, f"N: {data.get('N', 'N/A')}, P: {data.get('P', 'N/A')}, K: {data.get('K', 'N/A')}", 0, 1)
    pdf.cell(0, 10, f"Moisture: {data.get('moisture', 'N/A')}%", 0, 1)
    pdf.cell(0, 10, f"Texture: {data.get('texture', 'N/A')}", 0, 1)
    pdf.ln(5)

    # Economic Analysis (Summary)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "3. Economic Analysis", 0, 1)
    pdf.set_font("Arial", size=12)
    
    pdf.cell(0, 10, f"Estimated Residue: {float(data.get('field_size', 1.0)) * 2.5:.1f} Tons", 0, 1)
    
    if "analysis_results" in data:
        results = data["analysis_results"]
        
        # Soil Details
        if "soil_issues" in results:
            pdf.set_font("Arial", 'I', 12)
            pdf.cell(0, 10, "Soil Issues Found:", 0, 1)
            pdf.set_font("Arial", size=12)
            for issue in results["soil_issues"]:
                pdf.cell(0, 10, f"- {issue}", 0, 1)
        
        if "soil_treatments" in results: # Updated key from implementaiton
            pdf.set_font("Arial", 'I', 12)
            pdf.cell(0, 10, "Recommended Treatments:", 0, 1)
            pdf.set_font("Arial", size=12)
            for treat in results["soil_treatments"]:
                pdf.cell(0, 10, f"- {treat}", 0, 1)

        if "ai_soil_advice" in results:
            pdf.set_font("Arial", 'I', 12)
            pdf.cell(0, 10, "AI Recommended Chemicals:", 0, 1)
            pdf.set_font("Arial", size=12)
            for chem in results["ai_soil_advice"].get("top_chemicals", []):
                pdf.cell(0, 10, f"• {chem}", 0, 1)

        pdf.ln(5)

        # Economic Details
        if "best_strategy" in results:
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, f"Recommended Strategy: {results['best_strategy']}", 0, 1)
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, f"Reason: {results.get('strategy_reason', 'N/A')}")
        
        if "profit_comparison" in results:
            comp = results["profit_comparison"]
            pdf.cell(0, 10, f"Estimated Selling Profit: Rs.{comp.get('selling_profit', 0):,.0f}", 0, 1)
            pdf.cell(0, 10, f"Estimated Burning Loss: Rs.{comp.get('burning_loss', 0):,.0f}", 0, 1)

        if "ai_economic_advice" in results:
            pdf.set_font("Arial", 'I', 12)
            pdf.cell(0, 10, "AI Economic Forecast:", 0, 1)
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, results["ai_economic_advice"])

        pdf.ln(5)

        # 4. Government Subsidies
        if "detected_scheme" in results:
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "4. Government Subsidies", 0, 1)
            pdf.set_font("Arial", size=12)
            pdf.cell(0, 10, f"Matched Scheme: {results['detected_scheme']}", 0, 1)
            pdf.cell(0, 10, f"Direct Benefit: Rs.{results.get('subsidy_per_ton', 0)}/ton", 0, 1)
            pdf.cell(0, 10, f"Total Calculated Subsidy: Rs.{results.get('total_subsidy', 0):,.0f}", 0, 1)
            pdf.cell(0, 10, f"Total Net Gain: Rs.{results.get('total_net_gain', 0):,.0f}", 0, 1)
            pdf.ln(5)

        # 5. Buyer Recommendations
        if "best_buyer" in results:
            buyer = results["best_buyer"]
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "5. Buyer Recommendations", 0, 1)
            pdf.set_font("Arial", size=12)
            pdf.cell(0, 10, f"Top Matched Buyer: {buyer.get('name', 'N/A')}", 0, 1)
            pdf.cell(0, 10, f"Offered Price: Rs.{buyer.get('price', 0):,.0f}/ton", 0, 1)
            pdf.cell(0, 10, f"Proposed Quantity: {buyer.get('residue', 0):.2f} tons", 0, 1)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, f"Estimated Income: Rs.{buyer.get('income', 0):,.0f}", 0, 1)

    pdf.output(output_path)
    return output_path
