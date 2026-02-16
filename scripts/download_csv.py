import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os

# Configurazione
PATH_CARTELLA = r"C:\Users\marco\Desktop\The Garret\Sincronizzazione_Brevo"
ID_FOGLIO = "1L7PbJSD_nz2lwyK56HLaiRV5BIFn3jThGMNSvDWdiPQ" 
NOME_FILE_CSV = "Brevo.csv"

def download_csv():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    
    # Apre il foglio usando l'ID (più sicuro)
    sheet = client.open_by_key(ID_FOGLIO).get_worksheet(0)
    
    # Prende TUTTI i valori come lista di liste (evita l'errore dei duplicati)
    all_values = sheet.get_all_values()
    
    # Carica in Pandas: la prima riga diventa l'intestazione
    df = pd.DataFrame(all_values[1:], columns=all_values[0])
    
    # Salva in CSV
    df.to_csv(os.path.join(PATH_CARTELLA, NOME_FILE_CSV), index=False, encoding='utf-8')
    print(f"Successo! File {NOME_FILE_CSV} generato correttamente.")

if __name__ == "__main__":
    download_csv()