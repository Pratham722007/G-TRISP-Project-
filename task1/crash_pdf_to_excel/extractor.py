import pdfplumber
import re
from pathlib import Path
from typing import Dict, List, Optional

class CrashExtractor:
    """
    Logic for extracting structured data from Indian police crash report PDFs.
    """

    def __init__(self):
        # Mapping of internal keys to possible labels in the PDF
        self.field_map = {
            # Section 1 – Accident Summary
            "Accident_ID": ["Accident ID", "Accident_ID"],
            "FIR_CSR_Number": ["FIR/CSR Number", "FIR Number", "CSR Number"],
            "FIR_Date_Time": ["FIR Date & Time", "FIR Date Time", "Date and Time of FIR"],
            "Act": ["Act"],
            "Section": ["Section"],
            "State_Rule": ["State Rule", "State_Rule"],
            "Station_Name": ["Station Name", "Police Station Name"],
            "Station_Address": ["Station Address", "Police Station Address"],
            "Investigating_Officer": ["Investigating Officer", "Investigating_Officer"],
            "Field_Officer": ["Field Officer", "Field_Officer"],
            "District_Code": ["District Code", "District_Code"],
            "District_Name": ["District Name", "District_Name"],

            # Section 2 – Accident Details
            "Accident_Date_Time": ["Accident Date & Time", "Date and Time of Accident"],
            "Reporting_Date_Time": ["Reporting Date & Time", "Date and Time of Reporting"],
            "Landmark_Name": ["Landmark Name", "Landmark"],
            "Location_Details": ["Location Details", "Location"],
            "Severity": ["Severity"],
            "Road_Classification": ["Road Classification", "Class of Road"],
            "Road_Name_Street_Name": ["Road Name/Street Name", "Road Name"],
            "Local_Body": ["Local Body"],
            "Collision_Type": ["Collision Type"],
            "Collision_Nature": ["Collision Nature"],
            "Initial_Observation": ["Initial Observation"],
            "Traffic_Violation": ["Traffic Violation"],
            "Weather_Condition": ["Weather Condition"],
            "Light_Condition": ["Light Condition"],
            "Accident_Spot": ["Accident Spot"],
            "Visibility": ["Visibility"],
            "Remedial_Measures": ["Remedial Measures"],
            "Property_Damage": ["Property Damage"],
            "Approx_Damage_Value": ["Approx. Damage Value", "Damage Value"],
            "No_of_Vehicles_Involved": ["No. of Vehicles Involved", "Vehicles Involved"],

            # Section 4 – Vehicle Details
            "Vehicle_Reg_No": ["Vehicle Reg No", "Registration Number"],
            "Vehicle_Category": ["Vehicle Category"],
            "Vehicle_Type": ["Vehicle Type"],
            "Make_Model": ["Make / Model", "Make/Model"],
            "Fuel_Type": ["Fuel Type"],
            "Vehicle_Color": ["Vehicle Color"],
            "Engine_Number": ["Engine Number"],
            "Chassis_Number": ["Chassis Number"],
            "Insurance_Validity": ["Insurance Validity"],
            "Fitness_Validity": ["Fitness Validity"],
            "Vehicle_GVW": ["Vehicle GVW", "GVW"],
            "Seating_Capacity": ["Seating Capacity"],
            "Wheelbase": ["Wheelbase"],
            "Norms_Description": ["Norms Description"],
            "Brake_Type": ["Brake Type"],
            "Brake_Condition": ["Brake Condition"],
            "Damage_Status": ["Damage Status"],
            "Hit_and_Run": ["Hit and Run"],
            "Owner_Name": ["Owner Name"],

            # Section 5 – Driver Details
            "Driver_Name": ["Driver Name"],
            "Driver_Age": ["Driver Age"],
            "Driver_Gender": ["Driver Gender"],
            "Driver_Nationality": ["Driver Nationality"],
            "Driver_Education": ["Driver Education"],
            "Driver_Occupation": ["Driver Occupation"],
            "DL_Type": ["DL Type"],
            "DL_Status": ["DL Status"],
            "Non_Transport_DL_Validity": ["Non-Transport DL Validity", "DL Validity"],
            "Seatbelt_Helmet": ["Seatbelt/Helmet", "Safety Gear"],
            "Drunk_Driving": ["Drunk Driving"],
            "Cell_Phone_While_Driving": ["Cell Phone While Driving"],
            "Driver_Injury_Type": ["Driver Injury Type"],
            "Driver_Severity": ["Driver Severity"],
            "Blood_Group": ["Blood Group"],

            # Section 6 – Road Details
            "Area_Type": ["Area Type"],
            "Road_Owning_Agency": ["Road Owning Agency"],
            "Road_Surface_Type": ["Road Surface Type"],
            "Surface_Condition": ["Surface Condition"],
            "Carriageway_Type": ["Carriageway Type"],
            "Road_Width_Metres": ["Road Width (Metres)", "Road Width"],
            "Accident_Location_Geometry": ["Accident Location Geometry", "Geometry"],
            "Speed_Limit_KMPH": ["Speed Limit (KMPH)", "Speed Limit"],
            "Road_Markings": ["Road Markings"],
            "Road_Sign_Board": ["Road Sign Board"],
            "Physical_Divider": ["Physical Divider"],
            "Median_Type": ["Median Type"],
            "Pedestrian_Infrastructure": ["Pedestrian Infrastructure"],
            "Ongoing_Road_Work": ["Ongoing Road Work"]
        }

    def extract_from_pdf(self, pdf_path: Path) -> Dict[str, str]:
        """
        Extracts all required fields from a single PDF file.
        """
        data = {field: "" for field in self.field_map}
        # Initialize Section 3 fields (Persons Involved)
        person_fields = [
            "Killed_Driver", "Killed_Passenger", "Killed_Pedestrian", "Killed_Total",
            "Grievous_Injury_Total", "Minor_Injury_Total", "No_Injury_Total", "Total_Persons"
        ]
        for field in person_fields:
            data[field] = ""

        try:
            with pdfplumber.open(pdf_path) as pdf:
                full_text = ""
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
                
                lines = full_text.splitlines()
                
                # 1. Parse standard fields (Label : Value)
                self._parse_label_value_fields(lines, data)
                
                # 2. Parse Persons Involved table
                self._parse_persons_table(lines, data)

        except Exception as e:
            print(f"  Warning: Error processing {pdf_path.name}: {e}")
            # The dictionary is already initialized with empty strings
        
        return data

    def _parse_label_value_fields(self, lines: List[str], data: Dict[str, str]):
        """
        Scans lines for Label : Value patterns.
        """
        for line in lines:
            # Common pattern is "Label : Value" or "Label: Value" or "Label Value"
            # We'll check for " : " or ":" first
            if ":" in line:
                parts = line.split(":", 1)
                label_candidate = parts[0].strip()
                value_candidate = parts[1].strip()
                
                # Check which field this label maps to
                for field_key, labels in self.field_map.items():
                    if any(label.lower() in label_candidate.lower() for label in labels):
                        # If multiple fields match, we take the best one or append? 
                        # Usually, one line has one field.
                        if not data[field_key]: # Only fill if empty
                            data[field_key] = value_candidate
            else:
                # Handle "Label Value" patterns if needed, but "Label : Value" is more common
                # We can try to match labels directly at the start of the line
                for field_key, labels in self.field_map.items():
                    if data[field_key]: continue
                    for label in labels:
                        if line.strip().lower().startswith(label.lower()):
                            val = line[len(label):].strip()
                            if val:
                                data[field_key] = val
                                break

    def _parse_persons_table(self, lines: List[str], data: Dict[str, str]):
        """
        Extracts numeric values from the persons involved table.
        Table usually has rows for Driver, Passenger, Pedestrian, Total.
        And columns for Killed, Grievous Injury, Minor Injury, No Injury, Total.
        """
        # We look for rows starting with specific keywords
        keywords = ["Driver", "Passenger", "Pedestrian", "Total"]
        
        for line in lines:
            parts = line.split()
            if not parts: continue
            
            # Identify row
            row_type = None
            for kw in keywords:
                if kw.lower() == parts[0].lower().rstrip(':'):
                    row_type = kw
                    break
            
            if row_type:
                # Extract numbers from the line
                numbers = re.findall(r'\d+', line)
                if not numbers: continue
                
                # Assuming order: Killed, Grievous, Minor, No Injury, Total
                if row_type == "Driver" and len(numbers) >= 1:
                    data["Killed_Driver"] = numbers[0]
                elif row_type == "Passenger" and len(numbers) >= 1:
                    data["Killed_Passenger"] = numbers[0]
                elif row_type == "Pedestrian" and len(numbers) >= 1:
                    data["Killed_Pedestrian"] = numbers[0]
                elif row_type == "Total":
                    if len(numbers) >= 1: data["Killed_Total"] = numbers[0]
                    if len(numbers) >= 2: data["Grievous_Injury_Total"] = numbers[1]
                    if len(numbers) >= 3: data["Minor_Injury_Total"] = numbers[2]
                    if len(numbers) >= 4: data["No_Injury_Total"] = numbers[3]
                    if len(numbers) >= 5: data["Total_Persons"] = numbers[4]
