import csv
import random
import time
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Importando classes dos sistemas originais
from SistemaEntrega import SistemaEntrega
from SistemaEntregaIA import SistemaEntregaIA

class ComparadorAlgoritmos:
    def __init__(self):
        self.sistema_a = SistemaEntrega()
        self.sistema_b = SistemaEntregaIA()
        self.resultados = []
        
    def carregar_dados(self, arquivo_conexoes, arquivo_entregas):
        """Carrega dados para ambos os sistemas."""
        self.sistema_a.ler_conexoes(arquivo_conexoes)
        self.sistema_a.ler_entregas(arquivo_entregas)
        
        self.sistema_b.ler_conexoes(arquivo_conexoes)
        self.sistema_b.ler_entregas(arquivo_entregas)
        
    def executar_comparacao(self, data_inicio, dias=10, capacidade_diaria=5):
        """Executa ambos os algoritmos por vários dias e compara resultados."""
        resultados = []
        
        data_atual = data_inicio
        for dia in range(1, dias + 1):
            print(f"\n===== Dia {dia} - {data_atual.strftime('%Y-%m-%d')} =====")
            
            # Medir tempo de execução do algoritmo A
            inicio_a = time.time()
            entregas_a = self.sistema_a.selecionar_entregas(data_atual, capacidade_diaria)
            lucro_a = self.sistema_a.exibir_programacao(entregas_a)
            tempo_exec_a = time.time() - inicio_a
            
            # Calcular tempo total das entregas para algoritmo A
            tempo_total_a = 0
            rotas_a = []
            for entrega in entregas_a:
                tempo = self.sistema_a.calcular_tempo_entrega(entrega['origem'], entrega['destino'])
                if tempo:
                    tempo_total_a += tempo
                    rotas_a.append(f"{entrega['origem']};{tempo}")
            
            # Medir tempo de execução do algoritmo B
            inicio_b = time.time()
            entregas_b = self.sistema_b.algoritmo_genetico(data_atual, capacidade_diaria=capacidade_diaria)
            lucro_b, tempo_total_b = self.sistema_b.exibir_programacao(entregas_b)
            tempo_exec_b = time.time() - inicio_b
            
            # Construir rotas para algoritmo B
            rotas_b = []
            for entrega in entregas_b:
                tempo = self.sistema_b.calcular_tempo_entrega(entrega['origem'], entrega['destino'])
                if tempo:
                    rotas_b.append(f"{entrega['origem']};{tempo}")
            
            # Formatação da saída no formato solicitado
            saida_a = f"({capacidade_diaria}, {', '.join(rotas_a)})"
            saida_b = f"({capacidade_diaria}, {', '.join(rotas_b)})"
            
            # Guardar resultados
            resultados.append({
                'dia': dia,
                'data': data_atual.strftime('%Y-%m-%d'),
                'lucro_a': lucro_a,
                'tempo_exec_a': tempo_exec_a,
                'tempo_entrega_a': tempo_total_a,
                'entregas_a': len(entregas_a),
                'rotas_a': saida_a,
                'lucro_b': lucro_b,
                'tempo_exec_b': tempo_exec_b,
                'tempo_entrega_b': tempo_total_b,
                'entregas_b': len(entregas_b),
                'rotas_b': saida_b
            })
            
            # Avançar para o próximo dia
            data_atual += timedelta(days=1)
        
        self.resultados = resultados
        return resultados
    
    def gerar_graficos_comparativos(self):
        """Gera gráficos comparativos entre os algoritmos."""
        if not self.resultados:
            print("Execute a comparação primeiro")
            return
        
        df = pd.DataFrame(self.resultados)
        
        # Configuração dos gráficos
        plt.figure(figsize=(15, 12))
        
        # Gráfico de lucro
        plt.subplot(2, 2, 1)
        plt.plot(df['dia'], df['lucro_a'], 'b-', label='SistemaEntrega')
        plt.plot(df['dia'], df['lucro_b'], 'r-', label='SistemaEntregaIA')
        plt.xlabel('Dia')
        plt.ylabel('Lucro (R$)')
        plt.title('Comparação de Lucro por Algoritmo')
        plt.legend()
        plt.grid(True)
        
        # Gráfico de tempo de execução
        plt.subplot(2, 2, 2)
        plt.plot(df['dia'], df['tempo_exec_a'], 'b-', label='SistemaEntrega')
        plt.plot(df['dia'], df['tempo_exec_b'], 'r-', label='SistemaEntregaIA')
        plt.xlabel('Dia')
        plt.ylabel('Tempo de Execução (s)')
        plt.title('Comparação de Tempo de Processamento')
        plt.legend()
        plt.grid(True)
        
        # Gráfico de tempo total de entrega
        plt.subplot(2, 2, 3)
        plt.plot(df['dia'], df['tempo_entrega_a'], 'b-', label='SistemaEntrega')
        plt.plot(df['dia'], df['tempo_entrega_b'], 'r-', label='SistemaEntregaIA')
        plt.xlabel('Dia')
        plt.ylabel('Tempo Total de Entrega (min)')
        plt.title('Comparação de Tempo Total de Entrega')
        plt.legend()
        plt.grid(True)
        
        # Gráfico de eficiência (lucro/tempo)
        plt.subplot(2, 2, 4)
        eficiencia_a = df['lucro_a'] / df['tempo_entrega_a']
        eficiencia_b = df['lucro_b'] / df['tempo_entrega_b']
        plt.plot(df['dia'], eficiencia_a, 'b-', label='SistemaEntrega')
        plt.plot(df['dia'], eficiencia_b, 'r-', label='SistemaEntregaIA')
        plt.xlabel('Dia')
        plt.ylabel('Eficiência (R$/min)')
        plt.title('Comparação de Eficiência (Lucro/Tempo)')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig('comparacao_algoritmos.png')
        plt.show()
        
        # Tabela comparativa
        melhoria_lucro = ((df['lucro_b'].sum() / df['lucro_a'].sum()) - 1) * 100
        melhoria_tempo = ((df['tempo_entrega_a'].sum() / df['tempo_entrega_b'].sum()) - 1) * 100
        
        print("\n===== RESUMO COMPARATIVO =====")
        print(f"Lucro total SistemaEntrega: R$ {df['lucro_a'].sum():.2f}")
        print(f"Lucro total SistemaEntregaIA: R$ {df['lucro_b'].sum():.2f}")
        print(f"Melhoria no lucro: {melhoria_lucro:.2f}%")
        print(f"Tempo médio de execução SistemaEntrega: {df['tempo_exec_a'].mean():.4f} s")
        print(f"Tempo médio de execução SistemaEntregaIA: {df['tempo_exec_b'].mean():.4f} s")
        print(f"Tempo total de entrega SistemaEntrega: {df['tempo_entrega_a'].sum()} min")
        print(f"Tempo total de entrega SistemaEntregaIA: {df['tempo_entrega_b'].sum()} min")
        print(f"Redução no tempo de entrega: {melhoria_tempo:.2f}%")
        print("===============================")
        
        # Exibir formato de saída solicitado
        print("\n===== EXEMPLO DE SAÍDA =====")
        print("SistemaEntrega:")
        print(df['rotas_a'].iloc[0])
        print("\nSistemaEntregaIA:")
        print(df['rotas_b'].iloc[0])
        print("===========================")
        
        return df

class SimuladorLeilao(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Simulador de Leilão de Entregas")
        self.geometry("1200x800")
        
        self.sistema_a = SistemaEntrega()
        self.sistema_b = SistemaEntregaIA()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface gráfica."""
        # Frame para controles
        frm_controles = ttk.Frame(self)
        frm_controles.pack(pady=10, fill=tk.X)
        
        # Parâmetros de simulação
        ttk.Label(frm_controles, text="Data Inicial:").grid(row=0, column=0, padx=5, pady=5)
        self.data_var = tk.StringVar(value="2023-11-15")
        ttk.Entry(frm_controles, textvariable=self.data_var, width=12).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frm_controles, text="Capacidade Diária:").grid(row=0, column=2, padx=5, pady=5)
        self.capacidade_var = tk.IntVar(value=5)
        ttk.Spinbox(frm_controles, from_=1, to=20, textvariable=self.capacidade_var, width=5).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(frm_controles, text="Dias:").grid(row=0, column=4, padx=5, pady=5)
        self.dias_var = tk.IntVar(value=10)
        ttk.Spinbox(frm_controles, from_=1, to=30, textvariable=self.dias_var, width=5).grid(row=0, column=5, padx=5, pady=5)
        
        # Parâmetros do algoritmo genético
        ttk.Label(frm_controles, text="Tamanho População:").grid(row=1, column=0, padx=5, pady=5)
        self.populacao_var = tk.IntVar(value=50)
        ttk.Spinbox(frm_controles, from_=10, to=200, textvariable=self.populacao_var, width=5).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frm_controles, text="Gerações:").grid(row=1, column=2, padx=5, pady=5)
        self.geracoes_var = tk.IntVar(value=100)
        ttk.Spinbox(frm_controles, from_=10, to=500, textvariable=self.geracoes_var, width=5).grid(row=1, column=3, padx=5, pady=5)
        
        # Botões
        ttk.Button(frm_controles, text="Carregar Dados", command=self.carregar_dados).grid(row=1, column=4, padx=5, pady=5)
        ttk.Button(frm_controles, text="Executar Simulação", command=self.executar_simulacao).grid(row=1, column=5, padx=5, pady=5)
        
        # Frame para gráficos
        self.frm_graficos = ttk.Frame(self)
        self.frm_graficos.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Frame para resultados
        self.frm_resultados = ttk.Frame(self)
        self.frm_resultados.pack(fill=tk.X, padx=10, pady=10)
        
        # Frame para exibir formato de saída
        self.frm_saida = ttk.LabelFrame(self, text="Formato de Saída")
        self.frm_saida.pack(fill=tk.X, padx=10, pady=10)
        
        self.saida_a_var = tk.StringVar()
        self.saida_b_var = tk.StringVar()
        
        ttk.Label(self.frm_saida, text="SistemaEntrega:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(self.frm_saida, textvariable=self.saida_a_var, width=60, state="readonly").grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.frm_saida, text="SistemaEntregaIA:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(self.frm_saida, textvariable=self.saida_b_var, width=60, state="readonly").grid(row=1, column=1, padx=5, pady=5)
        
        # Label para status
        self.status_var = tk.StringVar(value="Pronto para iniciar. Carregue os dados e execute a simulação.")
        ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W).pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)
    
    def carregar_dados(self):
        """Carrega dados de conexões e entregas."""
        self.status_var.set("Carregando dados...")
        try:
            self.sistema_a.ler_conexoes("conexoes.csv")
            self.sistema_a.ler_entregas("entregas.csv")
            
            self.sistema_b.ler_conexoes("conexoes.csv")
            self.sistema_b.ler_entregas("entregas.csv")
            
            self.status_var.set(f"Dados carregados: {len(self.sistema_a.conexoes)} conexões e {len(self.sistema_a.entregas)} entregas.")
        except Exception as e:
            self.status_var.set(f"Erro ao carregar dados: {e}")
    
    def executar_simulacao(self):
        """Executa a simulação e exibe os resultados."""
        # Limpar gráficos anteriores
        for widget in self.frm_graficos.winfo_children():
            widget.destroy()
        for widget in self.frm_resultados.winfo_children():
            widget.destroy()
        
        try:
            data_inicial = datetime.strptime(self.data_var.get(), '%Y-%m-%d')
            capacidade = self.capacidade_var.get()
            dias = self.dias_var.get()
            
            # Modificar parâmetros do algoritmo genético
            tamanho_populacao = self.populacao_var.get()
            geracoes = self.geracoes_var.get()
            
            self.status_var.set("Executando simulação...")
            
            # Resultados da simulação
            resultados = []
            
            data_atual = data_inicial
            for dia in range(1, dias + 1):
                # Algoritmo A - SistemaEntrega
                inicio_a = time.time()
                entregas_a = self.sistema_a.selecionar_entregas(data_atual, capacidade)
                lucro_a = sum([e['valor'] + e['bonus'] for e in entregas_a])
                tempo_exec_a = time.time() - inicio_a
                
                tempo_total_a = 0
                rotas_a = []
                for entrega in entregas_a:
                    tempo = self.sistema_a.calcular_tempo_entrega(entrega['origem'], entrega['destino'])
                    if tempo:
                        tempo_total_a += tempo
                        rotas_a.append(f"{entrega['origem']};{tempo}")
                
                # Algoritmo B - SistemaEntregaIA
                inicio_b = time.time()
                entregas_b = self.sistema_b.algoritmo_genetico(data_atual, tamanho_populacao, geracoes, capacidade)
                tempo_exec_b = time.time() - inicio_b
                
                lucro_b = sum([e['valor'] + e['bonus'] for e in entregas_b])
                tempo_total_b = 0
                rotas_b = []
                for entrega in entregas_b:
                    tempo = self.sistema_b.calcular_tempo_entrega(entrega['origem'], entrega['destino'])
                    if tempo:
                        tempo_total_b += tempo
                        rotas_b.append(f"{entrega['origem']};{tempo}")
                
                # Formatação da saída no formato solicitado
                saida_a = f"({capacidade}, {', '.join(rotas_a)})"
                saida_b = f"({capacidade}, {', '.join(rotas_b)})"
                
                # Atualizar os campos de saída na interface na primeira iteração
                if dia == 1:
                    self.saida_a_var.set(saida_a)
                    self.saida_b_var.set(saida_b)
                
                # Guardar resultados
                resultados.append({
                    'dia': dia,
                    'data': data_atual.strftime('%Y-%m-%d'),
                    'lucro_a': lucro_a,
                    'tempo_exec_a': tempo_exec_a,
                    'tempo_entrega_a': tempo_total_a,
                    'entregas_a': len(entregas_a),
                    'rotas_a': saida_a,
                    'lucro_b': lucro_b,
                    'tempo_exec_b': tempo_exec_b,
                    'tempo_entrega_b': tempo_total_b,
                    'entregas_b': len(entregas_b),
                    'rotas_b': saida_b
                })
                
                # Avançar para o próximo dia
                data_atual += timedelta(days=1)
            
            # Criar DataFrame
            df = pd.DataFrame(resultados)
            
            # Criar figura para os gráficos
            fig = plt.Figure(figsize=(12, 8), dpi=100)
            
            # Gráfico de lucro
            ax1 = fig.add_subplot(221)
            ax1.plot(df['dia'], df['lucro_a'], 'b-', label='SistemaEntrega')
            ax1.plot(df['dia'], df['lucro_b'], 'r-', label='SistemaEntregaIA')
            ax1.set_xlabel('Dia')
            ax1.set_ylabel('Lucro (R$)')
            ax1.set_title('Comparação de Lucro por Algoritmo')
            ax1.legend()
            ax1.grid(True)
            
            # Gráfico de tempo de execução
            ax2 = fig.add_subplot(222)
            ax2.plot(df['dia'], df['tempo_exec_a'], 'b-', label='SistemaEntrega')
            ax2.plot(df['dia'], df['tempo_exec_b'], 'r-', label='SistemaEntregaIA')
            ax2.set_xlabel('Dia')
            ax2.set_ylabel('Tempo de Execução (s)')
            ax2.set_title('Comparação de Tempo de Processamento')
            ax2.legend()
            ax2.grid(True)
            
            # Gráfico de tempo total de entrega
            ax3 = fig.add_subplot(223)
            ax3.plot(df['dia'], df['tempo_entrega_a'], 'b-', label='SistemaEntrega')
            ax3.plot(df['dia'], df['tempo_entrega_b'], 'r-', label='SistemaEntregaIA')
            ax3.set_xlabel('Dia')
            ax3.set_ylabel('Tempo Total de Entrega (min)')
            ax3.set_title('Comparação de Tempo Total de Entrega')
            ax3.legend()
            ax3.grid(True)
            
            # Gráfico de eficiência (lucro/tempo)
            ax4 = fig.add_subplot(224)
            eficiencia_a = df['lucro_a'] / df['tempo_entrega_a']
            eficiencia_b = df['lucro_b'] / df['tempo_entrega_b']
            ax4.plot(df['dia'], eficiencia_a, 'b-', label='SistemaEntrega')
            ax4.plot(df['dia'], eficiencia_b, 'r-', label='SistemaEntregaIA')
            ax4.set_xlabel('Dia')
            ax4.set_ylabel('Eficiência (R$/min)')
            ax4.set_title('Comparação de Eficiência (Lucro/Tempo)')
            ax4.legend()
            ax4.grid(True)
            
            fig.tight_layout()
            
            # Inserir gráficos na interface
            canvas = FigureCanvasTkAgg(fig, self.frm_graficos)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Calcular estatísticas
            melhoria_lucro = ((df['lucro_b'].sum() / df['lucro_a'].sum()) - 1) * 100
            melhoria_tempo = ((df['tempo_entrega_a'].sum() / df['tempo_entrega_b'].sum()) - 1) * 100
            
            # Exibir resultados em tabela
            style = ttk.Style()
            style.configure("Treeview", rowheight=25)
            
            tree = ttk.Treeview(self.frm_resultados, columns=("algoritmo", "lucro", "tempo_exec", "tempo_entrega", "eficiencia", "bonus"))
            tree.heading("#0", text="")
            tree.heading("algoritmo", text="Algoritmo")
            tree.heading("lucro", text="Lucro Total (R$)")
            tree.heading("tempo_exec", text="Tempo Médio de Execução (s)")
            tree.heading("tempo_entrega", text="Tempo Total de Entrega (min)")
            tree.heading("eficiencia", text="Eficiência Média (R$/min)")
            tree.heading("bonus", text="Bônus Médio por Entrega (R$)")
            
            tree.column("#0", width=0, stretch=tk.NO)
            tree.column("algoritmo", width=150)
            tree.column("lucro", width=120)
            tree.column("tempo_exec", width=180)
            tree.column("tempo_entrega", width=180)
            tree.column("eficiencia", width=150)
            tree.column("bonus", width=150)
            
            # Calcular bônus médio para cada algoritmo
            bonus_a = []
            bonus_b = []
            for i in range(len(entregas_a)):
                bonus_a.append(entregas_a[i]['bonus'])
            for i in range(len(entregas_b)):
                bonus_b.append(entregas_b[i]['bonus'])
            
            bonus_medio_a = sum(bonus_a) / len(bonus_a) if bonus_a else 0
            bonus_medio_b = sum(bonus_b) / len(bonus_b) if bonus_b else 0
            
            tree.insert("", tk.END, text="1", values=("SistemaEntrega", 
                                                        f"{df['lucro_a'].sum():.2f}", 
                                                        f"{df['tempo_exec_a'].mean():.4f}",
                                                        f"{df['tempo_entrega_a'].sum()}",
                                                        f"{eficiencia_a.mean():.2f}",
                                                        f"{bonus_medio_a:.2f}"))
            
            tree.insert("", tk.END, text="2", values=("SistemaEntregaIA", 
                                                        f"{df['lucro_b'].sum():.2f}", 
                                                        f"{df['tempo_exec_b'].mean():.4f}",
                                                        f"{df['tempo_entrega_b'].sum()}",
                                                        f"{eficiencia_b.mean():.2f}",
                                                        f"{bonus_medio_b:.2f}"))
            
            tree.insert("", tk.END, text="3", values=("Diferença (%)", 
                                                        f"{melhoria_lucro:.2f}%", 
                                                        "---",
                                                        f"{melhoria_tempo:.2f}%",
                                                        f"{(eficiencia_b.mean()/eficiencia_a.mean() - 1) * 100:.2f}%",
                                                        f"{(bonus_medio_b/bonus_medio_a - 1) * 100:.2f}%"))
            
            tree.pack(fill=tk.X, expand=True)
            
            self.status_var.set(f"Simulação concluída. Mostrando resultados para {dias} dias.")
            
        except Exception as e:
            self.status_var.set(f"Erro na simulação: {e}")

# Função para gerar dados de exemplo para testes
def gerar_dados_exemplo():
    """Gera arquivos CSV de exemplo para teste."""
    # Gerar conexões
    cidades = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    
    conexoes = []
    for origem in cidades:
        for destino in cidades:
            if origem != destino:
                tempo = random.randint(30, 180)  # Entre 30 minutos e 3 horas
                conexoes.append({'origem': origem, 'destino': destino, 'tempo': tempo})
    
    with open('conexoes.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['origem', 'destino', 'tempo'])
        writer.writeheader()
        writer.writerows(conexoes)
    
    # Gerar entregas
    entregas = []
    for i in range(1, 101):  # 100 entregas disponíveis
        origem = random.choice(cidades)
        destino = random.choice([c for c in cidades if c != origem])
        
        # Data aleatória nos próximos 14 dias
        dias_entrega = random.randint(0, 14)
        data_prazo = (datetime.now() + timedelta(days=dias_entrega)).strftime('%Y-%m-%d')
        
        valor = random.uniform(50, 300)  # Valor entre 50 e 300
        bonus = random.uniform(10, 100)  # Bônus entre 10 e 100
        
        entregas.append({
            'id': f"E{i:03d}",
            'origem': origem,
            'destino': destino,
            'prazo': data_prazo,
            'valor': round(valor, 2),
            'bonus': round(bonus, 2)
        })
    
    with open('entregas.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['id', 'origem', 'destino', 'prazo', 'valor', 'bonus'])
        writer.writeheader()
        writer.writerows(entregas)
    
    print(f"Dados de exemplo gerados: {len(conexoes)} conexões e {len(entregas)} entregas.")
    
    # Mostrar exemplo de saída no formato solicitado
    exemplo_rota = f"({5}, C;10)"
    print(f"\nExemplo de saída no formato solicitado: {exemplo_rota}")

# Executar a aplicação
if __name__ == "__main__":
    # Verificar se os arquivos existem, caso contrário gerar dados de exemplo
    import os
    if not os.path.exists('conexoes.csv') or not os.path.exists('entregas.csv'):
        print("Arquivos de dados não encontrados. Gerando dados de exemplo...")
        gerar_dados_exemplo()
    
    # Iniciar a aplicação
    app = SimuladorLeilao()
    app.mainloop()