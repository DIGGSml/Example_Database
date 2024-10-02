import sqlite3
from lxml import etree
import re

def connect_to_database(db_path):
    return sqlite3.connect(db_path)

def parse_diggs_xml(xml_file):
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(xml_file, parser)
    return tree.getroot()

def extract_namespaces(root):
    ns = {k if k is not None else 'default': v for k, v in root.nsmap.items()}
    if None in ns:
        ns['default'] = ns.pop(None)
    return ns

def safe_xpath(element, xpath, namespaces):
    try:
        return element.xpath(xpath, namespaces=namespaces)[0].text
    except IndexError:
        return None

def extract_point_data(root, ns):
    point_data = []
    for borehole in root.xpath(".//default:Borehole", namespaces=ns):
        try:
            id = borehole.get(f"{{{ns['gml']}}}id")
            
            # Find location information
            pos = safe_xpath(borehole, ".//default:referencePoint//default:pos", ns)
            if pos:
                longitude, latitude, elevation = map(float, pos.split())
            else:
                print(f"Warning: No location found for borehole {id}")
                longitude = latitude = elevation = 0.0
            
            spt_source = safe_xpath(borehole, ".//default:BusinessAssociate/default:name", ns) or "Unknown"
            date_complete = safe_xpath(borehole, ".//default:TimeInterval/default:start", ns) or "Unknown"
            total_depth = float(safe_xpath(borehole, ".//default:totalMeasuredDepth", ns) or 0)
            
            point_data.append((id, pos, "SPT", spt_source, elevation, latitude, longitude, id, date_complete, total_depth))
            print(f"Processed borehole: {id}")
        except Exception as e:
            print(f"Error processing borehole {id}: {str(e)}")
    
    print(f"Extracted {len(point_data)} point data entries")
    return point_data

def extract_spt_data(root, ns):
    spt_data = []
    for measurement in root.xpath(".//default:Test", namespaces=ns):
        try:
            id = measurement.get(f"{{{ns['gml']}}}id")
            functionalkey = safe_xpath(measurement, ".//default:samplingFeatureRef", ns)
            if functionalkey:
                functionalkey = functionalkey.split('#')[-1]
            
            location = safe_xpath(measurement, ".//default:LinearExtent/default:posList", ns)
            if location:
                sample_top, sample_bottom = map(float, location.split())
            else:
                print(f"Warning: No location found for measurement {id}")
                sample_top = sample_bottom = 0.0
            
            n_value = int(safe_xpath(measurement, ".//default:dataValues", ns) or 0)
            
            blow_counts = measurement.xpath(".//diggs_geo:DriveSet/diggs_geo:blowCount", namespaces=ns)
            penetrations = measurement.xpath(".//diggs_geo:DriveSet/diggs_geo:penetration", namespaces=ns)
            
            blow1, blow2, blow3, blow4 = [int(blow.text) if blow is not None else None for blow in blow_counts + [None] * (4 - len(blow_counts))]
            pen1, pen2, pen3, pen4 = [float(pen.text) if pen is not None else None for pen in penetrations + [None] * (4 - len(penetrations))]
            
            sample_num = int(re.search(r'Num_(\d+)', id).group(1)) if re.search(r'Num_(\d+)', id) else 0
            sample_length = sample_bottom - sample_top
            
            spt_data.append((sample_bottom, sample_top, functionalkey, sample_num, sample_length, blow1, blow2, blow3, blow4, pen1, pen2, pen3, pen4))
            print(f"Processed SPT measurement: {id}")
        except Exception as e:
            print(f"Error processing SPT measurement {id}: {str(e)}")
    
    print(f"Extracted {len(spt_data)} SPT data entries")
    return spt_data

def extract_lith_data(root, ns):
    lith_data = []
    for observation in root.xpath(".//default:LithologySystem", namespaces=ns):
        try:
            id = observation.get(f"{{{ns['gml']}}}id")
            functionalkey = safe_xpath(observation, ".//default:samplingFeatureRef", ns)
            if functionalkey:
                functionalkey = functionalkey.split('#')[-1]
            
            location = safe_xpath(observation, ".//default:LinearExtent/default:posList", ns)
            if location:
                sample_top, sample_bottom = map(float, location.split())
            else:
                print(f"Warning: No location found for lithology {id}")
                sample_top = sample_bottom = 0.0
            
            desc_and_notes = safe_xpath(observation, ".//default:lithDescription", ns) or ""
            
            lith_data.append((sample_top, sample_bottom, desc_and_notes, functionalkey))
            print(f"Processed lithology: {id}")
        except Exception as e:
            print(f"Error processing lithology {id}: {str(e)}")
    
    print(f"Extracted {len(lith_data)} lithology data entries")
    return lith_data

def insert_data(conn, point_data, spt_data, lith_data):
    cursor = conn.cursor()
    
    cursor.executemany('''
    INSERT OR REPLACE INTO Point_Table (id, geom, spt_type, spt_source, elevation, latitude, longitude, functionalkey, date_complete, total_depth)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', point_data)
    
    cursor.executemany('''
    INSERT OR REPLACE INTO SPT_Table (sample_bottom, sample_top, functionalkey, sample_num, sample_length, blow1, blow2, blow3, blow4, penetration1, penetration2, penetration3, penetration4)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', spt_data)
    
    cursor.executemany('''
    INSERT OR REPLACE INTO Lith_Table (sample_top, sample_bottom, desc_and_notes, functionalkey)
    VALUES (?, ?, ?, ?)
    ''', lith_data)
    
    conn.commit()

def main(xml_file, db_path):
    root = parse_diggs_xml(xml_file)
    print("Root tag:", root.tag)
    print("Root attributes:", root.attrib)
    
    ns = extract_namespaces(root)
    print("Extracted namespaces:", ns)
    
    print("First-level children of root:")
    for child in list(root)[:5]:
        print(f"- {child.tag}")
    
    point_data = extract_point_data(root, ns)
    spt_data = extract_spt_data(root, ns)
    lith_data = extract_lith_data(root, ns)
    
    if point_data or spt_data or lith_data:
        conn = connect_to_database(db_path)
        insert_data(conn, point_data, spt_data, lith_data)
        conn.close()
        print("Data imported successfully!")
    else:
        print("No data extracted. Check the XML structure and xpath queries.")

if __name__ == "__main__":
    xml_file = "/workspaces/Example_Database/Simple Database Structure/Geosetta_01-10-2024-15-21-42_diggs.xml"
    db_path = "/workspaces/Example_Database/Simple Database Structure/simple_geotechnical_database.db"
    main(xml_file, db_path)