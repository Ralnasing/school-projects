import pandas as pd
from typing import Dict, Optional

def load_tls_cipher_lookup(csv_path: str) -> Dict[str, Dict[str, str]]:
    def normalize_value(value: str) -> Optional[str]:
        if pd.isna(value) or not isinstance(value, str):
            return None
            
        try:
            # Odstranit whitespace a rozdělit podle čárek
            parts = [p.strip() for p in str(value).split(',')]
            # Odstranit 0x prefixy a spojit
            hex_str = ''.join(p.replace('0x', '').replace('0X', '') for p in parts).upper()
            
            # Ověřit, že je to validní hex
            int(hex_str, 16)
            
            return f"0x{hex_str}"
        except (ValueError, AttributeError):
            return None

    try:
        df = pd.read_csv(csv_path)
        
        # Ověřit požadované sloupce
        required_columns = ["Value", "Description"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"[TLS] Missing columns: {missing_columns}")
            return {}

        df["NormalizedValue"] = df["Value"].apply(normalize_value)

        cipher_dict = {}
        for _, row in df.iterrows():
            normalized_val = row["NormalizedValue"]
            if normalized_val:  # Pouze pokud je normalizace úspěšná
                cipher_dict[normalized_val] = {
                    "description": str(row["Description"]) if pd.notna(row["Description"]) else "Unknown",
                    "recommended": "Yes" if str(row.get("Recommended", "")).strip().upper() == "Y" else "No"
                }

        print(f"[TLS] Loaded {len(cipher_dict)} cipher definitions")
        return cipher_dict

    except FileNotFoundError:
        print(f"[TLS] Cipher lookup file not found: {csv_path}")
        return {}
    except Exception as e:
        print(f"[TLS] Error loading cipher lookup: {e}")
        return {}