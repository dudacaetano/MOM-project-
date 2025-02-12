# MOM-project-
<h1 align="center">
   <br>Middleware Orientado a Mensagens
</h1>


## 📚 Resumo
> Este projeto implementa um sistema distribuído baseado em Middleware Orientado a Mensagens (MOM) para monitoramento de sensores. Ele utiliza um broker de mensagens MQTT para facilitar a comunicação entre sensores distribuídos e um aplicativo cliente que recebe e processa os dados em tempo real.

## Clone Repositório:
```bash
git clone https://github.com/dudacaetano/MOM-project-.git
cd MOM-project-
```

## Config ambiente virtual
```bash
python -m venv .venv
source .venv/bin/activate
```

## Instalando Dependencias

```bash
pip install -r requirements.txt
```

## Iniciando Gerenciador de Equipamentos

```bash
python client.py
```

## Iniciando Sensor:

```bash
python sensor.py
```
