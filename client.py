import sys 
import time
import json
import threading
import random

import paho.mqtt.client as mqtt
from tkinter import ttk
import tkinter as tk
from datetime import datetime

BROKER = "test.mosquitto.org"

class GerenciadorEquipametos:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Equipamentos")
        self.root.geometry("600x400")
        self.root.resizable(False, True)
        
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.connect(BROKER)
        
        self.sensores_livres = {}
        self.sensores_inscritos = {}
        
        self.setup_ui()
        threading.Thread(target=self.monitorar, daemon=True).start()
        
    def setup_ui(self):
        frame_top = tk.Frame(self.root, padx=10, pady=10)
        frame_top.pack(fill="x")
        
        tk.Label(frame_top, text="Sensores Livres>>", font=("Arial", 10, "bold")).pack(anchor="w")
        
        self.combobox_sensores = ttk.Combobox(frame_top, state="readonly", width=40)
        self.combobox_sensores.pack(pady=5, anchor="w")
        
        self.bnt_adicionar = tk.Button(frame_top, text="Escutar Sensor", command=self.adicionar_sensor)
        self.bnt_adicionar.pack(pady=5, anchor="w")
        
        self.frame_sensores = tk.Frame(self.root, padx=10, pady=5)
        self.frame_sensores.pack(fill="both", expand=True)
        
        self.client.subscribe("discovery/sensores")
        
    def adicionar_sensor(self):
        lista_topicos = self.combobox_sensores.get()
        if lista_topicos and lista_topicos not in self.sensores_inscritos:
            info = self.sensores_livres[lista_topicos]
            self.sensores_inscritos[lista_topicos] = self.criar_frame_sensor(info)
            self.client.subscribe(lista_topicos)
    
    def criar_frame_sensor(self, info):
        frame_sensor = tk.Frame(self.frame_sensores, pady=5, padx=5, relief="groove", borderwidth=2)
        frame_sensor.pack(fill="x", pady=5, padx=5, anchor="w")
        
        sufix = self.obter_sufixo(info['tipo_sensor'])
        
        label = tk.Text(frame_sensor, font=("Arial", 10, "bold"), height=1, wrap="word")
        label.pack(anchor="w")
        
        label.insert(tk.END, f"Sensor | Tópico: {info['lista_topicos']} | Min: {info['min_limit']}{sufix} Max: {info['max_limit']}{sufix} ({info['tipo_sensor']})")
        
        texto_saida = tk.Text(frame_sensor, height=5, width=50, wrap="word")
        texto_saida.pack(fill="both", expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(frame_sensor, command=texto_saida.yview)
        scrollbar.pack(side="right", fill="y")
        texto_saida.config(yscrollcommand=scrollbar.set)
        texto_saida.tag_config("alert", foreground="red")
        texto_saida.tag_config("INFO", foreground="black")
        
        return texto_saida
    
    def obter_sufixo(self, tipo):
        sufixos = {
            "Temperatura": "°C",
            "Pressao": "bar",
            "Umidade": "% UR",
            "Velocidade": "m/s"
        }
        return sufixos.get(tipo, "")
    
    def on_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode()
            lista_topicos = msg.topic
            
            if lista_topicos == "discovery/sensores":
                sensor_info = json.loads(payload)
                sensor_lista_topicos = sensor_info["lista_topicos"]
                
                if sensor_lista_topicos not in self.sensores_livres:
                    self.sensores_livres[sensor_lista_topicos] = sensor_info
                    self.combobox_sensores["values"] = list(self.sensores_livres.keys())
            
            elif lista_topicos in self.sensores_inscritos:
                self.log_mensagem(lista_topicos, payload)
        except Exception as e:
            print(f"Erro: {str(e)}")
            
    def log_mensagem(self, lista_topicos, mensagem):
        info = self.sensores_livres.get(lista_topicos, {})
        
        # Verifica se a mensagem contém um alerta
        if "[WARN]" in mensagem:
            tag = "alert"
        else:
            tag = "INFO"
        
        if lista_topicos in self.sensores_inscritos:
            caixa_mensagem = self.sensores_inscritos[lista_topicos]
            caixa_mensagem.insert(tk.END, mensagem + "\n", tag)
            caixa_mensagem.see(tk.END)
    
    def monitorar(self):
        self.client.loop_start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.client.loop_stop()

if __name__ == "__main__":
    root = tk.Tk()
    app = GerenciadorEquipametos(root)
    root.mainloop()