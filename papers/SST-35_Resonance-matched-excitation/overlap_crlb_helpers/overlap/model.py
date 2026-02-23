
import numpy as np
from .voigt import voigt_profile, voigt_and_grads

def predict_Y(omega0, sigma, omega_n, gamma_n, B_n, A=1.0):
    omega0 = np.asarray(omega0, dtype=float)
    sigma  = np.asarray(sigma, dtype=float)
    omega_n = np.asarray(omega_n, dtype=float)
    gamma_n = np.asarray(gamma_n, dtype=float)
    B_n     = np.asarray(B_n, dtype=float)
    K = omega0.shape[0]; N = omega_n.shape[0]
    Y = np.zeros(K, dtype=float)
    for k in range(K):
        s = sigma[k]
        d = omega0[k] - omega_n
        Vn = np.empty(N, dtype=float)
        for n in range(N):
            Vn[n] = voigt_profile(np.array([d[n]]), s, gamma_n[n])[0]
        Y[k] = A*np.sum(B_n*Vn)
    return Y

def jacobian(omega0, sigma, omega_n, gamma_n, B_n, A=1.0, wrt=("A","B","omega","gamma")):
    omega0 = np.asarray(omega0, dtype=float)
    sigma  = np.asarray(sigma, dtype=float)
    omega_n = np.asarray(omega_n, dtype=float)
    gamma_n = np.asarray(gamma_n, dtype=float)
    B_n     = np.asarray(B_n, dtype=float)
    K = omega0.shape[0]; N = omega_n.shape[0]
    cols=[]; names=[]
    if "A" in wrt:
        colA = np.zeros(K)
        for k in range(K):
            s = sigma[k]; d = omega0[k] - omega_n
            Vn = np.array([voigt_profile(np.array([d[n]]), s, gamma_n[n])[0] for n in range(N)])
            colA[k] = np.sum(B_n*Vn)
        cols.append(colA); names.append("A")
    if "B" in wrt:
        for n in range(N):
            col = np.zeros(K)
            for k in range(K):
                s = sigma[k]; d = omega0[k] - omega_n[n]
                V, dVdD, dVdG, dVdS = voigt_and_grads(np.array([d]), s, gamma_n[n])
                col[k] = A * V[0]
            cols.append(col); names.append(f"B[{n}]")
    if "omega" in wrt:
        for n in range(N):
            col = np.zeros(K)
            for k in range(K):
                s = sigma[k]; d = omega0[k] - omega_n[n]
                V, dVdD, dVdG, dVdS = voigt_and_grads(np.array([d]), s, gamma_n[n])
                col[k] = -A * B_n[n] * dVdD[0]
            cols.append(col); names.append(f"omega[{n}]")
    if "gamma" in wrt:
        for n in range(N):
            col = np.zeros(K)
            for k in range(K):
                s = sigma[k]; d = omega0[k] - omega_n[n]
                V, dVdD, dVdG, dVdS = voigt_and_grads(np.array([d]), s, gamma_n[n])
                col[k] =  A * B_n[n] * dVdG[0]
            cols.append(col); names.append(f"gamma[{n}]")
    J = np.stack(cols, axis=1) if cols else np.zeros((K,0))
    return J, names
