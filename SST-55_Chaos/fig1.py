import numpy as np
import matplotlib.pyplot as plt

Omega = np.linspace(-10, 10, 1000)
omega0 = 0.0
kappa = 1.5
tau = 2.0

plt.plot(Omega, Omega, label=r"$\Omega$")
plt.plot(Omega, omega0 - kappa*np.sin(Omega*tau),
         label=r"$\omega_0 - \kappa\sin(\Omega\tau)$")

plt.xlabel(r"$\Omega$")
plt.ylabel("frequency map")
plt.legend()
plt.grid(True)
# ✅ Get the script filename dynamically
import os
from datetime import datetime
script_name = os.path.splitext(os.path.basename(__file__))[0]
timestamp = datetime.now().strftime("%H%M%S")
filename = f"{script_name}_1_{timestamp}.png"
plt.savefig(filename, dpi=150)  # Save image with high resolution



Omega = np.linspace(-10,10,2000)
kappa = 1.5
tau = 2.0
stability = 1 + kappa*tau*np.cos(Omega*tau)

plt.plot(Omega, stability)
plt.axhline(0, color='k', linestyle='--')
plt.fill_between(Omega, stability, where=(stability>0), alpha=0.3)
plt.xlabel(r"$\Omega$")
plt.ylabel("stability criterion")
filename = f"{script_name}_2_{timestamp}.png"
plt.savefig(filename, dpi=150)  # Save image with high resolution
plt.show()