import csv
from datetime import datetime

class SistemaEntrega:
    def __init__(self):
        self.conexoes = []
        self.entregas = []
    
    def ler_conexoes(self, arquivo):
        """Lê as conexões (rotas) de um arquivo CSV."""
        try:
            with open(arquivo, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.conexoes.append({
                        'origem': row['origem'],
                        'destino': row['destino'],
                        'tempo': int(row['tempo'])
                    })
            print(f"Conexões carregadas: {len(self.conexoes)}")
        except Exception as e:
            print(f"Erro ao ler conexões: {e}")
    
    def ler_entregas(self, arquivo):
        """Lê as entregas disponíveis de um arquivo CSV."""
        try:
            with open(arquivo, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.entregas.append({
                        'id': row['id'],
                        'origem': row['origem'],
                        'destino': row['destino'],
                        'prazo': datetime.strptime(row['prazo'], '%Y-%m-%d'),
                        'valor': float(row['valor']),
                        'bonus': float(row['bonus'])
                    })
            print(f"Entregas carregadas: {len(self.entregas)}")
        except Exception as e:
            print(f"Erro ao ler entregas: {e}")
    
    def calcular_tempo_entrega(self, origem, destino):
        """Calcula o tempo necessário para uma entrega entre dois pontos."""
        for conexao in self.conexoes:
            if conexao['origem'] == origem and conexao['destino'] == destino:
                return conexao['tempo']
        return None  # Conexão não encontrada
    
    def selecionar_entregas(self, data_atual, capacidade_diaria=5):
        """
        Algoritmo básico para selecionar entregas.
        Seleciona entregas com base no maior bônus oferecido.
        """
        # Filtrar entregas que ainda estão no prazo
        entregas_validas = [e for e in self.entregas if e['prazo'] >= data_atual]
        
        # Ordenar entregas pelo valor do bônus (do maior para o menor)
        entregas_ordenadas = sorted(entregas_validas, key=lambda x: x['bonus'], reverse=True)
        
        # Selecionar até o limite de capacidade diária
        entregas_selecionadas = entregas_ordenadas[:capacidade_diaria]
        
        return entregas_selecionadas
    
    def exibir_programacao(self, entregas_selecionadas):
        """Exibe a programação de entregas e calcula o lucro total."""
        print("\n===== PROGRAMAÇÃO DE ENTREGAS =====")
        print("ID\tOrigem\tDestino\tTempo\tValor\tBônus\tLucro Total")
        
        lucro_total = 0
        tempo_total = 0
        
        for entrega in entregas_selecionadas:
            tempo = self.calcular_tempo_entrega(entrega['origem'], entrega['destino'])
            tempo_total += tempo if tempo else 0
            lucro = entrega['valor'] + entrega['bonus']
            lucro_total += lucro
            
            print(f"{entrega['id']}\t{entrega['origem']}\t{entrega['destino']}\t{tempo}\t{entrega['valor']}\t{entrega['bonus']}\t{lucro}")
        
        print(f"\nTempo total estimado: {tempo_total} minutos")
        print(f"Lucro total esperado: R$ {lucro_total:.2f}")
        print("==================================")
        
        return lucro_total

# Exemplo de uso
if __name__ == "__main__":
    sistema = SistemaEntrega()
    
    # Para teste, crie arquivos CSV com os seguintes formatos:
    # conexoes.csv: origem,destino,tempo
    # entregas.csv: id,origem,destino,prazo,valor,bonus
    
    sistema.ler_conexoes("conexoes.csv")
    sistema.ler_entregas("entregas.csv")
    
    # Data atual para comparação com os prazos
    data_atual = datetime.strptime('2023-11-15', '%Y-%m-%d')
    
    # Selecionar entregas para o dia
    entregas_selecionadas = sistema.selecionar_entregas(data_atual)
    
    # Exibir programação
    sistema.exibir_programacao(entregas_selecionadas)