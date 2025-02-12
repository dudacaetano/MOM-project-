import sys 
import time
import json
import threading
import random

import paho.mqtt.client as mqtt
from tkinter import *
from tkinter import ttk
from datetime import datetime

BROKER = "test.mosquitto.org"

class SensorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciar Sensores")
        self.root.geometry("400x400")
        
        self.sensores = {}  # Dicionário para armazenar sensores
        self.client = mqtt.Client()
        
        try:
            self.client.connect(BROKER)
            self.client.loop_start()  # Inicia o loop do cliente
        except Exception as e:
            print(f"Erro ao conectar ao broker: {e}")
            sys.exit(1)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame para entrada de dados
        frame = Frame(self.root, padx=10, pady=10)
        frame.pack(fill="both", expand=True)
        
        Label(frame, text="Lista de Tópicos:").grid(row=0, column=0, sticky="w")
        self.entry_topico = Entry(frame, width=30)
        self.entry_topico.grid(row=0, column=1, pady=5)
        
        Label(frame, text="Tipo de Sensor:").grid(row=1, column=0, sticky="w")
        self.combo_tipo = ttk.Combobox(frame, values=["Temperatura", "Pressao", "Umidade", "Velocidade"], state="readonly")
        self.combo_tipo.grid(row=1, column=1, pady=5)
        
        Label(frame, text="Limite Mínimo:").grid(row=2, column=0, sticky="w")
        self.entry_min = Entry(frame, width=10)
        self.entry_min.grid(row=2, column=1, pady=5)
        
        Label(frame, text="Limite Máximo:").grid(row=3, column=0, sticky="w")
        self.entry_max = Entry(frame, width=10)
        self.entry_max.grid(row=3, column=1, pady=5)
        
        self.btn_criar = Button(frame, text="Criar Sensor", command=self.criar_sensor)
        self.btn_criar.grid(row=4, columnspan=2, pady=10)
        
        Label(frame, text="Selecionar Sensor:").grid(row=5, column=0, sticky="w")
        self.combo_sensores = ttk.Combobox(frame, values=[], state="readonly")
        self.combo_sensores.grid(row=5, column=1, pady=5)
        
        self.btn_ligar = Button(frame, text="Ligar Sensor", command=self.ligar_sensor)
        self.btn_ligar.grid(row=6, columnspan=2, pady=5)
        
        self.btn_desligar = Button(frame, text="Desligar Sensor", command=self.desligar_sensor)
        self.btn_desligar.grid(row=7, columnspan=2, pady=5)

    def criar_sensor(self):
        lista_topicos = self.entry_topico.get().strip()
        tipo_sensor = self.combo_tipo.get()
        min_limit = int(self.entry_min.get().strip())
        max_limit = int(self.entry_max.get().strip())
        
        sensor_id = f"{tipo_sensor}_{lista_topicos}"  # Identificador único para o sensor
        self.sensores[sensor_id] = {
            "topico": lista_topicos,
            "tipo_sensor": tipo_sensor,
            "min_limit": min_limit,
            "max_limit": max_limit,
            "running": False
        }
        
        sensor_setup = json.dumps({
            "lista_topicos": lista_topicos,
            "tipo_sensor": tipo_sensor,
            "min_limit": min_limit,
            "max_limit": max_limit
        })   
        self.client.publish("discovery/sensores", sensor_setup)
        
        self.atualizar_combo_sensores()

    def atualizar_combo_sensores(self):
        self.combo_sensores["values"] = list(self.sensores.keys())  # Atualiza a lista de sensores

    def ligar_sensor(self):
        sensor_id = self.combo_sensores.get()
        if sensor_id in self.sensores:
            sensor = self.sensores[sensor_id]
            if not sensor["running"]:
                sensor["running"] = True
                self.client.publish(sensor["topico"], f'[INFO][{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]: ON')
                threading.Thread(target=self._valores_aleatorios, args=(sensor_id,), daemon=True).start()
                print(f"Sensor {sensor_id} ligado.")

    def desligar_sensor(self):
        sensor_id = self.combo_sensores.get()
        if sensor_id in self.sensores:
            sensor = self.sensores[sensor_id]
            if sensor["running"]:
                sensor["running"] = False
                self.client.publish(sensor["topico"], f'[INFO][{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]: OFF')
                print(f"Sensor {sensor_id} desligado.")

    def _valores_aleatorios(self, sensor_id):
        sensor = self.sensores[sensor_id]
        while sensor["running"]:
            valor = random.uniform(sensor["min_limit"] - 5, sensor["max_limit"] + 5)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            mensagem = f"[WARN][{timestamp}]: {valor:.2f}"
            if valor <= sensor["min_limit"] or valor >= sensor["max_limit"]:
                valor_str = f"\033[91m{valor:.2f}\033[0m"  # Vermelho para valores fora do limite
                self.client.publish(sensor["topico"], mensagem)
            else:
                valor_str = f"{valor:.2f}"
            
            print(f"[{sensor['topico']}]: {valor_str}")
            time.sleep(1)

if __name__ == "__main__":
    root = Tk()
    app = SensorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.desligar_sensor)  # Para desligar o sensor ao fechar a janela
    root.mainloop()