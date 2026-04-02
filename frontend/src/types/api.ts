// ============================================================
// MiroFish API Type Definitions
// ============================================================

import type { AxiosRequestConfig } from 'axios'

// ------------------------------------------------------------
// Generic / shared
// ------------------------------------------------------------

export interface ApiResponse<T = unknown> {
  success?: boolean
  error?: string
  message?: string
  data?: T
}

// Axios-like request config used by graph.ts custom calls
export type ApiRequestConfig = AxiosRequestConfig

// ------------------------------------------------------------
// Entity (Agent persona)
// ------------------------------------------------------------

export type Platform = 'reddit' | 'twitter'

export interface Entity {
  id: string
  name: string
  platform: Platform
  entity_type?: string
  description?: string
  profile?: string
  // raw fields from backend
  [key: string]: unknown
}

// ------------------------------------------------------------
// Ontology
// ------------------------------------------------------------

export interface Ontology {
  id: string
  name: string
  project_id: string
  status?: 'pending' | 'generating' | 'ready' | 'failed'
  entities?: Entity[]
  entity_types?: string[]
  metadata?: Record<string, unknown>
  [key: string]: unknown
}

// ------------------------------------------------------------
// Project
// ------------------------------------------------------------

export interface Project {
  id: string
  name: string
  description?: string
  created_at?: string
  updated_at?: string
  ontology_id?: string
  graph_id?: string
  [key: string]: unknown
}

// ------------------------------------------------------------
// Graph
// ------------------------------------------------------------

export interface Graph {
  id: string
  name: string
  project_id: string
  nodes?: GraphNode[]
  edges?: GraphEdge[]
  metadata?: Record<string, unknown>
  [key: string]: unknown
}

export interface GraphNode {
  id: string
  label: string
  type?: string
  properties?: Record<string, unknown>
  [key: string]: unknown
}

export interface GraphEdge {
  id?: string
  source: string
  target: string
  label?: string
  type?: string
  properties?: Record<string, unknown>
  [key: string]: unknown
}

// ------------------------------------------------------------
// Simulation – shared
// ------------------------------------------------------------

export type SimulationStatus =
  | 'created'
  | 'preparing'
  | 'ready'
  | 'running'
  | 'paused'
  | 'stopped'
  | 'completed'
  | 'failed'
  | 'closed'

export interface SimulationState {
  id: string
  project_id: string
  graph_id?: string
  status: SimulationStatus
  current_round?: number
  max_rounds?: number
  enable_twitter?: boolean
  enable_reddit?: boolean
  created_at?: string
  started_at?: string
  ended_at?: string
  metadata?: Record<string, unknown>
  [key: string]: unknown
}

export interface SimulationConfig {
  simulation_id: string
  entity_types?: string[]
  use_llm_for_profiles?: boolean
  parallel_profile_count?: number
  max_rounds?: number
  enable_graph_memory_update?: boolean
  platform_config?: {
    twitter?: Record<string, unknown>
    reddit?: Record<string, unknown>
  }
  [key: string]: unknown
}

// ------------------------------------------------------------
// Simulation – request payloads
// ------------------------------------------------------------

export interface CreateSimulationRequest {
  project_id: string
  graph_id?: string
  enable_twitter?: boolean
  enable_reddit?: boolean
}

export interface PrepareSimulationRequest {
  simulation_id: string
  entity_types?: string[]
  use_llm_for_profiles?: boolean
  parallel_profile_count?: number
  force_regenerate?: boolean
}

export interface PrepareStatusRequest {
  task_id?: string
  simulation_id?: string
}

export interface StartSimulationRequest {
  simulation_id: string
  platform?: Platform
  max_rounds?: number
  enable_graph_memory_update?: boolean
}

export interface StopSimulationRequest {
  simulation_id: string
}

export interface CloseEnvRequest {
  simulation_id: string
  timeout?: number
}

export interface EnvStatusRequest {
  simulation_id: string
}

export interface GetSimulationPostsParams {
  platform?: Platform
  limit?: number
  offset?: number
}

export interface GetSimulationTimelineParams {
  start_round?: number
  end_round?: number | null
}

export interface GetSimulationActionsParams {
  limit?: number
  offset?: number
  platform?: Platform
  agent_id?: string
  round_num?: number
}

export interface InterviewAgentItem {
  agent_id: string
  prompt: string
}

export interface InterviewAgentsRequest {
  simulation_id: string
  interviews: InterviewAgentItem[]
}

// ------------------------------------------------------------
// Simulation – response payloads
// ------------------------------------------------------------

export interface SimulationResponse {
  simulation_id: string
  project_id: string
  status: SimulationStatus
  [key: string]: unknown
}

export interface PrepareStatusResponse {
  task_id?: string
  simulation_id?: string
  status: 'pending' | 'running' | 'success' | 'failed'
  progress?: number
  message?: string
  [key: string]: unknown
}

export interface SimulationProfilesResponse {
  simulation_id: string
  platform: Platform
  profiles: AgentProfile[]
  total?: number
  [key: string]: unknown
}

export interface AgentProfile {
  agent_id: string
  name: string
  entity_type: string
  platform: Platform
  description?: string
  profile_text?: string
  [key: string]: unknown
}

export interface SimulationPostsResponse {
  simulation_id: string
  platform: Platform
  posts: Post[]
  total?: number
  [key: string]: unknown
}

export interface Post {
  id: string
  agent_id: string
  platform: Platform
  content: string
  timestamp?: string
  round?: number
  likes?: number
  comments?: number
  parent_id?: string
  [key: string]: unknown
}

export interface SimulationTimelineResponse {
  simulation_id: string
  rounds: TimelineRound[]
  [key: string]: unknown
}

export interface TimelineRound {
  round: number
  summary: string
  platform_stats?: {
    twitter?: PlatformRoundStats
    reddit?: PlatformRoundStats
  }
  [key: string]: unknown
}

export interface PlatformRoundStats {
  posts: number
  comments: number
  unique_agents: number
  [key: string]: unknown
}

export interface AgentStatsResponse {
  simulation_id: string
  total_agents: number
  platform_breakdown?: {
    twitter?: number
    reddit?: number
  }
  entity_type_breakdown?: Record<string, number>
  activity_stats?: Record<string, unknown>
  [key: string]: unknown
}

export interface SimulationActionsResponse {
  simulation_id: string
  actions: SimulationAction[]
  total?: number
  [key: string]: unknown
}

export interface SimulationAction {
  id: string
  agent_id: string
  platform: Platform
  action_type: string
  round_num: number
  timestamp?: string
  details?: Record<string, unknown>
  [key: string]: unknown
}

export interface SimulationHistoryItem {
  simulation_id: string
  project_id: string
  project_name?: string
  status: SimulationStatus
  created_at: string
  ended_at?: string
  [key: string]: unknown
}

export interface SimulationHistoryResponse {
  simulations: SimulationHistoryItem[]
  total?: number
  [key: string]: unknown
}

// ------------------------------------------------------------
// Run status
// ------------------------------------------------------------

export interface RunStatus {
  simulation_id: string
  status: SimulationStatus
  current_round: number
  max_rounds: number
  active_agents: number
  total_actions: number
  elapsed_seconds?: number
  [key: string]: unknown
}

export interface RunStatusDetail extends RunStatus {
  recent_actions?: SimulationAction[]
  platform_status?: {
    twitter?: Record<string, unknown>
    reddit?: Record<string, unknown>
  }
  [key: string]: unknown
}

// ------------------------------------------------------------
// Report
// ------------------------------------------------------------

export interface GenerateReportRequest {
  simulation_id: string
  force_regenerate?: boolean
}

export interface ReportStatusResponse {
  report_id: string
  simulation_id: string
  status: 'pending' | 'generating' | 'ready' | 'failed'
  progress?: number
  message?: string
  [key: string]: unknown
}

export interface AgentLogResponse {
  report_id: string
  lines: string[]
  total_lines: number
  [key: string]: unknown
}

export interface ConsoleLogResponse {
  report_id: string
  lines: string[]
  total_lines: number
  [key: string]: unknown
}

export interface Report {
  id: string
  simulation_id: string
  title?: string
  summary?: string
  content?: string
  sections?: ReportSection[]
  created_at?: string
  metadata?: Record<string, unknown>
  [key: string]: unknown
}

export interface ReportSection {
  id?: string
  title: string
  content?: string
  order?: number
  [key: string]: unknown
}

export interface ChatWithReportRequest {
  simulation_id: string
  message: string
  chat_history?: ChatMessage[]
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
}

export interface ChatWithReportResponse {
  reply: string
  [key: string]: unknown
}

// ------------------------------------------------------------
// Graph / Ontology
// ------------------------------------------------------------

export interface GenerateOntologyFormData {
  files?: File[]
  simulation_requirement?: string
  project_name?: string
  [key: string]: unknown
}

export interface BuildGraphRequest {
  project_id: string
  graph_name?: string
  [key: string]: unknown
}

export interface TaskStatusResponse {
  task_id: string
  status: 'pending' | 'running' | 'success' | 'failed'
  progress?: number
  message?: string
  result?: Record<string, unknown>
  [key: string]: unknown
}

export interface OntologyResponse {
  ontology_id: string
  project_id: string
  name: string
  entity_types?: string[]
  entities?: Entity[]
  status?: string
  [key: string]: unknown
}
