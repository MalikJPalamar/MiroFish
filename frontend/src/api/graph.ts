import service, { requestWithRetry } from './index'
import type {
  ApiResponse,
  ApiRequestConfig,
  GenerateOntologyFormData,
  BuildGraphRequest,
  TaskStatusResponse,
  OntologyResponse,
  Graph,
  Project,
} from '../types/api'

/**
 * Generate ontology (uploads documents + simulation requirement)
 */
export const generateOntology = (formData: GenerateOntologyFormData) => {
  return requestWithRetry<ApiResponse>(
    () =>
      service({
        url: '/api/graph/ontology/generate',
        method: 'post',
        data: formData,
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }) as Promise<ApiResponse>,
    3,
    1000
  )
}

/**
 * Build a knowledge graph
 */
export const buildGraph = (data: BuildGraphRequest) => {
  return requestWithRetry<ApiResponse>(
    () =>
      service({
        url: '/api/graph/build',
        method: 'post',
        data
      }) as Promise<ApiResponse>,
    3,
    1000
  )
}

/**
 * Get task status
 */
export const getTaskStatus = (taskId: string) => {
  return service.get<ApiResponse<TaskStatusResponse>>(
    `/api/graph/task/${taskId}`
  ) as Promise<ApiResponse<TaskStatusResponse>>
}

/**
 * Get graph data
 */
export const getGraphData = (graphId: string) => {
  return service.get<ApiResponse<Graph>>(
    `/api/graph/data/${graphId}`
  ) as Promise<ApiResponse<Graph>>
}

/**
 * Get project information
 */
export const getProject = (projectId: string) => {
  return service.get<ApiResponse<Project>>(
    `/api/graph/project/${projectId}`
  ) as Promise<ApiResponse<Project>>
}
