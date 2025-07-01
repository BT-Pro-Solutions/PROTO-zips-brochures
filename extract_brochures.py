#!/usr/bin/env python3
"""
Script to extract brochure data from HTML file and convert to JSON format
"""

import re
import json
from pathlib import Path

def extract_brochure_data(html_file_path):
    """Extract brochure data from HTML file"""
    
    # Read the HTML file
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Initialize the main data structure
    brochure_data = {
        "equipmentBrochures": {},
        "productBrochures": {}
    }
    
    # Find the Equipment Brochures section (starts at line 1)
    equipment_match = re.search(r'<div class="sfContentBlock"><h1><strong>Equipment Brochures</strong></h1>', html_content)
    
    # Find the Product Brochures section (starts around line 1996)
    product_match = re.search(r'<div class="sfContentBlock"><h1><strong>Product Brochures</strong></h1>', html_content)
    
    if equipment_match and product_match:
        # Extract Equipment Brochures section
        equipment_section = html_content[equipment_match.start():product_match.start()]
        brochure_data["equipmentBrochures"] = extract_brands_and_brochures(equipment_section, "equipment")
        
        # Extract Product Brochures section  
        product_section = html_content[product_match.start():]
        brochure_data["productBrochures"] = extract_brands_and_brochures(product_section, "product")
    
    return brochure_data

def extract_brand_names_from_html(section_html, section_type):
    """Extract brand names from h2 headers and map them to content IDs"""
    brand_mapping = {}
    
    # Find all brand headers and their associated content sections
    if section_type == "equipment":
        # Pattern for equipment brochures section
        pattern = r'<div id="Content_(C\d+)_Col\d+"[^>]*><div class="sfContentBlock"><h2><strong>([^<]+)</strong></h2>'
    else:
        # Pattern for product brochures section - includes both <strong> and non-<strong> variants
        pattern = r'<div id="Content_(C\d+)_Col\d+"[^>]*><div class="sfContentBlock"><h2>(?:<strong>)?([^<]+?)(?:</strong>)?</h2>'
    
    matches = re.findall(pattern, section_html)
    
    for content_id, brand_name in matches:
        brand_mapping[f'Content_{content_id}'] = brand_name.strip()
    
    return brand_mapping

def extract_brand_from_url(url):
    """Extract brand name from URL path - comprehensive mapping for parts-brochures"""
    
    # Extract the folder name after parts-brochures/ or new-equipment-brochures/
    url_lower = url.lower()
    
    # Comprehensive brand mapping based on URL folder structure
    brand_patterns = {
        # Product Brochures (parts-brochures)
        'arrow-safety-device': 'Arrow Safety Device',
        'ba-products': 'BA Products',
        'buyers-products': 'Buyers Products',
        'challenger': 'Challenger',
        'code-3': 'Code 3',
        'cortland': 'Cortland',
        'coxreels': 'Coxreels',
        'deweze': 'Deweze',
        'fastenal': 'Fastenal',
        'ferno-washington': 'Ferno Washington',
        'garmin': 'Garmin',
        'haldex': 'Haldex',
        'hamilton': 'Hamilton',
        'hopkins': 'Hopkins',
        'in-the-ditch': 'In The Ditch',
        'kinedyne': 'Kinedyne',
        'kussmaul': 'Kussmaul',
        'master-lock': 'Master Lock',
        'miller': 'Miller',
        'muncie-power': 'Muncie Power',
        'parker': 'Parker',
        'prime-design': 'Prime Design',
        'ramsey-winch': 'Ramsey Winch',
        'ramsey': 'Ramsey',
        'reese': 'Reese',
        'rki': 'RKI',
        'saf-holland': 'SAF-Holland',
        'stellar': 'Stellar',
        'streamlight': 'Streamlight',
        'technology-research': 'Technology Research',
        'tiger-tools': 'Tiger Tools',
        'timbren': 'Timbren',
        'towmate': 'TowMate',
        'trimax': 'Trimax',
        'voltair': 'Voltair',
        'warn': 'Warn',
        'warning-products': 'Warning Products',
        'westin': 'Westin',
        'whelen': 'Whelen',
        'will-burt': 'Will-Burt',
        'wreckmaster': 'Wreckmaster',
        'zacklift': 'Zacklift',
        
        # Equipment Brochures (new-equipment-brochures)
        'auto-crane': 'Auto Crane',
        'chevron-equipment': 'Chevron Equipment',
        'in-the-ditch-equipment': 'In The Ditch Equipment',
        'sidepullers': 'Sidepullers',
        'warner-service-bodies': 'Warner Service Bodies',
        'xl-specialized': 'XL Specialized',
        'century-equipment': 'Century Equipment',
        'jerr-dan': 'Jerr-Dan',
        'holmes': 'Holmes',
        'weld-built': 'Weld Built',
        'dynamic': 'Dynamic',
        'vulcan': 'Vulcan',
        'landoll': 'Landoll',
        'nrc': 'NRC'
    }
    
    # Extract the brand folder from the URL
    for pattern, brand_name in brand_patterns.items():
        if f'/{pattern}/' in url_lower:
            return brand_name
    
    # Try to extract brand from folder structure
    if '/parts-brochures/' in url_lower:
        # Extract folder name after parts-brochures/
        match = re.search(r'/parts-brochures/([^/]+)/', url_lower)
        if match:
            folder_name = match.group(1)
            # Convert folder name to brand name (title case, replace hyphens)
            brand_name = folder_name.replace('-', ' ').title()
            return brand_name
    
    if '/new-equipment-brochures/' in url_lower:
        # Extract folder name after new-equipment-brochures/
        match = re.search(r'/new-equipment-brochures/([^/]+)/', url_lower)
        if match:
            folder_name = match.group(1)
            # Convert folder name to brand name (title case, replace hyphens)
            brand_name = folder_name.replace('-', ' ').title()
            return brand_name
    
    return None

def extract_brands_and_brochures(section_html, section_type):
    """Extract brand groups and their brochures from a section"""
    brands = {}
    
    # First, try to extract brand names from HTML headers
    brand_mapping = extract_brand_names_from_html(section_html, section_type)
    
    # Add some known mappings for equipment brochures
    equipment_mappings = {
        'Content_C003': 'Auto Crane',
        'Content_C118': 'Chevron Equipment', 
        'Content_C021': 'In The Ditch Equipment',
        'Content_C019': 'Miller',
        'Content_C121': 'Sidepullers',
        'Content_C116': 'Warner Service Bodies',
        'Content_C124': 'XL Specialized',
        'Content_C114': 'Century Equipment',
        'Content_C115': 'Jerr-Dan',
        'Content_C122': 'Holmes',
        'Content_C117': 'Weld Built',
        'Content_C120': 'Dynamic',
        'Content_C123': 'Vulcan',
        'Content_C125': 'Landoll',
        'Content_C119': 'NRC'
    }
    
    if section_type == "equipment":
        brand_mapping.update(equipment_mappings)
    
    # Find all brochure links with their content IDs
    link_pattern = r'<a id="(Content_C\d+)_masterListView[^"]*" class="sfdownloadTitle" href="([^"]+)"[^>]*>([^<]+)</a>'
    matches = re.findall(link_pattern, section_html)
    
    for content_id_full, url, title in matches:
        # Extract the content ID (e.g., Content_C003)
        content_id = re.match(r'(Content_C\d+)', content_id_full).group(1)
        
        # Get brand name from mapping
        brand_name = brand_mapping.get(content_id)
        
        # If not found in mapping, try to extract from URL
        if not brand_name:
            brand_name = extract_brand_from_url(url)
        
        # Fallback to unknown brand
        if not brand_name:
            brand_name = f'Unknown Brand ({content_id})'
        
        # Initialize brand if not exists
        if brand_name not in brands:
            brands[brand_name] = []
        
        # Clean up the title and URL
        title = title.strip()
        url = url.strip()
        
        # Add brochure to brand
        brands[brand_name].append({
            "title": title,
            "url": url
        })
    
    return brands

def main():
    """Main function to run the extraction"""
    html_file = "Brochures _ Carriers, Wreckers, Trucks & Trailers _ Zip's.html"
    
    if not Path(html_file).exists():
        print(f"Error: HTML file '{html_file}' not found")
        return
    
    print("Extracting brochure data...")
    brochure_data = extract_brochure_data(html_file)
    
    # Save to JSON file
    output_file = "brochures_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(brochure_data, f, indent=2, ensure_ascii=False)
    
    print(f"Data extracted and saved to {output_file}")
    
    # Print summary
    print("\nSummary:")
    print(f"Equipment Brochures - {len(brochure_data['equipmentBrochures'])} brands:")
    for brand, brochures in brochure_data['equipmentBrochures'].items():
        print(f"  - {brand}: {len(brochures)} brochures")
    
    print(f"\nProduct Brochures - {len(brochure_data['productBrochures'])} brands:")
    for brand, brochures in brochure_data['productBrochures'].items():
        print(f"  - {brand}: {len(brochures)} brochures")

if __name__ == "__main__":
    main() 