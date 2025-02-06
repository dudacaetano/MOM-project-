import sys 
import os
import time
import json
import threading
import random

import paho.mqtt.client as mqtt

from tkinter import * 
from tkinter.scrolledtext import ScrolledText
#import tkinter.font as font 
from datetime import datetime


'''
endereco_broker = "test.mosquitto.org"
tipo_do_sensor = ''
unidade_do_sensor = ''
lista_topicos = []
'''

endereco_broker = "teste.mosquitto.org"

class Sensor:
    def __init__(self):
        self.lista_topicos = ""
        self.tipo_sensor = ""
        self.min_limit = 0
        self.max_limit = 0 
        self.running = False
        self.client = mqtt.Client()
        self.client.connect(endereco_broker)
        
    def setup(self):
        self.lista_topicos = input("Lista de Topicos:").strip()
        self.tipo_sensor = input("Tipo de Sensor(Temperatura, Pressao, Umidade ou Velocidade):").strip()
        self.min_limit = int(input("Minimo:").strip())
        self.max_limit = int(input("Maximo:").strip())
        
        sensor_setup = json.dumps({
            "lista_topicos": self.lista_topicos,
            "tipo_sensor": self.tipo_sensor,
            "min_limit": self.min_limit,
            "max_limit": self.max_limit
        })   
        self.client.publish("discovery/sensores", sensor_setup)
        
        self.ligar()
        
    def ligar(self):
        self.running = True
        self.client.publish(self.lista_topicos, f'[INFO][{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]:OFF')
        threading.Thread(target=self._valores_aleatorios, daemon=True).start()
        
    def desligar(self):
        print(f"\nSensor Encerrando {self.lista_topicos}...")
        self.client.publish(self.lista_topicos, f'[INFO][{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]:OFF')
        self.running = False
        self.client.disconnect()
        print("sensor encerrado com sucesso!")
        exit(0)
    
    def _valores_aleatorios(self):
        while self.running:
            valor = random.uniform(self.min_limit - 5, self.max_limit + 5)
            timestamp = datatime.now().strftime("%Y:%m %H:%M:%S")
            
            mensagem = f"[WARM][{timestamp}]:{valor:.2f}"
            if valor <= self.min_limit or valor >= self.max_limit:
                valor_str = f"\033[91m{valor:.2f}\033[0m"
                self.client.publish(self.lista_topicos, mensagem)
            else:
                valor_str = f"{valor: .2f}"
            
            print(f"[{self.lista_topicos}]: {valor_str}")
            
            time.sleep(1)
            
if __name__ == "__main__":
    sensor = Sensor()
    sensor.setup()
    
    try:
        while True: 
            time.sleep(1)
    except KeyboardInterrupt:
        sensor.desligar()