
import json, numpy as np
from overlap import predict_Y, jacobian
from overlap.design import fisher_information, crlb_from_fim, greedy_d_opt

rng = np.random.default_rng(123)
A_true = 1.0
omega_true = np.array([0.0, 5.0])
gamma_true = np.array([0.8, 0.5])
B_true     = np.array([1.2, 0.7])

omega0_grid = np.linspace(-3.0, 8.0, 40)
sigma_grid  = np.array([0.3, 0.8, 1.5])
omega0_cand, sigma_cand = np.meshgrid(omega0_grid, sigma_grid, indexing="ij")
omega0_cand = omega0_cand.ravel(); sigma_cand = sigma_cand.ravel()

K = 25
chosen = greedy_d_opt({"omega0": omega0_cand, "sigma": sigma_cand}, K,
                      omega_true, gamma_true, B_true, A=A_true, sigma_eps=0.02,
                      wrt=("B","omega","gamma"))
omega0 = omega0_cand[chosen]; sigma = sigma_cand[chosen]

sigma_eps = 0.02
y_true = predict_Y(omega0, sigma, omega_true, gamma_true, B_true, A=A_true)
y = y_true + rng.normal(scale=sigma_eps, size=y_true.shape)

theta = np.concatenate([B_true*0 + 1.0, omega_true + 0.2, gamma_true + 0.1])
N = len(omega_true)
for it in range(15):
    B = theta[:N]; om = theta[N:2*N]; ga = theta[2*N:3*N]
    mu = predict_Y(omega0, sigma, om, ga, B, A=A_true)
    J, names = jacobian(omega0, sigma, om, ga, B, A=A_true, wrt=("B","omega","gamma"))
    H = J.T @ J + 1e-6*np.eye(J.shape[1]); g = J.T @ (y - mu)
    step = np.linalg.solve(H, g); theta = theta + step
    if np.linalg.norm(step) < 1e-8: break

B_hat = theta[:N]; omega_hat = theta[N:2*N]; gamma_hat = theta[2*N:3*N]
I, names = fisher_information(omega0, sigma, omega_hat, gamma_hat, B_hat, A=A_true, sigma_eps=sigma_eps,
                              wrt=("B","omega","gamma"))
diag_crlb, C = crlb_from_fim(I)
summary = {
  "chosen_indices": list(map(int, chosen)),
  "theta_true": {"B": B_true.tolist(), "omega": omega_true.tolist(), "gamma": gamma_true.tolist()},
  "theta_hat": {"B": B_hat.tolist(), "omega": omega_hat.tolist(), "gamma": gamma_hat.tolist()},
  "FIM_eigs": np.linalg.eigvalsh(I).tolist(),
  "CRLB_diag": diag_crlb.tolist(),
  "param_names": names,
}
with open("demo_output.json", "w") as f: json.dump(summary, f, indent=2)
print("Recovered params:", summary["theta_hat"])
print("True params     :", summary["theta_true"])
print("Smallest FIM eigenvalue:", min(summary["FIM_eigs"]))
print("Wrote demo_output.json")
