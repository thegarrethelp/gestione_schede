import pandas as pd
import requests

# ============================================================
# CONFIGURAZIONE BREVO
# ============================================================
BREVO_API_KEY = "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"
LISTA_NOME = "Scheda_Personalizzata"  # Nome della lista dove aggiungere i contatti

# ============================================================
# PERCORSI FILE (modifica se necessario)
# ============================================================
FILE_ABBONAMENTI = "Lista_Abbonamenti_Totale.csv"
FILE_BREVO = "Brevo.csv"

HEADERS = {
    "api-key": BREVO_API_KEY,
    "Content-Type": "application/json"
}


def get_list_id(list_name):
    """Trova l'ID della lista dal nome"""
    response = requests.get("https://api.brevo.com/v3/contacts/lists", headers=HEADERS)
    
    if response.status_code == 200:
        lists = response.json().get("lists", [])
        for lst in lists:
            if lst["name"].lower() == list_name.lower():
                return lst["id"]
        
        # Se non trovata, creala
        print(f"⚠️ Lista '{list_name}' non trovata. La creo...")
        return create_list(list_name)
    else:
        print(f"❌ Errore nel recupero liste: {response.json()}")
        return None


def create_list(list_name):
    """Crea una nuova lista in Brevo"""
    data = {
        "name": list_name,
        "folderId": 1  # Folder di default
    }
    response = requests.post("https://api.brevo.com/v3/contacts/lists", headers=HEADERS, json=data)
    
    if response.status_code == 201:
        list_id = response.json().get("id")
        print(f"✅ Lista '{list_name}' creata con ID: {list_id}")
        return list_id
    else:
        print(f"❌ Errore nella creazione lista: {response.json()}")
        return None


def is_contact_in_list(email, list_id):
    """Verifica se il contatto è già nella lista"""
    response = requests.get(
        f"https://api.brevo.com/v3/contacts/{email}",
        headers=HEADERS
    )
    
    if response.status_code == 200:
        contact_data = response.json()
        list_ids = contact_data.get("listIds", [])
        return list_id in list_ids
    
    return False


def add_contact_to_list(email, list_id, nome="", cognome=""):
    """Aggiunge un contatto alla lista (solo se non già presente)"""
    
    # Controlla se è già nella lista
    if is_contact_in_list(email, list_id):
        return False, "⏭️ Già presente nella lista, saltato"
    
    # Prima verifica se il contatto esiste, altrimenti lo crea
    data = {
        "email": email,
        "listIds": [list_id],
        "updateEnabled": True,
        "attributes": {
            "NOME": nome,
            "COGNOME": cognome
        }
    }
    
    response = requests.post("https://api.brevo.com/v3/contacts", headers=HEADERS, json=data)
    
    if response.status_code in [200, 201, 204]:
        return True, "✅ Aggiunto alla lista"
    elif response.status_code == 400 and "duplicate" in response.text.lower():
        # Contatto già esiste, aggiungilo alla lista
        add_data = {
            "emails": [email]
        }
        add_response = requests.post(
            f"https://api.brevo.com/v3/contacts/lists/{list_id}/contacts/add",
            headers=HEADERS,
            json=add_data
        )
        if add_response.status_code in [200, 201, 204]:
            return True, "✅ Già esistente, aggiunto alla lista"
        else:
            return False, add_response.json()
    else:
        return False, response.json()


def main():
    print("=" * 60)
    print("AGGIUNGI UTENTI 'SCHEDA_PERSONALIZZATA' ALLA LISTA BREVO")
    print("=" * 60)
    
    # Trova o crea la lista
    print(f"\n🔍 Cerco la lista '{LISTA_NOME}'...")
    list_id = get_list_id(LISTA_NOME)
    
    if not list_id:
        print("❌ Impossibile ottenere/creare la lista. Uscita.")
        return
    
    print(f"✅ Lista '{LISTA_NOME}' trovata (ID: {list_id})")
    
    # Leggi i file
    print("\n📂 Caricamento file...")
    abbonamenti = pd.read_csv(FILE_ABBONAMENTI, sep=';', encoding='utf-8-sig')
    brevo = pd.read_csv(FILE_BREVO, encoding='utf-8')
    
    # Filtra abbonamenti con "Scheda"
    scheda_filter = abbonamenti['TipologiaAbbonamento'].str.contains('Scheda', case=False, na=False)
    abbonamenti_scheda = abbonamenti[scheda_filter]
    
    print(f"\n👥 Trovati {len(abbonamenti_scheda)} utenti con abbonamento 'Scheda'\n")
    print("-" * 60)
    
    aggiunti = 0
    saltati = 0
    errori = 0
    
    for idx, row in abbonamenti_scheda.iterrows():
        nome = str(row['Nome']).strip() if pd.notna(row['Nome']) else ''
        cognome = str(row['Cognome']).strip() if pd.notna(row['Cognome']) else ''
        lezioni = row['NumLezResidue']
        
        print(f"\n👤 {nome} {cognome} - Lezioni residue: {lezioni}")
        
        # Cerca in Brevo CSV per ottenere l'email
        brevo_match = brevo[
            (brevo['Nome'].astype(str).str.strip().str.lower() == nome.lower()) & 
            (brevo['Cognome'].astype(str).str.strip().str.lower() == cognome.lower())
        ]
        
        if len(brevo_match) > 0:
            email = brevo_match.iloc[0]['Email']
            
            if pd.notna(email) and str(email).strip() and '@' in str(email):
                email = str(email).strip()
                print(f"   📧 Email: {email}")
                
                success, message = add_contact_to_list(email, list_id, nome, cognome)
                
                if success:
                    print(f"   {message}")
                    aggiunti += 1
                elif "saltato" in message.lower() or "già presente" in message.lower():
                    print(f"   {message}")
                    saltati += 1
                else:
                    print(f"   ❌ Errore: {message}")
                    errori += 1
            else:
                print(f"   ⚠️ Email non valida: {email}")
                errori += 1
        else:
            print(f"   ❌ Non trovato in Brevo")
            errori += 1
    
    print("\n" + "=" * 60)
    print(f"COMPLETATO - Aggiunti: {aggiunti} | Saltati: {saltati} | Errori: {errori}")
    print("=" * 60)
    print(f"\n💡 Ora vai su Brevo e configura il flow sulla lista '{LISTA_NOME}'!")


if __name__ == "__main__":
    main()
