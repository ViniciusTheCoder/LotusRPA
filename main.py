from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# Configurações do WebDriver
chrome_options = Options()
#chrome_options.add_argument("--headless")  # Opcional: executa o navegador em segundo plano
service = Service(r'')  # Corrigido

driver = webdriver.Chrome(service=service, options=chrome_options)

def type_with_mask(input_element, text):
    """Simula a digitação de texto em um campo com máscara."""
    for char in text:
        input_element.send_keys(char)
        time.sleep(0.1)  # Atraso para simular a digitação
    
def main(sample):
    try:
        # Acesse a URL de login
        driver.get('https://app.lotusmais.com.br/login')

        # Preencha o formulário de login
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, 'email'))
        ).send_keys('')

        driver.find_element(By.ID, 'password').send_keys('Dinguinho123_')

        # Clique no botão de login
        login_button = driver.find_element(By.CLASS_NAME, 'btn.btn-primary')
        login_button.click()

        # Aguarde o campo de autenticação aparecer e solicite o código
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'vi'))
        )
        
        # Solicite o código de autenticação
        codigo = input("Digite o código de autenticação no terminal: ")

        # Preencha o campo de autenticação com o código fornecido
        auth_input = driver.find_element(By.CLASS_NAME, 'vi')
        auth_input.clear()
        auth_input.send_keys(codigo)

        # Verifique e marque a checkbox se não estiver marcada
        checkbox = driver.find_element(By.ID, 'flexCheckDefault')
        if not checkbox.is_selected():
            checkbox.click()

        # Verifique se o botão de confirmação está habilitado e visível
        try:
            confirm_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'btn.btn-primary.w-100.mt-2'))
            )
            # Remova a classe 'disabled' do botão para permitir o clique, se necessário
            driver.execute_script("arguments[0].classList.remove('disabled');", confirm_button)
            confirm_button.click()
        except Exception as e:
            print(f"Erro ao encontrar ou clicar no botão de confirmação. Erro: {e}")
            driver.quit()
            return

        # Aguarde redirecionamento para a página principal
        WebDriverWait(driver, 20).until(
            EC.url_to_be('https://app.lotusmais.com.br/dashboard')
        )

        # Continue com o fluxo original
        try:
            nova_proposta = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Nova Proposta')]"))
            )
            nova_proposta.click()
        except Exception as e:
            print(f"Erro ao encontrar ou clicar no elemento 'Nova Proposta'. Erro: {e}")
            driver.quit()
            return

        # Acesse a planilha pública
        url_planilha = 'C:\\Users\\admin\\Documents\\Projects\\automation\\planilha.xlsx'
        df = pd.read_excel(url_planilha, engine='openpyxl')

        # Verifique se há CPFs na planilha
        if df.empty or 'CPF' not in df.columns:
            print("A planilha não contém a coluna 'CPF'.")
            driver.quit()
            return

        # Certifique-se de que a coluna 'CPF' é tratada como string
        df['CPF'] = df['CPF'].astype(str)

        # Itera sobre os CPFs, limitado pelo parâmetro sample
        for index, row in df.head(sample).iterrows():
            cpf = row['CPF']
            print(f"Processando CPF: {cpf}")

            try:
                # Preencha o input com o CPF usando digitação simulada
                input_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'form-control.wizard__step__input'))
                )
                
                # Limpar o campo
                input_element.clear()

                # Simular a digitação do CPF
                type_with_mask(input_element, cpf)
                
                # Clique no botão para buscar
                busca_button = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'btn.btn-primary.d-flex.align-items-center.justify-content-center'))
                )

                # Adicione um atraso para garantir que o botão se torne clicável
                time.sleep(5)
                
                # Remover a classe 'disabled' do botão
                driver.execute_script("arguments[0].classList.remove('disabled');", busca_button)
                
                if busca_button.is_displayed() and busca_button.is_enabled():
                    busca_button.click()
                else:
                    print("O botão de busca ainda está desabilitado.")
                    continue

                # Aguarde 10 segundos para o site carregar
                time.sleep(10)

                # Verifique se a classe 'totalTransfer' existe
                try:
                    total_transfer_element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'totalTransfer'))
                    )
                    saldo = total_transfer_element.find_element(By.TAG_NAME, 'span').text

                    # Atualize a planilha com o saldo
                    df.at[index, 'Saldo'] = saldo
                    print(f"Saldo do CPF {cpf}: {saldo}")

                    # Clique no botão para seguir para o próximo CPF
                    next_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, 'btn.btn-outline-primary.d-flex.align-items-center.justify-content-center'))
                    )
                    next_button.click()

                except Exception as e:
                    print(f"Saldo não encontrado para CPF {cpf}. Erro: {e}")
                    # Clique no botão para seguir para o próximo CPF
                    next_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, 'btn.btn-outline-primary.d-flex.align-items-center.justify-content-center'))
                    )
                    next_button.click()
                
            except Exception as e:
                print(f"Erro ao processar CPF {cpf}. Erro: {e}")

        # Salve a planilha atualizada
        df.to_excel('planilha_atualizada.xlsx', index=False)

    finally:
        # Feche o navegador
        driver.quit()

if __name__ == "__main__":
    sample = 5  # Defina o número de CPFs a serem processados
    main(sample)
