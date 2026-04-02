import service, { requestWithRetry } from './index'
import type {
  ApiResponse,
  CreateSimulationRequest,
  PrepareSimulationRequest,
  PrepareStatusRequest,
  SimulationState,
  SimulationProfilesResponse,
  SimulationConfig,
  SimulationPostsResponse,
  SimulationTimelineResponse,
  GetSimulationPostsParams,
  GetSimulationTimelineParams,
  GetSimulationActionsParams,
  AgentStatsResponse,
  SimulationActionsResponse,
  RunStatus,
  RunStatusDetail,
  CloseEnvRequest,
  EnvStatusRequest,
  InterviewAgentsRequest,
  SimulationHistoryResponse,
  Platform,
} from '../types/api'

/**
 * Create a new simulation
 */
export const createSimulation = (data: CreateSimulationRequest) => {
  return requestWithRetry<ApiResponse<{ simulation_id: string; project_id: string }>>(
    () => service.post('/api/simulation/create', data) as Promise<ApiResponse<{ simulation_id: string; project_id: string }>>,
    3,
    1000
  )
}

/**
 * Prepare simulation environment (async task)
 */
export const prepareSimulation = (data: PrepareSimulationRequest) => {
  return requestWithRetry<ApiResponse>(
    () => service.post('/api/simulation/prepare', data),
    3,
    1000
  )
}

/**
 * Get preparation task status
 */
export const getPrepareStatus = (data: PrepareStatusRequest) => {
  return service.post<ApiResponse>('/api/simulation/prepare/status', data)
}

/**
 * Get simulation state
 */
export const getSimulation = (simulationId: string) => {
  return service.get<ApiResponse<SimulationState>>(`/api/simulation/${simulationId}`)
}

/**
 * Get simulation agent profiles
 */
export const getSimulationProfiles = (
  simulationId: string,
  platform: Platform = 'reddit'
) => {
  return service.get<ApiResponse<SimulationProfilesResponse>>(
    `/api/simulation/${simulationId}/profiles`,
    { params: { platform } }
  )
}

/**
 * Real-time streaming profiles (returns current generated profiles)
 */
export const getSimulationProfilesRealtime = (
  simulationId: string,
  platform: Platform = 'reddit'
) => {
  return service.get<ApiResponse<SimulationProfilesResponse>>(
    `/api/simulation/${simulationId}/profiles/realtime`,
    { params: { platform } }
  )
}

/**
 * Get simulation configuration
 */
export const getSimulationConfig = (simulationId: string) => {
  return service.get<ApiResponse<SimulationConfig>>(
    `/api/simulation/${simulationId}/config`
  )
}

/**
 * Real-time streaming configuration (returns current generated config)
 */
export const getSimulationConfigRealtime = (simulationId: string) => {
  return service.get<ApiResponse>(`/api/simulation/${simulationId}/config/realtime`)
}

/**
 * List all simulations, optionally filtered by project
 */
export const listSimulations = (projectId?: string) => {
  const params = projectId ? { project_id: projectId } : {}
  return service.get<ApiResponse>('/api/simulation/list', { params })
}

/**
 * Start simulation
 */
export const startSimulation = (data: {
  simulation_id: string
  platform?: Platform
  max_rounds?: number
  enable_graph_memory_update?: boolean
}) => {
  return requestWithRetry<ApiResponse>(
    () => service.post('/api/simulation/start', data),
    3,
    1000
  )
}

/**
 * Stop simulation
 */
export const stopSimulation = (data: { simulation_id: string }) => {
  return service.post<ApiResponse>('/api/simulation/stop', data)
}

/**
 * Get real-time simulation run status
 */
export const getRunStatus = (simulationId: string) => {
  return service.get<ApiResponse<RunStatus>>(
    `/api/simulation/${simulationId}/run-status`
  )
}

/**
 * Get detailed run status (includes recent actions)
 */
export const getRunStatusDetail = (simulationId: string) => {
  return service.get<ApiResponse<RunStatusDetail>>(
    `/api/simulation/${simulationId}/run-status/detail`
  )
}

/**
 * Get simulation posts
 */
export const getSimulationPosts = (
  simulationId: string,
  platform: Platform = 'reddit',
  limit = 50,
  offset = 0
) => {
  return service.get<ApiResponse<SimulationPostsResponse>>(
    `/api/simulation/${simulationId}/posts`,
    { params: { platform, limit, offset } }
  )
}

/**
 * Get simulation timeline (summary by round)
 */
export const getSimulationTimeline = (
  simulationId: string,
  startRound = 0,
  endRound: number | null = null
) => {
  const params: Record<string, unknown> = { start_round: startRound }
  if (endRound !== null) {
    params.end_round = endRound
  }
  return service.get<ApiResponse<SimulationTimelineResponse>>(
    `/api/simulation/${simulationId}/timeline`,
    { params }
  )
}

/**
 * Get agent statistics
 */
export const getAgentStats = (simulationId: string) => {
  return service.get<ApiResponse<AgentStatsResponse>>(
    `/api/simulation/${simulationId}/agent-stats`
  )
}

/**
 * Get simulation action history
 */
export const getSimulationActions = (
  simulationId: string,
  params: GetSimulationActionsParams = {}
) => {
  return service.get<ApiResponse<SimulationActionsResponse>>(
    `/api/simulation/${simulationId}/actions`,
    { params }
  )
}

/**
 * Gracefully close simulation environment
 */
export const closeSimulationEnv = (data: CloseEnvRequest) => {
  return service.post<ApiResponse>('/api/simulation/close-env', data)
}

/**
 * Get simulation environment status
 */
export const getEnvStatus = (data: EnvStatusRequest) => {
  return service.post<ApiResponse>('/api/simulation/env-status', data)
}

/**
 * Batch interview agents
 */
export const interviewAgents = (data: InterviewAgentsRequest) => {
  return requestWithRetry<ApiResponse>(
    () => service.post('/api/simulation/interview/batch', data),
    3,
    1000
  )
}

/**
 * Get historical simulation list (with project details)
 * Used for homepage history display
 */
export const getSimulationHistory = (limit = 20) => {
  return service.get<ApiResponse<SimulationHistoryResponse>>(
    '/api/simulation/history',
    { params: { limit } }
  )
}
