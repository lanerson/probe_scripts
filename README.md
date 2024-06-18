# Probe Script

## Script criado para coletar informações de diferentes hardwares
- Baixe o arquivo probe.py
- Tenha em mãos o arquivo service_account.json
- Certifique-se de manter os dois arquivos no mesmo diretório

## Passo a passo

Baixar gspread
```bash
$ pip install gspread
```

Executar probe.py
``` bash
$ python3 probe.py
```

Os dados são então jogados em uma [Planilha](https://docs.google.com/spreadsheets/d/1mFA4W2FpUhi_gUcvUZfNNyV_VQqcjz8Yv-W_-9PWos0/edit?gid=909281549#gid=909281549) do GoogleSheets
