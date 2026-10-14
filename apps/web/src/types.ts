export type Status='queued'|'running'|'completed'|'failed';
export interface Finding{id:string;agent:string;severity:'critical'|'high'|'medium'|'low'|'info';confidence:number;title:string;explanation:string;file:string;line:number;evidence:string;status:'open'|'verified'|'dismissed'|'fixed';patch?:string}
export interface GraphNode{id:string;label:string;kind:string;path?:string}
export interface GraphEdge{id:string;source:string;target:string;kind:string}
export interface AgentState{name:string;status:Status;latency_ms:number}
export interface Verification{name:string;tool:string;passed:boolean;output:string}
export interface Run{id:string;repository_url:string;status:Status;demo_mode:boolean;created_at:string;updated_at:string;agents:AgentState[];findings:Finding[];graph:{nodes:GraphNode[];edges:GraphEdge[]};verification:Verification[];trace:{at:string;message:string;kind:string}[];metrics:{files:number;nodes:number;findings:number;latency_ms:number;tokens:number;estimated_cost_usd:number}}

