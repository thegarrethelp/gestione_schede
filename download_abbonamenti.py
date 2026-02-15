import requests
import pandas as pd
import os
from bs4 import BeautifulSoup

# --- CONFIGURAZIONE ---
PATH_CARTELLA = r"C:\Users\marco\Desktop\The Garret\Sincronizzazione_Brevo"
NOME_FILE_CSV = "Lista_Abbonamenti_Totale.csv"
URL_LOGIN = "https://clubmanager-pro.com/Identity/Account/Login"
URL_PAGINA_RICERCA = "https://clubmanager-pro.com/Ricerche/Ricerche/searchsubscriptionslistSN"
URL_API_ABB = "https://clubmanager-pro.com/Ricerche/Ricerche/SearchSubscriptionsListGrid"

USERNAME = 'FrauMarco'
PASSWORD = 'cmPro?2024'

def main():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
    })

    try:
        # 1. Login
        print("1. Login...")
        r_init = session.get(URL_LOGIN)
        soup_init = BeautifulSoup(r_init.text, 'html.parser')
        token = soup_init.find('input', {'name': '__RequestVerificationToken'})['value']
        
        payload_login = {'Input.Username': USERNAME, 'Input.Password': PASSWORD, '__RequestVerificationToken': token}
        session.post(URL_LOGIN, data=payload_login, allow_redirects=True)

        # 2. Inizializzazione Pagina
        print("2. Accesso modulo ricerche...")
        r_page = session.get(URL_PAGINA_RICERCA)
        soup_page = BeautifulSoup(r_page.text, 'html.parser')
        token_ricerca = soup_page.find('input', {'name': '__RequestVerificationToken'})['value']

        # 3. Estrazione Dati
        print("3. Estrazione abbonamenti in corso...")
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'RequestVerificationToken': token_ricerca,
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': URL_PAGINA_RICERCA
        }

        payload_api = {
            "requiresCounts": True,
            "params": {
                "fs_TipoRicercaAbbonamento": "22",
                "f_Abbonamenti": True,
                "f_Servizi": False,
                "f_QuoteAssociative": False,
                "f_DaDataScadenzaAbb": "01/01/2000",
                "f_ADataScadenzaAbb": "31/12/2026",
                "f_StatoPagamento": "-1",
                "f_NascondiSospesi": False,
                "f_NascondiScaduti": False,
                "RefreshCache": True,
                "HasIndirizzo": "true",
                "HasRecapiti": "true"
            },
            "skip": 0,
            "take": 50000 
        }

        response = session.post(URL_API_ABB, json=payload_api, headers=headers)
        data_json = response.json()
        
        # USARE 'result' INVECE DI 'data'
        raw_data = data_json.get('result', [])

        if not raw_data:
            print("Nessun dato trovato in 'result'.")
            return

        # 4. Mappatura campi reali (basata sul tuo output)
        print(f"4. Elaborazione di {len(raw_data)} record...")
        df = pd.DataFrame(raw_data)

        # Pulizia HTML dal campo 'Stato' (se presente)
        if 'Stato' in df.columns:
            df['Stato'] = df['Stato'].str.replace(r'<[^>]*>', '', regex=True)

        # 5. Salvataggio
        if not os.path.exists(PATH_CARTELLA): os.makedirs(PATH_CARTELLA)
        output_path = os.path.join(PATH_CARTELLA, NOME_FILE_CSV)
        df.to_csv(output_path, index=False, sep=';', encoding='utf-8-sig')
        
        print("-" * 30)
        print(f"SUCCESSO! File creato con {len(df)} righe.")
        print(f"Percorso: {output_path}")

    except Exception as e:
        print(f"Errore critico: {e}")

if __name__ == "__main__":
    main()