from scipy.stats import kurtosis
import numpy as np

def PPG_analysis(signal: list, fs: float, window_size: int) -> float:
    """
    Seleciona a melhor janela do sinal PPG através de uma análise de SQI.

    Parâmetros:
        signal (list): Os dados do sinal PPG como uma lista de valores.
        fs (float): Taxa de quadros dos dados.
        window_size (int): Tamanho da janela para análise, em segundos.
    
    Retorna:
        float: Valor do maior NSQI
        highest_NSQI
    """

    window_size = window_size * fs
    highest_NSQI = float('-inf')
    try:
        for i in range(0, int(len(signal) - window_size + 1)):
            window = signal[i:int(i + window_size)]

            NSQI = SNR(window)
            if NSQI > highest_NSQI:
                highest_NSQI = NSQI

        return highest_NSQI
    except Exception as e:
        print(f"Erro: {e}")

def PPG_analysis2(signal: list, fs: float, window_size: int) -> float:
    """
    Seleciona a melhor janela do sinal PPG através de uma análise de SQI.

    Parâmetros:
        signal (list): Os dados do sinal PPG como uma lista de valores.
        fs (float): Taxa de quadros dos dados.
        window_size (int): Tamanho da janela para análise, em segundos.
    
    Retorna:
        float: Valor do meno NSQI
        lowest_NSQI
    """

    window_size = window_size * fs
    lowest_NSQI = float('inf')
    try:
        for i in range(0, int(len(signal) - window_size + 1)):
            window = signal[i:int(i + window_size)]

            NSQI = abs(SNR(window))    
            if NSQI < lowest_NSQI:
                lowest_NSQI = NSQI

        return lowest_NSQI
    except Exception as e:
        print(f"Erro: {e}")
""" 
    As funções abaixo devem receber um sinal PPG no formato list ou np.array
    e retornam os respectivos resultados da analise do sinal PPG.
"""

def Kurtosis(signal: list) -> float:
    """
        A Kurtosis mede como as caudas de uma distribuição diferem das de uma distribuição normal. 
    Ela determina se valores extremos estão presentes na distribuição e foi considerada um bom 
    indicador da qualidade do sinal de PPG.
    """

    KSQI = kurtosis(signal)

    return KSQI

def SNR(signal, axis=0, ddof=0) -> float:
    """
        Esse SQI compara a potência do sinal desejável com a potência do ruído de fundo indesejado.
    """
    a = np.asanyarray(signal)
    m = a.mean(axis)
    sd = a.std(axis=axis, ddof=ddof)

    return np.where(sd == 0, 0, m/sd)