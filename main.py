from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


chrome_options = Options()
chrome_options.add_argument("--headless")  
service = Service(r'')  
def setup_driver():
    return webdriver.Chrome(service=service, options=chrome_options)

def type_with_mask(input_element, text):
    for char in text:
        input_element.send_keys(char)
        time.sleep(0.1)
    
   
    if input_element.get_attribute('value') != text:
        input_element.clear()
        input_element.send_keys(text)

def login(driver, email, password):
    driver.get('https://app.lotusmais.com.br/login')
    
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'email'))).send_keys('your email')
    driver.find_element(By.ID, 'password').send_keys('your password')
    
    login_button = driver.find_element(By.CLASS_NAME, 'btn.btn-primary')
    login_button.click()
    
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'vi')))
    
    codigo = input("Digite o código de autenticação no terminal: ")
    
    auth_input = driver.find_element(By.CLASS_NAME, 'vi')
    auth_input.clear()
    auth_input.send_keys(codigo)
    
    checkbox = driver.find_element(By.ID, 'flexCheckDefault')
    if not checkbox.is_selected():
        checkbox.click()
    
    try:
        confirm_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'btn.btn-primary.w-100.mt-2'))
        )
        driver.execute_script("arguments[0].classList.remove('disabled');", confirm_button)
        confirm_button.click()
    except Exception as e:
        logging.error(f"Erro ao confirmar login: {e}")
        raise

    WebDriverWait(driver, 5).until(EC.url_to_be('https://app.lotusmais.com.br/dashboard'))

def navigate_to_new_proposal(driver):
    try:
        nova_proposta = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Nova Proposta')]"))
        )
        nova_proposta.click()
    except Exception as e:
        logging.error(f"Erro ao navegar para Nova Proposta: {e}")
        raise

def process_cpf(driver, cpf, index, total):
    try:
        input_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'form-control.wizard__step__input'))
        )
        input_element.clear()
        type_with_mask(input_element, cpf)
        
        busca_button = WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'btn.btn-primary.d-flex.align-items-center.justify-content-center'))
        )
        time.sleep(1)
        driver.execute_script("arguments[0].classList.remove('disabled');", busca_button)
        
        if busca_button.is_displayed() and busca_button.is_enabled():
            busca_button.click()
        else:
            logging.warning("O botão de busca está desabilitado.")
            return None

        time.sleep(1)

        saldo = "0"
        found_total_transfer = False
        try:
            total_transfer_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'totalTransfer'))
            )
            saldo = total_transfer_element.find_element(By.TAG_NAME, 'h3').text
            found_total_transfer = True
        except (TimeoutException, NoSuchElementException):
            logging.info(f"Saldo não encontrado para CPF {cpf}. Definindo como 0.")

        if found_total_transfer:
            
            try:
                
                dashboard_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Dashboard')]"))
                )
                dashboard_button.click()
                logging.info("Clicou em 'Dashboard'")

                
                time.sleep(2)

                
                nova_proposta = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Nova Proposta')]"))
                )
                nova_proposta.click()
                logging.info("Clicou em 'Nova Proposta'")

            except Exception as e:
                logging.error(f"Erro ao navegar para Nova Proposta após encontrar saldo: {e}")
        else:
            
            try:
                back_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.btn.btn-outline-primary.d-flex.align-items-center.justify-content-center'))
                )
                driver.execute_script("arguments[0].click();", back_button)
                logging.info("Clicou no botão 'Voltar'")
            except Exception as e:
                logging.error(f"Erro ao clicar no botão 'Voltar': {e}")

       
        logging.info(f"Processados {index + 1} de {total} CPFs.")

        return saldo

    except Exception as e:
        logging.error(f"Erro ao processar CPF {cpf}: {e}")
        return None

def main(sample):
    driver = setup_driver()
    try:
        login(driver, 'seu_email@exemplo.com', 'sua_senha')
        navigate_to_new_proposal(driver)

        df = pd.read_excel('\\planilha.xlsx', engine='openpyxl')
        
        if df.empty or 'CPF' not in df.columns:
            logging.error("A planilha não contém a coluna 'CPF'.")
            return

        df['CPF'] = df['CPF'].astype(str)
        df['Saldo'] = ""  

        total_cpfs = len(df.head(sample)) 

        for index, row in df.head(sample).iterrows():
            cpf = row['CPF']
            logging.info(f"Processando CPF: {cpf}")
            
            saldo = process_cpf(driver, cpf, index, total_cpfs)
            if saldo is not None:
                df.at[index, 'Saldo'] = saldo
                logging.info(f"Saldo do CPF {cpf}: {saldo}")
            else:
                df.at[index, 'Saldo'] = "0"
                logging.warning(f"Definindo saldo como 0 para CPF {cpf} devido a erro no processamento.")

        df.to_excel('planilha_atualizada.xlsx', index=False)
        logging.info("Processamento concluído. Planilha atualizada salva.")

    except Exception as e:
        logging.error(f"Erro durante a execução: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    sample = 11911
    main(sample)
