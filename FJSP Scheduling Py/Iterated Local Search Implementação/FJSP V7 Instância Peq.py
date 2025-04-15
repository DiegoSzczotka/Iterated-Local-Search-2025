import random
import copy
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


class FJSP_ILS:
    def __init__(self):
        # Lista de Trabalhos e Máquinas
        self.trabalhos = [1, 2]             # Lista de trabalhos (jobs)
        self.maquinas = [1, 2, 3, 4]        # Máquinas disponíveis para processamento
        self.operacoes_por_trabalho = 4     # Número de operações por trabalho

        # Lista de Operações globais
        total_operacoes = len(self.trabalhos) * self.operacoes_por_trabalho
        self.operacoes = list(range(1, total_operacoes + 1))  # Enumera todas as operações

        # Tempos de Processamento [Job][Operation][Machine]
        self.tempos_processamento = {
            1: {  # Job 1
                1: {1: 456, 2: 999999, 3: 999999, 4: 456},      # OP 1
                2: {1: 999999, 2: 856, 3: 856, 4: 856},         # OP 2
                3: {1: 963, 2: 999999, 3: 963, 4: 963},         # OP 3
                4: {1: 999999, 2: 999999, 3: 999999, 4: 696}    # OP 4
            },
            2: {  # Job 2
                1: {1: 789, 2: 789, 3: 789, 4: 999999},         # OP 1
                2: {1: 999999, 2: 930, 3: 930, 4: 930},         # OP 2
                3: {1: 999999, 2: 21, 3: 21, 4: 21},            # OP 3
                4: {1: 320, 2: 320, 3: 320, 4: 999999}          # OP 4
            }
        }

        # Define as precedências entre operações
        self.predecessoras = {}
        for trabalho in self.trabalhos:
            op_inicial = (trabalho - 1) * self.operacoes_por_trabalho + 1
            for i in range(self.operacoes_por_trabalho):
                op_atual = op_inicial + i
                if i == 0:
                    self.predecessoras[op_atual] = None          # Primeira operação não tem predecessora
                else:
                    self.predecessoras[op_atual] = op_atual - 1  # Operação anterior é predecessora

    def obter_trabalho_e_indice_operacao(self, op):
        # Retorna o trabalho e o índice da operação (Exemplo: Op 6 pertence ao Job 2, Op 2)
        trabalho = ((op - 1) // self.operacoes_por_trabalho) + 1
        indice_operacao = ((op - 1) % self.operacoes_por_trabalho) + 1
        return trabalho, indice_operacao
    def criar_solucao_inicial(self):
        

        # Gera uma solução inicial aleatória
        solucao = {'atribuicao_maquinas': {}, 'sequencia_operacoes': []}
        for op in self.operacoes:
            trabalho, indice_operacao = self.obter_trabalho_e_indice_operacao(op)
            maquinas_disponiveis = [
                maquina for maquina in self.maquinas
                if self.tempos_processamento[trabalho][indice_operacao][maquina] < 999999]
            solucao['atribuicao_maquinas'][op] = random.choice(maquinas_disponiveis)

        # Geração da sequência inicial, respeitando as precedências
        operacoes_restantes = self.operacoes[:]
        while operacoes_restantes:
            ops_disponiveis = [
                op for op in operacoes_restantes
                if self.predecessoras[op] is None or self.predecessoras[op] in solucao['sequencia_operacoes']
            ]
            # Seleciona uma operação disponível
            op_selecionada = random.choice(ops_disponiveis)
            solucao['sequencia_operacoes'].append(op_selecionada)
            operacoes_restantes.remove(op_selecionada)

        return solucao

          # Calcula o Makespan (Tempo de processamento do Job mais demorado)
    def calcular_makespan(self, solucao):
       
        disponibilidade_maquinas = {m: 0 for m in self.maquinas}
        tempo_conclusao_operacoes = {}
        tempo_conclusao_trabalhos = {t: 0 for t in self.trabalhos}
        for op in solucao['sequencia_operacoes']:
            maquina = solucao['atribuicao_maquinas'][op]
            trabalho, indice_operacao = self.obter_trabalho_e_indice_operacao(op)

            # Calcula o início mais cedo considerando predecessoras e disponibilidade da máquina
            if self.predecessoras[op] is not None:
                predecessora = self.predecessoras[op]
                if predecessora in tempo_conclusao_operacoes:
                    inicio_mais_cedo = tempo_conclusao_operacoes[predecessora]
                else:
                    raise ValueError(f"Precedência violada: {op} depende de {predecessora}, que não foi concluída.")
            else:
                inicio_mais_cedo = 0
            inicio = max(disponibilidade_maquinas[maquina], inicio_mais_cedo)
            tempo_proc = self.tempos_processamento[trabalho][indice_operacao][maquina]
            tempo_conclusao = inicio + tempo_proc

            tempo_conclusao_operacoes[op] = tempo_conclusao
            disponibilidade_maquinas[maquina] = tempo_conclusao
            tempo_conclusao_trabalhos[trabalho] = max(tempo_conclusao_trabalhos[trabalho], tempo_conclusao)
        return max(tempo_conclusao_trabalhos.values())
    

             # Perturba a solução atual respeitando precedências
    def perturbar_solucao(self, solucao, quantidade_maquinas=1, quantidade_operacoes=1):
        nova_solucao = copy.deepcopy(solucao)

             # Trocar máquinas de múltiplas operações
        operacoes_para_alterar = random.sample(self.operacoes, min(quantidade_maquinas, len(self.operacoes)))
        for op in operacoes_para_alterar:
            trabalho, indice_operacao = self.obter_trabalho_e_indice_operacao(op)
            maquina_atual = nova_solucao['atribuicao_maquinas'][op]
            maquinas_disponiveis = [
                maquina for maquina in self.maquinas
                if self.tempos_processamento[trabalho][indice_operacao][maquina] < 999999
                and maquina != maquina_atual]

            # Atribuir uma nova máquina, se disponível
            if maquinas_disponiveis:
                nova_solucao['atribuicao_maquinas'][op] = random.choice(maquinas_disponiveis)

        # Perturbando sequência de operações
        operacoes_restantes = self.operacoes[:]
        nova_sequencia = []

        # Perturbar apenas um subconjunto de operações
        quantidade_para_perturbar = min(quantidade_operacoes, len(operacoes_restantes))
        operacoes_para_perturbar = random.sample(operacoes_restantes, quantidade_para_perturbar)

        while operacoes_restantes:
            ops_disponiveis = [
                op for op in operacoes_restantes
                if self.predecessoras[op] is None or self.predecessoras[op] in nova_sequencia]

            # Introduzir maior aleatoriedade para operações escolhidas
            if any(op in operacoes_para_perturbar for op in ops_disponiveis):
                op_selecionada = random.choice([op for op in ops_disponiveis if op in operacoes_para_perturbar])
            else:
                op_selecionada = random.choice(ops_disponiveis)

            nova_sequencia.append(op_selecionada)
            operacoes_restantes.remove(op_selecionada)

        nova_solucao['sequencia_operacoes'] = nova_sequencia
        return nova_solucao


    def busca_local(self, solucao):
        # Melhorar solução localmente
        melhor_solucao = copy.deepcopy(solucao)
        melhor_makespan = self.calcular_makespan(solucao)

        for op in self.operacoes:
            trabalho, indice_operacao = self.obter_trabalho_e_indice_operacao(op)
            maquina_atual = melhor_solucao['atribuicao_maquinas'][op]

            maquinas_disponiveis = [
                maquina for maquina in self.maquinas
                if self.tempos_processamento[trabalho][indice_operacao][maquina] < 999999
            ]
            for maquina in maquinas_disponiveis:
                if maquina != maquina_atual:
                    nova_solucao = copy.deepcopy(melhor_solucao)
                    nova_solucao['atribuicao_maquinas'][op] = maquina
                    novo_makespan = self.calcular_makespan(nova_solucao)
                    if novo_makespan < melhor_makespan:
                        melhor_solucao = nova_solucao
                        melhor_makespan = novo_makespan

        return melhor_solucao

    def executar_ils(self, max_iteracoes=100, sem_melhoria_max=20):
        # Executa o Iterated Local Search (ILS)
        melhor_solucao = self.criar_solucao_inicial()
        melhor_solucao = self.busca_local(melhor_solucao)
        melhor_makespan = self.calcular_makespan(melhor_solucao)

        iteracoes_sem_melhoria = 0
        for i in range(max_iteracoes):
            solucao_perturbada = self.perturbar_solucao(melhor_solucao)
            solucao_ajustada = self.busca_local(solucao_perturbada)
            makespan_ajustado = self.calcular_makespan(solucao_ajustada)

            if makespan_ajustado < melhor_makespan:
                melhor_solucao = solucao_ajustada
                melhor_makespan = makespan_ajustado
                iteracoes_sem_melhoria = 0
            else:
                iteracoes_sem_melhoria += 1

            if iteracoes_sem_melhoria >= sem_melhoria_max:
                break

        return melhor_solucao, melhor_makespan


def gerar_grafico_gantt(sequencia, atribuicoes, tempos_processamento, maquinas, operacoes_por_trabalho):
    # Função de geração de gráfico de Gantt com máquinas em ordem invertida
    disponibilidade_maquinas = {m: 0 for m in maquinas}
    tempo_proximo_job = {t: 0 for t in range(1, len(maquinas) + 1)}
    cores_jobs = {1: "green", 2: "red"}
    tempo_maximo_gantt = 0

    fig, ax = plt.subplots(figsize=(16, 8))

    # Reverter a ordem das máquinas para exibir do maior para o menor
    maquinas_invertidas = sorted(maquinas, reverse=True)

    for op in sequencia:
        trabalho = ((op - 1) // operacoes_por_trabalho) + 1
        indice_op = ((op - 1) % operacoes_por_trabalho) + 1

        maquina = atribuicoes[op]
        tempo_proc = tempos_processamento[trabalho][indice_op][maquina]

        inicio = max(disponibilidade_maquinas[maquina], tempo_proximo_job[trabalho])
        fim = inicio + tempo_proc
        disponibilidade_maquinas[maquina] = fim
        tempo_proximo_job[trabalho] = fim

        tempo_maximo_gantt = max(tempo_maximo_gantt, fim)

        cor = cores_jobs[trabalho]
        y_posicao = maquinas_invertidas.index(maquina)
        ax.barh(y=y_posicao, width=tempo_proc, left=inicio, color=cor, edgecolor="black")
        ax.text(x=inicio + tempo_proc / 2, y=y_posicao, s=f"Job {trabalho} - Op {indice_op}",
                va="center", ha="center", color="white")

    print(f"\n[Makespan do Gráfico: {tempo_maximo_gantt}]")
    ax.set_title("Gráfico de Gantt - Makespan",fontsize=16, fontweight='bold')
    ax.set_xlabel("Tempo",fontsize=14, fontweight='bold')
    ax.set_ylabel("")
    ax.grid(which="both", linestyle="--", alpha=0.5)
    ax.set_yticks(range(len(maquinas)))
    ax.set_yticklabels([f"Máquina {m}" for m in maquinas_invertidas],fontsize=16, fontweight='bold')

    legend_labels = [mpatches.Patch(color=color, label=f"Job, {job}") for job, color in cores_jobs.items()]
    ax.legend(handles=legend_labels, loc="upper right", fontsize=14, title_fontsize=15, frameon=True)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    resolvedor = FJSP_ILS()
    try:
        melhor_solucao, melhor_makespan = resolvedor.executar_ils(max_iteracoes=100, sem_melhoria_max=20)
        print("\n--- RESULTADOS ---")
        print(f"Melhor Makespan: {melhor_makespan}")
        print("Sequência de Operações:", melhor_solucao['sequencia_operacoes'])
        print("Atribuição de Máquinas:", melhor_solucao['atribuicao_maquinas'])

        gerar_grafico_gantt(
            sequencia=melhor_solucao['sequencia_operacoes'],
            atribuicoes=melhor_solucao['atribuicao_maquinas'],
            tempos_processamento=resolvedor.tempos_processamento,
            maquinas=resolvedor.maquinas,
            operacoes_por_trabalho=resolvedor.operacoes_por_trabalho
        )
    except Exception as e:
        print(f"Ocorreu um erro: {e}")    