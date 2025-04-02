import csv
import random
from datetime import datetime

class SistemaEntregaIA:
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
        return None
    
    def avaliar_solucao(self, solucao, data_atual):
        """
        Avalia uma solução calculando o tempo total e o lucro total.
        Retorna uma tupla (tempo_total, lucro_total)
        """
        tempo_total = 0
        lucro_total = 0
        
        for id_entrega in solucao:
            entrega = next((e for e in self.entregas if e['id'] == id_entrega), None)
            if entrega and entrega['prazo'] >= data_atual:
                tempo = self.calcular_tempo_entrega(entrega['origem'], entrega['destino'])
                if tempo:
                    tempo_total += tempo
                    lucro_total += entrega['valor'] + entrega['bonus']
        
        return (tempo_total, lucro_total)
    
    def algoritmo_genetico(self, data_atual, tamanho_populacao=50, geracoes=100, capacidade_diaria=5):
        """
        Implementa um algoritmo genético para encontrar a melhor combinação de entregas.
        """
        # Filtrar entregas válidas
        entregas_validas = [e for e in self.entregas if e['prazo'] >= data_atual]
        if not entregas_validas:
            return []
        
        # Gerar população inicial
        populacao = []
        for _ in range(tamanho_populacao):
            # Cada indivíduo é uma seleção aleatória de entregas
            if len(entregas_validas) <= capacidade_diaria:
                solucao = [e['id'] for e in entregas_validas]
            else:
                solucao = [e['id'] for e in random.sample(entregas_validas, capacidade_diaria)]
            populacao.append(solucao)
        
        melhor_solucao = None
        melhor_avaliacao = (float('inf'), 0)  # (tempo, lucro)
        
        for geracao in range(geracoes):
            # Avaliar cada solução
            avaliacoes = []
            for solucao in populacao:
                avaliacao = self.avaliar_solucao(solucao, data_atual)
                avaliacoes.append((solucao, avaliacao))
                
                # Verifica se é a melhor solução até agora (menor tempo e maior lucro)
                if avaliacao[0] < melhor_avaliacao[0] or (avaliacao[0] == melhor_avaliacao[0] and avaliacao[1] > melhor_avaliacao[1]):
                    melhor_solucao = solucao
                    melhor_avaliacao = avaliacao
            
            # Ordenar por fitness (menor tempo e maior lucro)
            avaliacoes.sort(key=lambda x: (-x[1][1], x[1][0]))
            
            # Seleção dos melhores (elitismo)
            elite = [item[0] for item in avaliacoes[:10]]
            
            # Criar nova população
            nova_populacao = elite.copy()
            
            # Cruzamento e mutação
            while len(nova_populacao) < tamanho_populacao:
                # Seleção de pais
                pai1 = random.choice(elite)
                pai2 = random.choice(elite)
                
                # Cruzamento
                if min(len(pai1), len(pai2)) > 1:
                    ponto_corte = random.randint(1, min(len(pai1), len(pai2)) - 1)
                else:
                    ponto_corte = 1  # Ou outra abordagem para lidar com cromossomos pequenos

                filho = pai1[:ponto_corte] + [x for x in pai2 if x not in pai1[:ponto_corte]]
                
                # Garantir que o filho tenha o tamanho correto
                if len(filho) > capacidade_diaria:
                    filho = filho[:capacidade_diaria]
                elif len(filho) < capacidade_diaria and len(entregas_validas) > capacidade_diaria:
                    # Adicionar entregas aleatórias para completar
                    entregas_disponiveis = [e['id'] for e in entregas_validas if e['id'] not in filho]
                    if entregas_disponiveis:
                        filho.extend(random.sample(entregas_disponiveis, min(capacidade_diaria - len(filho), len(entregas_disponiveis))))
                
                # Mutação (com baixa probabilidade)
                if random.random() < 0.1 and len(entregas_validas) > capacidade_diaria:
                    # Substituir uma entrega aleatória
                    idx = random.randint(0, len(filho) - 1)
                    entregas_disponiveis = [e['id'] for e in entregas_validas if e['id'] not in filho]
                    if entregas_disponiveis:
                        filho[idx] = random.choice(entregas_disponiveis)
                
                nova_populacao.append(filho)
            
            populacao = nova_populacao
        
        # Recuperar as entregas completas a partir dos IDs
        entregas_selecionadas = []
        for id_entrega in melhor_solucao:
            entrega = next((e for e in self.entregas if e['id'] == id_entrega), None)
            if entrega:
                entregas_selecionadas.append(entrega)
        
        return entregas_selecionadas
    
    def exibir_programacao(self, entregas_selecionadas):
        """Exibe a programação de entregas e calcula o lucro total."""
        print("\n===== PROGRAMAÇÃO DE ENTREGAS OTIMIZADA =====")
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
        print("==========================================")
        
        return lucro_total, tempo_total

# Exemplo de uso
if __name__ == "__main__":
    sistema = SistemaEntregaIA()
    
    # Para teste, crie arquivos CSV com os seguintes formatos:
    # conexoes.csv: origem,destino,tempo
    # entregas.csv: id,origem,destino,prazo,valor,bonus
    
    sistema.ler_conexoes("conexoes.csv")
    sistema.ler_entregas("entregas.csv")
    
    # Data atual para comparação com os prazos
    data_atual = datetime.strptime('2023-11-15', '%Y-%m-%d')
    
    # Selecionar entregas usando algoritmo genético
    entregas_selecionadas = sistema.algoritmo_genetico(data_atual)
    
    # Exibir programação
    sistema.exibir_programacao(entregas_selecionadas)