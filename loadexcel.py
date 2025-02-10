#load PropertyTycoonBoardData.xlsx data to the game 
# currently only load data with PropertyTycoonBoardData.xlsx ,not include PropertyTycoonCardData.xlsx
# will do if have time
import pandas as pd
import os

def load_property_data(filename="assets/gamedata/PropertyTycoonBoardData.xlsx"):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, filename)
        print(f"Loading property data from: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"File not found at {file_path}")
            alt_path = os.path.join(current_dir, "Useful Canvas file", "PropertyTycoonBoardData.xlsx")
            if os.path.exists(alt_path):
                file_path = alt_path
                print(f"Using alternative path: {alt_path}")
            else:
                raise FileNotFoundError(f"Neither {file_path} nor {alt_path} exists")

        df = pd.read_excel(file_path, header=3)
        df = df.fillna('')
        print(f"Successfully read Excel file. Found {len(df)} rows")

        properties_data = {}
        for _, row in df.iterrows():
            try:
                position = int(row['Position'])
                property_name = str(row['Space/property']).strip()
                
                print(f"Processing position {position}: {property_name}")
                
                property_data = {
                    "name": property_name,
                    "group": str(row['Group']).strip() if row['Group'] else None,
                    "action": str(row['Action']).strip() if row['Action'] else None
                }

                if str(row['Can be bought?']).strip().lower() == 'yes' and row['£']:
                    try:
                        property_data.update({
                            "price": int(float(str(row['£']).replace('£', '').strip())),
                            "rent": int(float(str(row['£.1']).replace('£', '').strip() or '0')),
                            "owner": None,
                            "house_costs": []
                        })
                        
                        for i in range(2, 7):
                            cost = row.get(f'£.{i}', '')
                            if cost and str(cost).strip():
                                try:
                                    property_data["house_costs"].append(
                                        int(float(str(cost).replace('£', '').strip()))
                                    )
                                except (ValueError, TypeError):
                                    continue
                    except (ValueError, TypeError) as e:
                        print(f"Error processing costs for position {position}: {e}")
                        continue

                properties_data[str(position)] = property_data
                
            except (ValueError, TypeError) as e:
                print(f"Error processing row: {e}")
                continue

        print(f"Successfully loaded {len(properties_data)} properties")
        return properties_data

    except Exception as e:
        print(f"Error loading Excel file: {e}")
        import traceback
        traceback.print_exc()
        return None

def load_game_text(filename="assets/gamedata/PropertyTycoonCardData.xlsx", sheet_name="Game Text"):
    try:
        file_path = os.path.join(os.path.dirname(__file__), filename)
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        card_data = {}
        for index, row in df.iterrows():
            key = row['Key'] 
            text = row['Text']  
            card_data[key] = text
        print(f"Game text loaded from '{sheet_name}' sheet in Excel.")
        return card_data

    except FileNotFoundError:
        print(f"{filename} not found. Make sure it's in the same directory as the script.")
        return None
    except KeyError:
        print(f"{sheet_name}' or columns 'Key' and 'Text' not found in {filename}.")
        return None
    except Exception as e:
        print(f"Error loading card data from Excel: {e}")
        return None