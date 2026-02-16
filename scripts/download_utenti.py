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
        res_login = session.post(URL_LOGIN, data=payload_login, headers={'Referer': URL_LOGIN})

        if "Identity/Account/Login" in res_login.url and res_login.status_code == 200:
            print("ERRORE: Login fallito. Controlla Username e Password.")
            return

        print("Login effettuato con successo!")

        # 3. Download Dati
        print("3. Estrazione anagrafica completa...")
        
        headers_api = {
            'Content-Type': 'application/json; charset=utf-8',
            'X-Requested-With': 'XMLHttpRequest',
            'RequestVerificationToken': token,
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

        if response.text.strip().startswith("<!DOCTYPE"):
            print("ERRORE: La sessione è scaduta o il server ha rifiutato l'accesso API.")
            return

        json_data = response.json()
        
        print(f"Tipo json_data: {type(json_data)}")
        print(f"Chiavi json_data: {json_data.keys() if isinstance(json_data, dict) else 'Non è un dict'}")
        
        # Prova diverse strutture possibili
        if isinstance(json_data, dict):
            if 'result' in json_data:
                data_list = json_data['result']
            elif 'data' in json_data:
                data_list = json_data['data']
            elif 'items' in json_data:
                data_list = json_data['items']
            elif 'Result' in json_data:
                data_list = json_data['Result']
            else:
                print(f"Chiavi disponibili: {list(json_data.keys())}")
                # Stampa un campione dei valori
                for key in list(json_data.keys())[:5]:
                    val = json_data[key]
                    print(f"  {key}: {type(val)} - {str(val)[:100] if val else 'None'}")
                data_list = None
        else:
            data_list = json_data
        
        print(f"Tipo data_list: {type(data_list)}")
        if isinstance(data_list, list) and len(data_list) > 0:
            print(f"Numero elementi: {len(data_list)}")
            print(f"Tipo primo elemento: {type(data_list[0])}")
        
        if data_list:
            # Estrai i campi necessari dalla struttura annidata
            utenti_estratti = []
            
            for utente in data_list:
                # I dati sono dentro 'Anagrafica'
                anagrafica = utente.get('Anagrafica', {})
                
                if anagrafica:
                    nome = anagrafica.get('Nome', '')
                    cognome = anagrafica.get('Cognome', '')
                    email = utente.get('Email') or anagrafica.get('Email', '')
                    cellulare = utente.get('Cellulare', '')
                    codice_fiscale = anagrafica.get('CodiceFiscale', '')
                    
                    utenti_estratti.append({
                        'Nome': nome,
                        'Cognome': cognome,
                        'Email': email,
                        'Cellulare': cellulare,
                        'CodiceFiscale': codice_fiscale
                    })
            
            df = pd.DataFrame(utenti_estratti)
            output_path = os.path.join(PATH_CARTELLA, NOME_FILE_CSV)
            df.to_csv(output_path, index=False, encoding='utf-8')
            print(f"--- OPERAZIONE COMPLETATA ---")
            print(f"File salvato in: {output_path}")
            print(f"Righe esportate: {len(df)}")
            print(f"Colonne: {list(df.columns)}")
        else:
            print("La risposta è arrivata ma non contiene dati.")

    except Exception as e:
        print(f"Errore critico: {e}")

if __name__ == "__main__":
    main()