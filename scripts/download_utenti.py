import requests
import pandas as pd
import os
from bs4 import BeautifulSoup

# --- CONFIGURAZIONE ---
PATH_CARTELLA = r"scripts/"
NOME_FILE_CSV = "Brevo.csv"
URL_LOGIN = "https://clubmanager-pro.com/Identity/Account/Login"
URL_API_DATI = "https://clubmanager-pro.com/Users/Users/UsersList"

USERNAME = 'FrauMarco'
PASSWORD = 'cmPro?2024'

def main():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*'
    })

    try:
        # 1. Recupero Token Iniziale
        print("1. Recupero token di accesso...")
        r_init = session.get(URL_LOGIN)
        soup = BeautifulSoup(r_init.text, 'html.parser')
        token = soup.find('input', {'name': '__RequestVerificationToken'})['value']

        # 2. Login
        print("2. Tentativo di Login...")
        payload_login = {
            'Input.Username': USERNAME,
            'Input.Password': PASSWORD,
            '__RequestVerificationToken': token,
            'Input.RememberMe': 'false'
        }
        # In .NET il login deve inviare i dati come form
        res_login = session.post(URL_LOGIN, data=payload_login, headers={'Referer': URL_LOGIN})

        # Verifica se siamo ancora sulla pagina di login (segno di fallimento)
        if "Identity/Account/Login" in res_login.url and res_login.status_code == 200:
            # Se la risposta contiene ancora il form di login, le credenziali o il token sono errati
            print("ERRORE: Login fallito. Controlla Username e Password.")
            return

        print("Login effettuato con successo!")

        # 3. Download Dati
        print("3. Estrazione anagrafica completa...")
        
        # Header specifici per la chiamata API JSON
        headers_api = {
            'Content-Type': 'application/json; charset=utf-8',
            'X-Requested-With': 'XMLHttpRequest',
            'RequestVerificationToken': token, # Fondamentale per sistemi .NET
            'Referer': 'https://clubmanager-pro.com/Users/Users/UsersList'
        }

        payload_api = {
            "requiresCounts": True,
            "params": {
                "fr_Disuso": "0", "fa_Utente": None, "f_Codice": "", "f_CodiceFiscale": "",
                "f_EMail": "", "f_Sesso": "0", "f_DaDataInserimento": "", "f_ADataInserimento": "",
                "f_filtroCompleannoRange": False, "fs_MeseCompleanno": None, "f_GiornoCompleanno": "",
                "f_DaDataCompleanno": "", "f_ADataCompleanno": "", "f_DaEta": "", "f_AEta": "",
                "f_NumTel": "", "f_DaDataScadCertificato": "", "f_ADataScadCertificato": "",
                "f_NoCertificato": False, "f_NoAssicurazione": False, "f_StatoAttivazione": "-1",
                "f_Privacy": "-1", "f_NewsLetter": "-1", "f_TPP": "-1", "f_HasEmail": "-1",
                "f_CAP": "", "f_DaDataScadAssicurazione": "", "f_ADataScadAssicurazione": "",
                "f_NumAssicurazione": "", "f_IsMoroso": "-1", "f_HasFederation": "-1",
                "filtroCompleannoRange": False, "RefreshCache": True
            },
            "skip": 0,
            "take": 100000 
        }

        response = session.post(URL_API_DATI, json=payload_api, headers=headers_api)

        # Se il server ci ha rimandato al login, la risposta sarà HTML (inizia con <)
        if response.text.strip().startswith("<!DOCTYPE"):
            print("ERRORE: La sessione è scaduta o il server ha rifiutato l'accesso API.")
            print("Il server ha restituito una pagina HTML invece dei dati JSON.")
            return

        json_data = response.json()
        
        # Estrazione dati (gestiamo diverse possibili strutture del JSON)
        data_list = json_data.get('data') or json_data.get('items') or json_data
        
        if data_list:
            df = pd.DataFrame(data_list)
            output_path = os.path.join(PATH_CARTELLA, NOME_FILE_CSV)
            df.to_csv(output_path, index=False, encoding='utf-8')
            print(f"--- OPERAZIONE COMPLETATA ---")
            print(f"File salvato in: {output_path}")
            print(f"Righe esportate: {len(df)}")
        else:
            print("La risposta è arrivata ma non contiene dati.")

    except Exception as e:
        print(f"Errore critico: {e}")

if __name__ == "__main__":
    main()