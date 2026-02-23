
import numpy as np
from .model import jacobian

def fisher_information(omega0, sigma, omega_n, gamma_n, B_n, A=1.0, sigma_eps=1.0, wrt=("A","B","omega","gamma")):
    J, names = jacobian(omega0, sigma, omega_n, gamma_n, B_n, A=A, wrt=wrt)
    I = (J.T @ J) / (sigma_eps**2)
    return I, names

def crlb_from_fim(I):
    try:
        C = np.linalg.inv(I)
    except np.linalg.LinAlgError:
        C = np.linalg.pinv(I)
    return np.diag(C), C

def greedy_d_opt(candidates, K, omega_n, gamma_n, B_n, A=1.0, sigma_eps=1.0, wrt=("A","B","omega","gamma")):
    omega0_all = np.asarray(candidates["omega0"], dtype=float)
    sigma_all  = np.asarray(candidates["sigma"], dtype=float)
    M = len(omega0_all)
    chosen=[]; best_det=-np.inf
    for _ in range(K):
        best=None; best_val=-np.inf
        for m in range(M):
            if m in chosen: continue
            idx = chosen + [m]
            from .design import fisher_information
            I, _ = fisher_information(omega0_all[idx], sigma_all[idx], omega_n, gamma_n, B_n, A=A, sigma_eps=sigma_eps, wrt=wrt)
            if np.linalg.matrix_rank(I) < I.shape[0]: val = -np.inf
            else: val = np.linalg.slogdet(I)[1]
            if val > best_val: best_val = val; best = m
        chosen.append(best)
    return chosen
