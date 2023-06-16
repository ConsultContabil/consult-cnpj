from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/verificar', methods=['POST'])
def verificar_dispensa_licenciamento():
    cnpj = request.form['cnpj']
    data = consultar_cnpj(cnpj)

    if 'message' in data:
        return render_template('resultados.html', resultado='CNPJ inválido')

    nome_empresa = data['nome']
    cnaes = data['atividade_principal'] + data['atividades_secundarias']

    cnaes_encontrados = []

    cnaes_desejados = obter_cnaes_desejados()

    dispensa_licenciamento = True

    for cnae_data in cnaes:
        cnae = cnae_data['code']
        nome = cnae_data['text']

        cnaes_encontrados.append(f"{cnae} - {nome}")

        if cnae_data['code'] not in cnaes_desejados:
            dispensa_licenciamento = False
            break

    if dispensa_licenciamento:
        return render_template('resultados.html', resultado='A empresa pode ser dispensada de licenciamento', cnaes_encontrados=cnaes_encontrados, nome_empresa=nome_empresa)
    else:
        return render_template('resultados.html', resultado='A empresa não pode ser dispensada de licenciamento', nome_empresa=nome_empresa)

def consultar_cnpj(cnpj):
    url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj}"
    response = requests.get(url)
    if response.status_code == 200:
        try:
            data = response.json()
            return data
        except ValueError:
            return None
    else:
        return None

def obter_cnaes_desejados():
    url = 'https://tiago-consult.github.io/Tabela_Cnaes/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table')
    cnaes_desejados = set()
    if table:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                cnae = cells[0].text.strip()
                cnaes_desejados.add(cnae)
    return cnaes_desejados

if __name__ == '__main__':
    app.run(debug=True)
