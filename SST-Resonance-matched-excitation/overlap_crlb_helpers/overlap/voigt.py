
import numpy as np
try:
    import mpmath as mp
    _HAS_MPMATH = True
except Exception:
    _HAS_MPMATH = False

def _faddeeva_w(z):
    return mp.e**(-z**2) * mp.erfc(-1j*z)

def voigt_profile(delta, sigma, gamma):
    delta = np.asarray(delta, dtype=float)
    sigma = float(sigma); gamma = float(gamma)
    if sigma <= 0 or gamma < 0:
        raise ValueError("sigma>0, gamma>=0 required")
    if _HAS_MPMATH:
        out = np.empty_like(delta, dtype=float)
        pref = sigma * np.sqrt(2.0*np.pi)
        for i, d in enumerate(delta):
            z = (d + 1j*gamma) / (sigma*np.sqrt(2.0))
            out[i] = float(mp.re(_faddeeva_w(z))) / pref
        return out
    else:
        G = (1.0/(sigma*np.sqrt(2.0*np.pi))) * np.exp(-delta**2/(2.0*sigma**2))
        L = (gamma/np.pi) / (delta**2 + gamma**2 + 1e-300)
        a = gamma / (gamma + 0.5346*sigma + np.sqrt(0.2166*sigma**2 + gamma**2))
        eta = np.clip(1.36603*a - 0.47719*a*a + 0.11116*a*a*a, 0.0, 1.0)
        return eta*L + (1.0-eta)*G

def voigt_and_grads(delta, sigma, gamma):
    delta = np.asarray(delta, dtype=float)
    if _HAS_MPMATH:
        V = voigt_profile(delta, sigma, gamma)
        out_dD = np.empty_like(V); out_dG = np.empty_like(V); out_dS = np.empty_like(V)
        pref = 1.0/(sigma*np.sqrt(2.0*np.pi))
        for i, d in enumerate(delta):
            z = (d + 1j*gamma) / (sigma*np.sqrt(2.0))
            w = _faddeeva_w(z)
            wp = -2.0*z*w + 2j/np.sqrt(np.pi)
            dVdD = pref * np.real(wp) * (1.0/(sigma*np.sqrt(2.0)))
            dVdG = pref * np.real(wp * (1j)) * (1.0/(sigma*np.sqrt(2.0)))
            dpref = -1.0/(sigma*sigma*np.sqrt(2.0*np.pi))
            dVdS = dpref * np.real(w) + pref * np.real(wp * ( - z / sigma ))
            out_dD[i]=dVdD; out_dG[i]=dVdG; out_dS[i]=dVdS
        return V, out_dD, out_dG, out_dS
    else:
        V = voigt_profile(delta, sigma, gamma)
        epsD = 1e-6 * (1.0 + np.abs(delta))
        epsG = 1e-6 * (1.0 + abs(gamma))
        epsS = 1e-6 * (1.0 + abs(sigma))
        dVdD = (voigt_profile(delta+epsD, sigma, gamma) - voigt_profile(delta-epsD, sigma, gamma)) / (2.0*epsD)
        dVdG = (voigt_profile(delta, sigma, gamma+epsG) - voigt_profile(delta, sigma, gamma-epsG)) / (2.0*epsG)
        dVdS = (voigt_profile(delta, sigma+epsS, gamma) - voigt_profile(delta, sigma-epsS, gamma)) / (2.0*epsS)
        return V, dVdD, dVdG, dVdS
