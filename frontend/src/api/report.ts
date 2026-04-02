import service, { requestWithRetry } from './index'
import type {
  ApiResponse,
  GenerateReportRequest,
  ReportStatusResponse,
  AgentLogResponse,
  ConsoleLogResponse,
  Report,
  ChatWithReportRequest,
  ChatWithReportResponse,
} from '../types/api'

/**
 * Start report generation
 */
export const generateReport = (data: GenerateReportRequest) => {
  return requestWithRetry<ApiResponse>(
    () => service.post('/api/report/generate', data),
    3,
    1000
  )
}

/**
 * Get report generation status
 */
export const getReportStatus = (reportId: string) => {
  return service.get<ApiResponse<ReportStatusResponse>>(
    `/api/report/generate/status`,
    { params: { report_id: reportId } }
  )
}

/**
 * Get agent log (incremental)
 */
export const getAgentLog = (reportId: string, fromLine = 0) => {
  return service.get<ApiResponse<AgentLogResponse>>(
    `/api/report/${reportId}/agent-log`,
    { params: { from_line: fromLine } }
  )
}

/**
 * Get console log (incremental)
 */
export const getConsoleLog = (reportId: string, fromLine = 0) => {
  return service.get<ApiResponse<ConsoleLogResponse>>(
    `/api/report/${reportId}/console-log`,
    { params: { from_line: fromLine } }
  )
}

/**
 * Get full report details
 */
export const getReport = (reportId: string) => {
  return service.get<ApiResponse<Report>>(`/api/report/${reportId}`)
}

/**
 * Chat with the Report Agent
 */
export const chatWithReport = (data: ChatWithReportRequest) => {
  return requestWithRetry<ApiResponse<ChatWithReportResponse>>(
    () => service.post('/api/report/chat', data) as Promise<ApiResponse<ChatWithReportResponse>>,
    3,
    1000
  )
}
