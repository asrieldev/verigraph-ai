import type {Run} from './types';
const BASE=import.meta.env.VITE_API_URL||'http://localhost:8000';
async function request<T>(path:string,init?:RequestInit):Promise<T>{const r=await fetch(`${BASE}${path}`,{...init,headers:{'Content-Type':'application/json',...(init?.headers||{})}});if(!r.ok)throw new Error((await r.json().catch(()=>({detail:r.statusText}))).detail);return r.json() as Promise<T>}
export const api={createRun:(repository_url:string)=>request<Run>('/api/runs',{method:'POST',body:JSON.stringify({repository_url})}),getRun:(id:string)=>request<Run>(`/api/runs/${id}`),listRuns:()=>request<Run[]>('/api/runs'),applyPatch:(run:string,finding:string)=>request<Run>(`/api/runs/${run}/findings/${finding}/approve`,{method:'POST'}),report:(id:string)=>`${BASE}/api/runs/${id}/report`};

