from scipy.stats import kurtosis
import numpy as np

def PPG_analysis(signal: list, fs: float, window_size: int) -> dict:
    """
    Seleciona a melhor janela do sinal PPG através de uma análise de SQI.

    Parâmetros:
        signal (list): Os dados do sinal PPG como uma lista de valores.
        fs (float): Taxa de quadros dos dados.
        window_size (int): Tamanho da janela para análise, em segundos.
    
    Retorna:
        dict: O melhor segmento de sinal e os valores de NSQI e KSQI.
        {'acc_window': acc_window, 'exc_window': exc_window, 'LSQI': lowest_NSQI, 'KSQI': b_KSQI}
    """

    window_size = window_size * fs
    exc_window = []
    acc_window = []
    lowest_NSQI = float('inf')
    b_KSQI = None
    try:
        for i in range(0, int(len(signal) - window_size + 1)):
            window = signal[i:int(i + window_size)]

            NSQI = abs(SNR(window))    
            KSQI = abs(Kurtosis(window))
            if NSQI < lowest_NSQI:
                if NSQI < 0.293:
                    exc_window = window
                elif NSQI > 0.293 and KSQI < 0.221:
                    acc_window = window
                    b_KSQI = KSQI
                lowest_NSQI = NSQI

        return {'acc_window': acc_window, 'exc_window': exc_window, 'LSQI': lowest_NSQI, 'KSQI': b_KSQI}
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