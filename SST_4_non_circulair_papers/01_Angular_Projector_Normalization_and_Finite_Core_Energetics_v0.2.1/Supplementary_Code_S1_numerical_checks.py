#!/usr/bin/env python3
"""Reproduce selected v0.2.0 numerical diagnostics from Supplementary Data S1."""
from pathlib import Path
import argparse, json, math, re
import numpy as np


def load_coeffs(path):
    raw=Path(path).read_text(encoding="utf-8", errors="replace")
    coeff=[]
    for m in re.finditer(r'<Coeff\b([^>]*)/>', raw, re.S):
        attrs=dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
        n=int(attrs['I'])
        A=np.fromstring(attrs['A'],sep=',')
        B=np.fromstring(attrs['B'],sep=',')
        coeff.append((n,A,B))
    return coeff


def evaluate(coeff,N):
    t=np.linspace(0,2*np.pi,N,endpoint=False)
    x=np.zeros((N,3)); r1=np.zeros((N,3)); r2=np.zeros((N,3))
    for n,A,B in coeff:
        ph=n*t
        x += np.cos(ph)[:,None]*A + np.sin(ph)[:,None]*B
        r1 += (-n*np.sin(ph))[:,None]*A + (n*np.cos(ph))[:,None]*B
        r2 += (-n*n*np.cos(ph))[:,None]*A + (-n*n*np.sin(ph))[:,None]*B
    speed=np.linalg.norm(r1,axis=1)
    curvature=np.linalg.norm(np.cross(r1,r2),axis=1)/(speed**3)
    L=2*np.pi*np.mean(speed)
    Ik=2*np.pi*np.mean(curvature**2*speed)
    return x,L,Ik,float(curvature.max())


def writhe_midpoint(x,skip=2,block=256):
    dx=np.roll(x,-1,axis=0)-x
    mid=(x+np.roll(x,-1,axis=0))/2
    N=len(x); total=0.0
    jj=np.arange(N)[None,:]
    for i0 in range(0,N,block):
        i1=min(N,i0+block)
        R=mid[i0:i1,None,:]-mid[None,:,:]
        C=np.cross(dx[i0:i1,None,:],dx[None,:,:])
        num=np.einsum('ijk,ijk->ij',R,C)
        den=np.linalg.norm(R,axis=2)**3
        ii=np.arange(i0,i1)[:,None]
        d=np.abs(ii-jj); d=np.minimum(d,N-d)
        den[d<=skip]=np.inf
        total += np.sum(num/den)
    return float(total/(4*np.pi))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--record',default='Supplementary_Data_S1_Gilbert_trefoil_record.xml')
    ap.add_argument('--out',default='Supplementary_Numerical_Checks_v0.2.0.json')
    args=ap.parse_args()
    coeff=load_coeffs(args.record)
    conv=[]
    for N in [1000,2000,4000,8000]:
        x,L,Ik,kmax=evaluate(coeff,N)
        conv.append({'samples':N,'writhe_midpoint_skip2':writhe_midpoint(x,2),'fourier_length':L,'I_kappa2_raw_fourier':Ik,'max_curvature_raw_fourier':kmax})
    alpha_inv=137.035999177
    LD_hr=16.3714672385; LD_g=16.371637
    result={
      'warning':'Rounded Fourier coefficients create curvature overshoot; local curvature diagnostics are not certified ideal-knot observables.',
      'writhe_orientation_note':'Sign belongs to the stored orientation and changes under mirroring or reversal.',
      'convergence':conv,
      'high_resolution_candidate':{
        'L_D':LD_hr,
        'unnormalized_candidate':8*math.pi/3*LD_hr,
        'external_residual':alpha_inv-8*math.pi/3*LD_hr,
      },
      'fourier_metadata_candidate':{
        'L_D':LD_g,
        'unnormalized_candidate':8*math.pi/3*LD_g,
        'external_residual':alpha_inv-8*math.pi/3*LD_g,
      },
      'branch_separation_ppm':(LD_g-LD_hr)/LD_hr*1e6,
    }
    Path(args.out).write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
