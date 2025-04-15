# Modelo de Escalonamento Flexível (Flexible Job Shop Scheduling)  

# Conjuntos  
set J;    # Jobs  
set M;    # Máquinas  
set O;    # Operações  
set R within (O cross M); # Máquinas elegíveis para cada operação  


# Parâmetros  
param tp{J,O,M};     # Tempos de processamento  
param pr{O};         # Operação predecessora    
param H := 999999;  # Valor suficientemente grande para big-M  


# Variáveis de Decisão  
  
var t{O} >=0        integer;            #Tempo de início
var Cmax >=0        integer;            # Makespan  
var alfa{O, M}      binary;            # Atribuição de máquina  
var beta{O,O}       binary;            # Sequenciamento de operações


# Função Objetivo  
minimize Makespan: Cmax;  

# Restrições  


subject to rt2 {i in O}:            #Atribui cada Operação a apenas uma máquina elegível
	sum{(i,k) in R} alfa[i, k] = 1; 
	

subject to rt3 {i in O: pr[i] > 0}:   #Define relação de precedência entre operações do mesmo Job
    t[i] >= t[pr[i]] + sum{(pr[i],k) in R} (tp[1,pr[i],k] * alfa[pr[i],k]);
    
# Restrição (4) e (5) evitam a sobreposição de duas operações na mesma máquina k,
subject to rt4 {i in O, i2 in O, m in M: 
    i != i2 and (i,m) in R and (i2,m) in R}:
    t[i] >= t[i2] + sum{k in M: (i2,k) in R} (tp[1,i2,k] * alfa[i2,k]) 
    - H * (2 - alfa[i,m] - alfa[i2,m] + beta[i,i2]);

# Restrição (5)    
subject to rt5 {i in O, i2 in O, m in M: 
    i != i2 and (i,m) in R and (i2,m) in R}:
    t[i2] >= t[i] + sum{k in M: (i,k) in R} (tp[1,i,k] * alfa[i,k]) 
    - H * (3 - alfa[i,m] - alfa[i2,m] - beta[i,i2]);



subject to rt6 {i in O}:              # Definição do Makespan Rt6
    Cmax >= t[i] + sum{(i,k) in R} (tp[1,i,k] * alfa[i,k]);
    
 
    